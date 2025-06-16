from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from law_classifier.rules import RuleEngine


def test_budget_category():
    engine = RuleEngine(Path("data/terms.yaml"))
    text = "Державний бюджет наукових досліджень"
    code, terms = engine.match(text)
    assert code == "BUD"
    assert terms


def test_unlabelled():
    engine = RuleEngine(Path("data/terms.yaml"))
    text = "Це простий текст без згадок"
    code, terms = engine.match(text)
    assert code == "UNLABELLED"
    assert not terms
