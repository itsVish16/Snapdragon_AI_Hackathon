from snapflow.core.refiner import EdgeRefiner


def test_refiner_disabled():
    refiner = EdgeRefiner(is_enabled=False)
    raw = "umm hello world like you know"
    res = refiner.refine(raw)
    assert res["refined"] == raw
    assert res["style"] == "raw"


def test_clean_verbatim():
    refiner = EdgeRefiner(is_enabled=True)
    raw = "umm so basically I want to spend twenty dollars on this like definitely"
    res = refiner.refine(raw, style="clean_verbatim")

    assert "umm" not in res["refined"].lower()
    assert "like" not in res["refined"].lower()
    assert "$20" in res["refined"]
    assert res["refined"].endswith(".")


def test_executive_email():
    refiner = EdgeRefiner(is_enabled=True)
    raw = "we need to finalize the snapdragon hackathon submission today"
    res = refiner.refine(raw, style="executive_email")

    assert "Subject:" in res["refined"]
    assert "Hi Team," in res["refined"]
    assert "Best regards," in res["refined"]


def test_action_items():
    refiner = EdgeRefiner(is_enabled=True)
    raw = "benchmark whisper latency on hexagon npu; verify qnn execution provider; record demo video"
    res = refiner.refine(raw, style="action_items")

    assert "### Action Items & Decisions:" in res["refined"]
    assert "- [ ]" in res["refined"]


def test_code_docstring():
    refiner = EdgeRefiner(is_enabled=True)
    raw = "transcribe incoming audio stream and return json payload"
    res = refiner.refine(raw, style="code_docstring")

    assert '"""' in res["refined"]
    assert "Parameters:" in res["refined"]
    assert "Returns:" in res["refined"]
