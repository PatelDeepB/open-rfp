"""Shared test fixtures for OpenRFP test suite."""

import shutil
import tempfile
from pathlib import Path
import pytest
from openrfp.core.retriever import KnowledgeRetriever
from openrfp.core.seed import get_sample_enterprise_knowledge
from openrfp.models import (
    ComplianceRequirement,
    PriorityLevel,
    RequirementCategory,
    RfpDocument,
)
from openrfp.storage import StorageService


@pytest.fixture
def temp_storage_dir():
    """Provide a temporary directory for isolated storage tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def storage_service(temp_storage_dir):
    """Provide a clean StorageService pointed to temporary storage."""
    return StorageService(base_dir=temp_storage_dir)


@pytest.fixture
def sample_knowledge_items():
    """Provide standard sample enterprise knowledge items."""
    return get_sample_enterprise_knowledge()


@pytest.fixture
def seeded_retriever(sample_knowledge_items):
    """Provide a KnowledgeRetriever pre-seeded with sample enterprise truth."""
    return KnowledgeRetriever(items=sample_knowledge_items)


@pytest.fixture
def sample_rfp_document():
    """Provide a pre-parsed sample RfpDocument."""
    requirements = [
        ComplianceRequirement(
            id="REQ-001",
            section_title="Security",
            requirement_text="Vendor must hold active SOC 2 Type II certification.",
            category=RequirementCategory.SECURITY_COMPLIANCE,
            priority=PriorityLevel.MANDATORY,
        ),
        ComplianceRequirement(
            id="REQ-002",
            section_title="Technical Architecture",
            requirement_text="Platform must run in high-availability multi-tenant cloud architecture.",
            category=RequirementCategory.TECHNICAL_ARCHITECTURE,
            priority=PriorityLevel.HIGH,
        ),
        ComplianceRequirement(
            id="REQ-003",
            section_title="Edge Case",
            requirement_text="Must provide quantum-encrypted teleportation hardware.",
            category=RequirementCategory.FUNCTIONAL_SPEC,
            priority=PriorityLevel.OPTIONAL,
        ),
    ]
    return RfpDocument(
        id="test-rfp-001",
        title="FinTech Security Solicitation",
        buyer_name="FinTech Corp",
        raw_text="Raw text payload",
        requirements=requirements,
    )
