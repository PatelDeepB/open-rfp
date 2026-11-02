"""Unit tests for RFP Parser and Document Shredder."""

import pytest
from openrfp.core.parser import RfpParser
from openrfp.exceptions import DocumentNotFoundError, ParseError
from openrfp.models import PriorityLevel, RequirementCategory


def test_should_parse_markdown_into_sections_and_requirements():
    """Verify parser extracts structured requirements from sectioned markdown."""
    # Arrange
    parser = RfpParser()
    raw_markdown = """# Section 1: Security Requirements
* REQ-001: Vendor must provide SOC 2 Type II audit report.
* REQ-002: System must encrypt data at rest using AES-256.

# Section 2: Integrations
* REQ-003: Must provide REST APIs and webhooks.
"""

    # Act
    rfp = parser.parse_text(raw_markdown, title="Security RFP", buyer_name="TestBank")

    # Assert
    assert len(rfp.requirements) == 3
    assert rfp.requirements[0].id == "REQ-001"
    assert rfp.requirements[0].category == RequirementCategory.SECURITY_COMPLIANCE
    assert rfp.requirements[0].priority == PriorityLevel.MANDATORY


def test_should_raise_parse_error_when_text_is_empty():
    """Verify empty text triggers a typed ParseError."""
    # Arrange
    parser = RfpParser()

    # Act & Assert
    with pytest.raises(ParseError, match="empty RFP text"):
        parser.parse_text("   ", title="Empty RFP")


def test_should_raise_document_not_found_when_file_missing(tmp_path):
    """Verify non-existent file triggers DocumentNotFoundError."""
    # Arrange
    parser = RfpParser()
    non_existent = tmp_path / "does_not_exist.md"

    # Act & Assert
    with pytest.raises(DocumentNotFoundError):
        parser.parse_file(non_existent)


def test_should_classify_categories_accurately():
    """Verify category classification matches domain keywords."""
    # Arrange
    parser = RfpParser()
    sample = """# Section: General
- Must support 99.99% monthly SLA and disaster recovery.
- Must provide pricing rate card and volume discounts.
"""

    # Act
    rfp = parser.parse_text(sample)

    # Assert
    categories = [req.category for req in rfp.requirements]
    assert RequirementCategory.SLA_SUPPORT in categories
    assert RequirementCategory.PRICING in categories


def test_should_classify_mandatory_priority_when_modal_word_used():
    """Verify mandatory vs optional priority detection."""
    # Arrange
    parser = RfpParser()
    sample = """# Requirements
- System must enforce strict multi-factor authentication.
- A dark mode theme is nice to have and optional.
"""

    # Act
    rfp = parser.parse_text(sample)

    # Assert
    assert rfp.requirements[0].priority == PriorityLevel.MANDATORY
    assert rfp.requirements[1].priority == PriorityLevel.OPTIONAL


def test_should_extract_technical_tags_accurately():
    """Verify parser extracts relevant tags from requirement text."""
    # Arrange
    parser = RfpParser()
    sample = "# Tech\n- Must support AWS deployment, REST APIs, and SOC 2 compliance."

    # Act
    rfp = parser.parse_text(sample)

    # Assert
    tags = rfp.requirements[0].tags
    assert "AWS" in tags
    assert "REST" in tags
    assert "SOC 2" in tags


def test_should_parse_docx_file(tmp_path):
    """Verify parser extracts requirements from DOCX files."""
    # Arrange
    import docx
    doc = docx.Document()
    doc.add_heading("Architecture Requirements", level=1)
    doc.add_paragraph("Vendor must provide 99.99% uptime SLA.")
    docx_path = tmp_path / "tender.docx"
    doc.save(str(docx_path))

    # Act
    parser = RfpParser()
    rfp = parser.parse_file(docx_path, buyer_name="BankCorp")

    # Assert
    assert len(rfp.requirements) >= 1
    assert "99.99%" in rfp.requirements[0].requirement_text


def test_should_parse_csv_file(tmp_path):
    """Verify parser extracts requirements from CSV matrix sheets."""
    # Arrange
    csv_path = tmp_path / "compliance.csv"
    csv_path.write_text("ID,Requirement\nREQ-1,Must support SAML 2.0 SSO\nREQ-2,Must encrypt with AES-256")

    # Act
    parser = RfpParser()
    rfp = parser.parse_file(csv_path, buyer_name="GovAgency")

    # Assert
    assert len(rfp.requirements) >= 1

