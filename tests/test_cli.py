"""Unit tests for OpenRFP Typer CLI."""

from typer.testing import CliRunner
from openrfp.cli import app

runner = CliRunner()


def test_should_display_version():
    """Verify version command outputs OpenRFP version string."""
    # Act
    result = runner.invoke(app, ["version"])

    # Assert
    assert result.exit_code == 0
    assert "OpenRFP" in result.stdout
    assert "0.1.0" in result.stdout


def test_should_seed_and_list_knowledge_base():
    """Verify seeding enterprise truth and listing entries via CLI."""
    # Act - Seed
    seed_result = runner.invoke(app, ["kb", "seed"])
    assert seed_result.exit_code == 0
    assert "Successfully seeded" in seed_result.stdout

    # Act - List
    list_result = runner.invoke(app, ["kb", "list"])
    assert list_result.exit_code == 0
    assert "Enterprise Truth Repository" in list_result.stdout
    assert "SOC 2 Type II" in list_result.stdout


def test_should_shred_rfp_file(tmp_path):
    """Verify shred command parses input file and renders compliance table."""
    # Arrange
    rfp_file = tmp_path / "sample_tender.md"
    rfp_file.write_text("# Requirements\n- Must support SAML 2.0 SSO.\n- Must provide REST API.")

    # Act
    result = runner.invoke(app, ["shred", str(rfp_file), "--buyer", "TestBuyer"])

    # Assert
    assert result.exit_code == 0
    assert "Compliance Matrix" in result.stdout
    assert "REQ-001" in result.stdout


def test_should_draft_and_save_deliverables(tmp_path):
    """Verify draft command runs end-to-end synthesis and exports deliverables."""
    # Arrange
    rfp_file = tmp_path / "sample_tender.md"
    rfp_file.write_text("# Requirements\n- Vendor must provide SOC 2 Type II.")
    out_dir = tmp_path / "out"

    # Act
    runner.invoke(app, ["kb", "seed"])
    result = runner.invoke(app, ["draft", str(rfp_file), "--buyer", "AcmeBank", "--output-dir", str(out_dir)])

    # Assert
    assert result.exit_code == 0
    assert "Proposal Summary for AcmeBank" in result.stdout
    assert (out_dir / "sample-tender-proposal.md").exists()
    assert (out_dir / "sample-tender-proposal-matrix.csv").exists()
