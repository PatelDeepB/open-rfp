"""Unit tests for Knowledge Retriever and Semantic Search."""

from openrfp.core.retriever import KnowledgeRetriever
from openrfp.models import KnowledgeItem, RequirementCategory


def test_should_retrieve_high_scoring_match_for_exact_terms(seeded_retriever):
    """Verify retriever surfaces exact matches with high confidence."""
    # Arrange
    query = "Vendor must hold active SOC 2 Type II certification"

    # Act
    results = seeded_retriever.search(query, category=RequirementCategory.SECURITY_COMPLIANCE)

    # Assert
    assert len(results) > 0
    top_match = results[0]
    assert top_match.item.id == "KB-SEC-001"
    assert top_match.similarity_score >= 0.70
    assert "soc" in top_match.matched_terms or "certification" in top_match.matched_terms


def test_should_return_empty_list_when_retriever_is_empty():
    """Verify empty retriever gracefully returns an empty result list."""
    # Arrange
    retriever = KnowledgeRetriever()

    # Act
    results = retriever.search("Any random query string")

    # Assert
    assert results == []


def test_should_apply_category_boosting_correctly():
    """Verify items in matching category receive relevance score boost."""
    # Arrange
    item_sec = KnowledgeItem(
        id="SEC-1",
        title="Encryption Policy",
        category=RequirementCategory.SECURITY_COMPLIANCE,
        content="We support AES-256 encryption at rest.",
    )
    item_other = KnowledgeItem(
        id="OTH-1",
        title="General Feature",
        category=RequirementCategory.FUNCTIONAL_SPEC,
        content="We support AES-256 encryption at rest.",
    )
    retriever = KnowledgeRetriever(items=[item_sec, item_other])

    # Act
    results = retriever.search("AES-256 encryption", category=RequirementCategory.SECURITY_COMPLIANCE)

    # Assert
    assert len(results) == 2
    assert results[0].item.id == "SEC-1"
    assert results[0].similarity_score > results[1].similarity_score


def test_should_respect_top_k_parameter(seeded_retriever):
    """Verify retriever caps returned results to top_k limit."""
    # Arrange
    top_k = 2

    # Act
    results = seeded_retriever.search("security compliance cloud", top_k=top_k)

    # Assert
    assert len(results) <= top_k


def test_should_retrieve_item_by_id_properly(seeded_retriever):
    """Verify direct lookup by ID works as expected."""
    # Act
    item = seeded_retriever.get_item_by_id("KB-SEC-001")

    # Assert
    assert item is not None
    assert item.title == "SOC 2 Type II Certification"
