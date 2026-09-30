from snapflow.core.injector import TextInjector


def test_injector_clipboard_copy():
    injector = TextInjector()
    text = "SnapFlow AI Unit Test String"
    copied = injector.copy_to_clipboard(text)
    assert copied is True


def test_injector_empty_text():
    injector = TextInjector()
    assert injector.copy_to_clipboard("") is False
    assert injector.type_text("") is False
