import time
import threading
from typing import Callable, Generator, Optional
import numpy as np

try:
    import sounddevice as sd
except ImportError:
    sd = None


class AudioRingBuffer:
    def __init__(self, capacity_seconds: float = 30.0, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.capacity = int(capacity_seconds * sample_rate)
        self.buffer = np.zeros(self.capacity, dtype=np.float32)
        self.write_idx = 0
        self.total_written = 0
        self.lock = threading.Lock()

    def write(self, samples: np.ndarray):
        with self.lock:
            samples = samples.flatten().astype(np.float32)
            n = len(samples)
            if n == 0:
                return
            if n >= self.capacity:
                self.buffer[:] = samples[-self.capacity:]
                self.write_idx = 0
            else:
                end_idx = self.write_idx + n
                if end_idx <= self.capacity:
                    self.buffer[self.write_idx:end_idx] = samples
                else:
                    first_part = self.capacity - self.write_idx
                    second_part = n - first_part
                    self.buffer[self.write_idx:] = samples[:first_part]
                    self.buffer[:second_part] = samples[first_part:]
                self.write_idx = end_idx % self.capacity
            self.total_written += n

    def get_last_n_seconds(self, seconds: float) -> np.ndarray:
        with self.lock:
            n = min(int(seconds * self.sample_rate), min(self.total_written, self.capacity))
            if n == 0:
                return np.zeros(0, dtype=np.float32)
            start_idx = (self.write_idx - n) % self.capacity
            if start_idx + n <= self.capacity:
                return self.buffer[start_idx:start_idx + n].copy()
            first_part = self.capacity - start_idx
            second_part = n - first_part
            return np.concatenate((self.buffer[start_idx:], self.buffer[:second_part])).copy()

    def clear(self):
        with self.lock:
            self.buffer.fill(0)
            self.write_idx = 0
            self.total_written = 0


class AudioStreamer:
    def __init__(
        self,
        sample_rate: int = 16000,
        chunk_duration: float = 1.5,
        energy_threshold: float = 0.015,
        silence_timeout: float = 0.45,
    ):
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.energy_threshold = energy_threshold
        self.silence_timeout = silence_timeout

        self.ring_buffer = AudioRingBuffer(capacity_seconds=30.0, sample_rate=sample_rate)
        self.is_recording = False
        self.stream = None
        self._thread = None
        self.last_speech_time = 0.0
        self.is_speech_active = False

    def calculate_rms(self, audio: np.ndarray) -> float:
        if len(audio) == 0:
            return 0.0
        return float(np.sqrt(np.mean(np.square(audio))))

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            pass
        audio_chunk = indata[:, 0].copy()
        self.ring_buffer.write(audio_chunk)

        rms = self.calculate_rms(audio_chunk)
        now = time.time()
        if rms >= self.energy_threshold:
            self.last_speech_time = now
            self.is_speech_active = True
        elif self.is_speech_active and (now - self.last_speech_time > self.silence_timeout):
            self.is_speech_active = False

    def start(self, device: Optional[int] = None) -> bool:
        if self.is_recording:
            return True
        if sd is None:
            return False
        try:
            self.is_recording = True
            blocksize = int(self.sample_rate * 0.05)
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                blocksize=blocksize,
                device=device,
                callback=self._audio_callback,
            )
            self.stream.start()
            return True
        except Exception:
            self.is_recording = False
            return False

    def stop(self):
        self.is_recording = False
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

    def get_latest_chunk(self, duration: Optional[float] = None) -> np.ndarray:
        dur = duration if duration is not None else self.chunk_duration
        return self.ring_buffer.get_last_n_seconds(dur)

    def write_external_chunk(self, samples: np.ndarray):
        self.ring_buffer.write(samples)
        rms = self.calculate_rms(samples)
        now = time.time()
        if rms >= self.energy_threshold:
            self.last_speech_time = now
            self.is_speech_active = True
        elif self.is_speech_active and (now - self.last_speech_time > self.silence_timeout):
            self.is_speech_active = False

    @staticmethod
    def generate_mock_speech(duration: float = 2.0, sample_rate: int = 16000) -> np.ndarray:
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        signal = (
            0.3 * np.sin(2 * np.pi * 220 * t)
            + 0.2 * np.sin(2 * np.pi * 440 * t)
            + 0.1 * np.sin(2 * np.pi * 880 * t)
        )
        envelope = np.hanning(len(signal))
        noise = 0.01 * np.random.normal(0, 1, len(signal))
        return ((signal * envelope) + noise).astype(np.float32)
