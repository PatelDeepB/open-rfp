"""Unit tests for LlmClient provider and heuristic fallbacks."""

from openrfp.core.llm import LlmClient


def test_should_fallback_to_grounded_when_facts_provided():
    """Verify LlmClient falls back to grounded template when facts are available."""
    # Arrange
    client = LlmClient()
    facts = ["Platform is audited annually for SOC 2 Type II."]

    # Act
    answer, assumptions = client.synthesize_response(
        requirement_text="Must have SOC 2 certification",
        buyer_name="Enterprise Corp",
        verified_facts=facts,
    )

    # Assert
    assert "Enterprise Corp" in answer
    assert "SOC 2 Type II" in answer
    assert assumptions == []


def test_should_fallback_to_unmatched_when_facts_empty():
    """Verify LlmClient flags SME review when facts are absent."""
    # Arrange
    client = LlmClient()

    # Act
    answer, assumptions = client.synthesize_response(
        requirement_text="Must support quantum teleportation",
        buyer_name="Enterprise Corp",
        verified_facts=[],
    )

    # Assert
    assert "Pending Subject Matter Expert review" in answer
    assert len(assumptions) > 0
