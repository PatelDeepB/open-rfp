"""Unit tests for Proposal Exporter."""

import json
from openrfp.core.drafter import ProposalDrafter
from openrfp.core.exporter import ProposalExporter


def test_should_export_valid_markdown_proposal(seeded_retriever, sample_rfp_document):
    """Verify markdown output contains executive summary and compliance matrix."""
    # Arrange
    drafter = ProposalDrafter(retriever=seeded_retriever)
    exporter = ProposalExporter()
    proposal = drafter.draft_proposal(sample_rfp_document)

    # Act
    markdown = exporter.to_markdown(proposal, sample_rfp_document)

    # Assert
    assert "# Commercial & Technical Proposal Response" in markdown
    assert sample_rfp_document.buyer_name in markdown
    assert "REQ-001" in markdown
    assert "Executive Summary" in markdown


def test_should_export_csv_compliance_matrix(seeded_retriever, sample_rfp_document):
    """Verify CSV contains header row and requirement entries."""
    # Arrange
    drafter = ProposalDrafter(retriever=seeded_retriever)
    exporter = ProposalExporter()
    proposal = drafter.draft_proposal(sample_rfp_document)

    # Act
    csv_text = exporter.to_csv(proposal, sample_rfp_document)

    # Assert
    lines = csv_text.strip().splitlines()
    assert "Requirement ID,Section,Requirement Text" in lines[0]
    assert len(lines) == len(sample_rfp_document.requirements) + 1


def test_should_export_html_report(seeded_retriever, sample_rfp_document):
    """Verify HTML export includes proper markup and styling."""
    # Arrange
    drafter = ProposalDrafter(retriever=seeded_retriever)
    exporter = ProposalExporter()
    proposal = drafter.draft_proposal(sample_rfp_document)

    # Act
    html = exporter.to_html(proposal, sample_rfp_document)

    # Assert
    assert "<!DOCTYPE html>" in html
    assert f"Proposal for {sample_rfp_document.buyer_name}" in html
    assert "REQ-001" in html


def test_should_export_json_and_save_all(seeded_retriever, sample_rfp_document, tmp_path):
    """Verify save_all writes all format files to destination directory."""
    # Arrange
    drafter = ProposalDrafter(retriever=seeded_retriever)
    exporter = ProposalExporter()
    proposal = drafter.draft_proposal(sample_rfp_document)

    # Act
    files = exporter.save_all(proposal, sample_rfp_document, output_dir=tmp_path)

    # Assert
    assert files["markdown"].exists()
    assert files["csv"].exists()
    assert files["html"].exists()
    assert files["json"].exists()

    loaded_json = json.loads(files["json"].read_text(encoding="utf-8"))
    assert loaded_json["rfp_id"] == sample_rfp_document.id
