"""Unit tests for Gap Analyzer and SME Routing."""

from openrfp.core.gap_analyzer import GapAnalyzer
from openrfp.models import (
    ComplianceRequirement,
    ConfidenceLevel,
    Department,
    DraftAnswer,
    PriorityLevel,
    RequirementCategory,
)


def test_should_calculate_completeness_and_counts_accurately():
    """Verify gap analyzer computes correct percentages and categorizes counts."""
    # Arrange
    analyzer = GapAnalyzer()
    requirements = [
        ComplianceRequirement(
            id="REQ-1",
            section_title="Sec",
            requirement_text="Requirement one",
            category=RequirementCategory.SECURITY_COMPLIANCE,
            priority=PriorityLevel.MANDATORY,
        ),
        ComplianceRequirement(
            id="REQ-2",
            section_title="Arch",
            requirement_text="Requirement two",
            category=RequirementCategory.TECHNICAL_ARCHITECTURE,
            priority=PriorityLevel.HIGH,
        ),
    ]
    drafts = [
        DraftAnswer(
            requirement_id="REQ-1",
            answer_text="Verified response",
            confidence=ConfidenceLevel.GREEN,
            confidence_score=0.90,
            target_department=Department.SECURITY_INFOSEC,
        ),
        DraftAnswer(
            requirement_id="REQ-2",
            answer_text="Gap response",
            confidence=ConfidenceLevel.RED,
            confidence_score=0.20,
            target_department=Department.ENGINEERING_ARCH,
        ),
    ]

    # Act
    report = analyzer.analyze_gaps("rfp-123", requirements, drafts)

    # Assert
    assert report.total_requirements == 2
    assert report.green_count == 1
    assert report.amber_count == 0
    assert report.red_count == 1
    assert report.completeness_percentage == 50.0
    assert len(report.tasks) == 1
    assert report.tasks[0].department == Department.ENGINEERING_ARCH
    assert "CRITICAL GAP" in report.tasks[0].question


def test_should_handle_empty_requirements_list():
    """Verify analyzer gracefully handles empty requirement sets."""
    # Arrange
    analyzer = GapAnalyzer()

    # Act
    report = analyzer.analyze_gaps("empty-rfp", [], [])

    # Assert
    assert report.total_requirements == 0
    assert report.completeness_percentage == 100.0
    assert report.tasks == []
