from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAD_SURFACES = [
    ROOT / "README.md",
    ROOT / "docs" / "CASE_STUDY.md",
    ROOT / "docs" / "RETRO.md",
    ROOT / "docs" / "STATUS.md",
    ROOT / "web" / "app" / "page.tsx",
    ROOT / "web" / "app" / "plan" / "page.tsx",
]


def test_lead_surfaces_drop_unqualified_legacy_claims_and_brand():
    public_copy = "\n".join(path.read_text(encoding="utf-8") for path in LEAD_SURFACES)

    for stale_phrase in ("After Midnight", "108%", "95%", "High confidence"):
        assert stale_phrase not in public_copy


def test_readme_states_the_synthetic_evidence_boundary():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "synthetic-household" in readme
    assert "not measured customer outcomes" in readme
    assert "feature-freeze release" in readme
