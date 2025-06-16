from law_classifier.cli import get_engine


def test_budget_category():
    engine = get_engine()
    text = "Державний бюджет наукових досліджень"
    code, terms = engine.match(text)
    assert code == "BUD"
    assert terms


def test_unlabelled():
    engine = get_engine()
    text = "Це простий текст без згадок"
    code, terms = engine.match(text)
    assert code == "UNLABELLED"
    assert not terms
