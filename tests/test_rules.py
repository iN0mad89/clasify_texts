from pathlib import Path

def test_budget_category():
    from law_classifier.rules import RuleEngine

    engine = RuleEngine(Path("data/terms.yaml"))
    text = "Державний бюджет наукових досліджень"
    code, terms = engine.match(text)
    assert code == "BUD"
    assert terms


def test_unlabelled():
    from law_classifier.rules import RuleEngine

    engine = RuleEngine(Path("data/terms.yaml"))
    text = "Це простий текст без згадок"
    code, terms = engine.match(text)
    assert code == "UNLABELLED"
    assert not terms
