"""Unit tests for Proposal Drafter and Synthesis Engine."""

from openrfp.core.drafter import ProposalDrafter
from openrfp.models import ConfidenceLevel, Department


def test_should_synthesize_green_draft_when_strong_match_found(seeded_retriever, sample_rfp_document):
    """Verify strong knowledge base match yields a Green confidence answer."""
    # Arrange
    drafter = ProposalDrafter(retriever=seeded_retriever)

    # Act
    proposal = drafter.draft_proposal(sample_rfp_document)

    # Assert
    soc2_draft = next(d for d in proposal.drafts if d.requirement_id == "REQ-001")
    assert soc2_draft.confidence == ConfidenceLevel.GREEN
    assert "SOC 2 Type II" in soc2_draft.answer_text
    assert len(soc2_draft.cited_sources) > 0
    assert soc2_draft.target_department == Department.SECURITY_INFOSEC


def test_should_flag_red_draft_when_no_knowledge_matches(seeded_retriever, sample_rfp_document):
    """Verify missing capabilities are marked Red with gap routing."""
    # Arrange
    drafter = ProposalDrafter(retriever=seeded_retriever)

    # Act
    proposal = drafter.draft_proposal(sample_rfp_document)

    # Assert
    gap_draft = next(d for d in proposal.drafts if d.requirement_id == "REQ-003")
    assert gap_draft.confidence == ConfidenceLevel.RED
    assert "Pending SME Review" in gap_draft.answer_text
    assert len(gap_draft.identified_assumptions) > 0


def test_should_compute_valid_win_probability_and_executive_summary(seeded_retriever, sample_rfp_document):
    """Verify proposal summary includes executive summary and realistic score."""
    # Arrange
    drafter = ProposalDrafter(retriever=seeded_retriever)

    # Act
    proposal = drafter.draft_proposal(sample_rfp_document)

    # Assert
    assert 0.0 < proposal.win_probability_score <= 100.0
    assert sample_rfp_document.buyer_name in proposal.executive_summary
    assert "compliance coverage" in proposal.executive_summary
