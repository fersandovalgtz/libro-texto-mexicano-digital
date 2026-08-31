import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "analyze_indigenous_languages.py"
SPEC = importlib.util.spec_from_file_location("analyze_indigenous_languages", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def test_direct_phrase_is_explicit():
    result = mod.analyze_text("En México se hablan muchas lenguas indígenas.")
    assert result["explicit_general"]
    assert result["broad_candidate"]


def test_maya_civilization_without_context_is_rejected():
    result = mod.analyze_text("La civilización maya construyó grandes ciudades y templos.")
    assert not result["named_language_contextual"]
    assert not result["broad_candidate"]


def test_named_language_with_context_is_accepted():
    result = mod.analyze_text("En esta comunidad muchas familias hablan rarámuri y conservan su lengua.")
    assert result["named_language_contextual"]
    assert "Tarahumara / rarámuri" in result["language_hits"]


def test_concept_requires_indigenous_anchor():
    assert not mod.analyze_text("La diversidad lingüística del español es amplia.")["explicit_general"]
    assert mod.analyze_text(
        "La diversidad lingüística de los pueblos indígenas forma parte del patrimonio."
    )["explicit_general"]


def test_diacritics_fold_deterministically():
    result = mod.analyze_text("La lengua náhuatl tiene numerosos hablantes.")
    assert "Náhuatl" in result["language_hits"]


def test_context_window_rejects_far_cooccurrence():
    text = "maya " + " ".join(["territorio"] * 40) + " lengua"
    assert not mod.analyze_text(text)["named_language_contextual"]
