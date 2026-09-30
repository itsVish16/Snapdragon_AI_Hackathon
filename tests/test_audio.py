import numpy as np
import pytest
from snapflow.core.audio import AudioRingBuffer, AudioStreamer


def test_ring_buffer_write_and_read():
    sample_rate = 16000
    rb = AudioRingBuffer(capacity_seconds=5.0, sample_rate=sample_rate)

    samples = np.ones(16000, dtype=np.float32) * 0.5
    rb.write(samples)

    chunk = rb.get_last_n_seconds(1.0)
    assert len(chunk) == 16000
    assert np.allclose(chunk, 0.5)


def test_ring_buffer_overflow_wrap():
    sample_rate = 16000
    rb = AudioRingBuffer(capacity_seconds=1.0, sample_rate=sample_rate)

    first_chunk = np.ones(16000, dtype=np.float32) * 0.2
    second_chunk = np.ones(16000, dtype=np.float32) * 0.8

    rb.write(first_chunk)
    rb.write(second_chunk)

    chunk = rb.get_last_n_seconds(1.0)
    assert len(chunk) == 16000
    assert np.allclose(chunk, 0.8)


def test_audio_rms_calculation():
    streamer = AudioStreamer()

    silent_audio = np.zeros(16000, dtype=np.float32)
    assert streamer.calculate_rms(silent_audio) == 0.0

    loud_audio = np.ones(16000, dtype=np.float32) * 0.5
    assert pytest.approx(streamer.calculate_rms(loud_audio), 0.01) == 0.5


def test_mock_speech_generation():
    speech = AudioStreamer.generate_mock_speech(duration=1.5, sample_rate=16000)
    assert len(speech) == int(1.5 * 16000)
    assert np.max(np.abs(speech)) > 0.05
