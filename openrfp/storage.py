"""Persistent file storage for OpenRFP records."""

import json
from pathlib import Path
from typing import List, Optional
from openrfp.config import settings
from openrfp.exceptions import DocumentNotFoundError, StorageError
from openrfp.models import KnowledgeItem, ProposalSummary, RfpDocument


class StorageService:
    """Manages persistent JSON records for documents, knowledge, and proposals."""

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        self.base_dir = Path(base_dir or settings.data_dir)
        self.rfp_dir = self.base_dir / "rfps"
        self.kb_dir = self.base_dir / "knowledge"
        self.proposal_dir = self.base_dir / "proposals"
        self._initialize_directories()

    def _initialize_directories(self) -> None:
        """Create required storage subdirectories."""
        for path in (self.rfp_dir, self.kb_dir, self.proposal_dir):
            path.mkdir(parents=True, exist_ok=True)

    def save_rfp(self, rfp: RfpDocument) -> None:
        """Save an RFP document to disk."""
        target_path = self.rfp_dir / f"{rfp.id}.json"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(target_path, "w", encoding="utf-8") as file:
                json.dump(rfp.model_dump(), file, indent=2)
        except OSError as error:
            raise StorageError(f"Failed to save RFP {rfp.id}: {error}") from error

    def get_rfp(self, rfp_id: str) -> RfpDocument:
        """Retrieve an RFP document by ID."""
        target_path = self.rfp_dir / f"{rfp_id}.json"
        if not target_path.exists():
            raise DocumentNotFoundError(f"RFP with ID '{rfp_id}' not found.")
        try:
            with open(target_path, "r", encoding="utf-8") as file:
                return RfpDocument(**json.load(file))
        except OSError as error:
            raise StorageError(f"Failed to read RFP {rfp_id}: {error}") from error

    def list_rfps(self) -> List[RfpDocument]:
        """List all saved RFPs."""
        records: List[RfpDocument] = []
        for file_path in self.rfp_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    records.append(RfpDocument(**json.load(file)))
            except Exception:
                continue
        return records

    def save_knowledge_item(self, item: KnowledgeItem) -> None:
        """Save a single enterprise truth item."""
        target_path = self.kb_dir / f"{item.id}.json"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(target_path, "w", encoding="utf-8") as file:
                json.dump(item.model_dump(), file, indent=2)
        except OSError as error:
            raise StorageError(f"Failed to save KB item {item.id}: {error}") from error

    def get_all_knowledge_items(self) -> List[KnowledgeItem]:
        """Load all enterprise knowledge items."""
        items: List[KnowledgeItem] = []
        for file_path in self.kb_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    items.append(KnowledgeItem(**json.load(file)))
            except Exception:
                continue
        return items

    def save_proposal(self, proposal: ProposalSummary) -> None:
        """Save a generated proposal summary."""
        target_path = self.proposal_dir / f"{proposal.rfp_id}.json"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(target_path, "w", encoding="utf-8") as file:
                json.dump(proposal.model_dump(), file, indent=2)
        except OSError as error:
            raise StorageError(
                f"Failed to save proposal {proposal.rfp_id}: {error}"
            ) from error

    def get_proposal(self, rfp_id: str) -> ProposalSummary:
        """Retrieve an assembled proposal by RFP ID."""
        target_path = self.proposal_dir / f"{rfp_id}.json"
        if not target_path.exists():
            raise DocumentNotFoundError(f"Proposal for RFP '{rfp_id}' not found.")
        try:
            with open(target_path, "r", encoding="utf-8") as file:
                return ProposalSummary(**json.load(file))
        except OSError as error:
            raise StorageError(
                f"Failed to read proposal {rfp_id}: {error}"
            ) from error
