from __future__ import annotations

from community_energy_flex.data_sources.tariffs import FlatTariff
from community_energy_flex.demo import sample_carbon_curve, sample_tasks
from community_energy_flex.domain.models import Objective
from community_energy_flex.optimisation.planning import build_planning_slots
from community_energy_flex.optimisation.rule_based import optimise
from community_energy_flex.reporting.excel_report import build_workbook, write_workbook_bytes
from community_energy_flex.reporting.pdf_report import write_pdf_bytes
from community_energy_flex.reporting.summary import build_action_summary, format_text_report


def _summary():
    slots = build_planning_slots(sample_carbon_curve(), FlatTariff(unit_rate_p=28.0))
    schedule = optimise(sample_tasks(), slots, Objective.BALANCED)
    return build_action_summary(schedule)


def test_summary_has_one_line_per_task():
    summary = _summary()
    assert len(summary.lines) == 3
    assert all("-" in line.recommended_window for line in summary.lines)


def test_totals_convert_units():
    summary = _summary()
    assert summary.total_cost_saving_pounds == summary.total_cost_saving_p / 100.0
    assert summary.total_carbon_saving_kg == summary.total_carbon_saving_g / 1000.0


def test_text_report_mentions_safety_and_robustness():
    text = format_text_report(_summary())
    assert "planning recommendations only" in text
    assert "robustness" in text.lower()


def test_excel_report_has_brand_and_robustness_column():
    workbook = build_workbook(_summary())

    assert workbook["Executive Summary"]["A1"].value == "Community Energy Flex - Action Report"
    assert workbook["Tomorrow Schedule"]["F1"].value == "Robustness indicator"
    assert write_workbook_bytes(_summary()).startswith(b"PK")


def test_pdf_report_is_serialised():
    report = write_pdf_bytes(_summary())

    assert report.startswith(b"%PDF")
    assert len(report) > 1_000
