import numpy as np
from snapflow.core.whisper_engine import SnapWhisperEngine
from snapflow.core.audio import AudioStreamer


def test_whisper_engine_initialization():
    engine = SnapWhisperEngine()
    assert engine.provider_display_name is not None
    assert engine.active_provider is not None


def test_whisper_engine_empty_chunk():
    engine = SnapWhisperEngine()
    empty = np.zeros(0, dtype=np.float32)
    res = engine.transcribe_chunk(empty)
    assert res["text"] == ""
    assert res["latency_ms"] == 0.0


def test_whisper_engine_transcribe_mock():
    engine = SnapWhisperEngine()
    mock_audio = AudioStreamer.generate_mock_speech(duration=1.0)
    res = engine.transcribe_chunk(mock_audio)

    assert "text" in res
    assert "latency_ms" in res
    assert "rtf" in res
    assert "provider" in res
    assert res["latency_ms"] > 0
    assert res["rtf"] >= 0
