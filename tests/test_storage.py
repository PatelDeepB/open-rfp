"""Unit tests for StorageService persistence layer."""

import pytest
from openrfp.exceptions import DocumentNotFoundError
from openrfp.models import (
    GapReport,
    KnowledgeItem,
    ProposalSummary,
    RequirementCategory,
    RfpDocument,
)
from openrfp.storage import StorageService


def test_should_save_and_retrieve_rfp(storage_service, sample_rfp_document):
    """Verify storing and retrieving RFP document by ID."""
    # Act
    storage_service.save_rfp(sample_rfp_document)
    retrieved = storage_service.get_rfp(sample_rfp_document.id)

    # Assert
    assert retrieved.id == sample_rfp_document.id
    assert retrieved.buyer_name == sample_rfp_document.buyer_name
    assert len(retrieved.requirements) == len(sample_rfp_document.requirements)


def test_should_raise_document_not_found_when_rfp_missing(storage_service):
    """Verify looking up non-existent RFP raises DocumentNotFoundError."""
    # Act & Assert
    with pytest.raises(DocumentNotFoundError):
        storage_service.get_rfp("unknown-rfp-id")


def test_should_list_all_saved_rfps(storage_service, sample_rfp_document):
    """Verify listing returns all saved RFP records."""
    # Arrange
    storage_service.save_rfp(sample_rfp_document)

    # Act
    rfps = storage_service.list_rfps()

    # Assert
    assert len(rfps) >= 1
    assert any(r.id == sample_rfp_document.id for r in rfps)


def test_should_save_and_list_knowledge_items(storage_service):
    """Verify storing and retrieving enterprise knowledge items."""
    # Arrange
    item = KnowledgeItem(
        id="KB-CUSTOM-001",
        title="Custom SLA Policy",
        category=RequirementCategory.SLA_SUPPORT,
        content="Custom 99.95% SLA for government sector.",
    )

    # Act
    storage_service.save_knowledge_item(item)
    all_items = storage_service.get_all_knowledge_items()

    # Assert
    assert len(all_items) >= 1
    assert any(i.id == "KB-CUSTOM-001" for i in all_items)


def test_should_save_and_retrieve_proposal(storage_service, sample_rfp_document):
    """Verify storing and retrieving proposal summaries."""
    # Arrange
    proposal = ProposalSummary(
        rfp_id=sample_rfp_document.id,
        title=sample_rfp_document.title,
        buyer_name=sample_rfp_document.buyer_name,
        executive_summary="Sample executive proposal narrative.",
        win_probability_score=85.5,
        gap_report=GapReport(
            rfp_id=sample_rfp_document.id,
            total_requirements=3,
            green_count=2,
            amber_count=1,
            red_count=0,
            completeness_percentage=86.7,
        ),
    )

    # Act
    storage_service.save_proposal(proposal)
    retrieved = storage_service.get_proposal(sample_rfp_document.id)

    # Assert
    assert retrieved.rfp_id == sample_rfp_document.id
    assert retrieved.win_probability_score == 85.5
