"""REST API route controllers for OpenRFP."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from openrfp.core.drafter import ProposalDrafter
from openrfp.core.exporter import ProposalExporter
from openrfp.core.parser import RfpParser
from openrfp.core.retriever import KnowledgeRetriever
from openrfp.exceptions import DocumentNotFoundError, OpenRfpError
from openrfp.models import (
    KnowledgeItem,
    ProposalSummary,
    RequirementCategory,
    RfpDocument,
    SearchResult,
)
from openrfp.storage import StorageService

router = APIRouter(prefix="/api/v1", tags=["OpenRFP API"])
storage = StorageService()
parser = RfpParser()
retriever = KnowledgeRetriever()
drafter = ProposalDrafter(retriever=retriever)
exporter = ProposalExporter()


class ParseRfpRequest(BaseModel):
    """Payload to parse raw RFP solicitation text."""

    title: str = "Enterprise RFP"
    buyer_name: str = "Client"
    raw_text: str = Field(..., min_length=10)


class SearchKbRequest(BaseModel):
    """Payload to search enterprise knowledge."""

    query: str
    category: Optional[RequirementCategory] = None
    top_k: int = 5


def _sync_knowledge_base() -> None:
    """Ensure in-memory retriever contains items from disk."""
    items = storage.get_all_knowledge_items()
    retriever.items.clear()
    retriever.add_items(items)


@router.get("/health", status_code=status.HTTP_200_OK)
def check_health() -> dict:
    """Health check endpoint indicating service availability."""
    _sync_knowledge_base()
    return {
        "status": "healthy",
        "version": "0.1.0",
        "knowledge_items_indexed": retriever.count(),
    }


@router.post("/rfp/parse", response_model=RfpDocument)
def parse_rfp(request: ParseRfpRequest) -> RfpDocument:
    """Shred raw RFP text into a structured compliance matrix."""
    try:
        rfp = parser.parse_text(
            raw_text=request.raw_text,
            title=request.title,
            buyer_name=request.buyer_name,
        )
        storage.save_rfp(rfp)
        return rfp
    except OpenRfpError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/rfp/parse-and-draft", response_model=ProposalSummary)
def parse_and_draft(request: ParseRfpRequest) -> ProposalSummary:
    """End-to-end endpoint: parse solicitation and synthesize proposal."""
    try:
        _sync_knowledge_base()
        rfp = parser.parse_text(
            raw_text=request.raw_text,
            title=request.title,
            buyer_name=request.buyer_name,
        )
        storage.save_rfp(rfp)
        proposal = drafter.draft_proposal(rfp)
        storage.save_proposal(proposal)
        return proposal
    except OpenRfpError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/rfp", response_model=List[RfpDocument])
def list_rfps() -> List[RfpDocument]:
    """Retrieve all parsed RFPs."""
    return storage.list_rfps()


@router.get("/rfp/{rfp_id}", response_model=RfpDocument)
def get_rfp_by_id(rfp_id: str) -> RfpDocument:
    """Get single RFP document by ID."""
    try:
        return storage.get_rfp(rfp_id)
    except DocumentNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/knowledge", response_model=KnowledgeItem)
def add_knowledge_item(item: KnowledgeItem) -> KnowledgeItem:
    """Add a verified enterprise truth item to knowledge base."""
    storage.save_knowledge_item(item)
    retriever.add_item(item)
    return item


@router.get("/knowledge", response_model=List[KnowledgeItem])
def list_knowledge_items() -> List[KnowledgeItem]:
    """List all enterprise truth items."""
    return storage.get_all_knowledge_items()


@router.post("/knowledge/search", response_model=List[SearchResult])
def search_knowledge(request: SearchKbRequest) -> List[SearchResult]:
    """Search knowledge base using hybrid semantic-lexical match."""
    _sync_knowledge_base()
    return retriever.search(
        query=request.query,
        category=request.category,
        top_k=request.top_k,
    )


@router.get("/proposal/{rfp_id}", response_model=ProposalSummary)
def get_proposal_by_id(rfp_id: str) -> ProposalSummary:
    """Get synthesized proposal summary by RFP ID."""
    try:
        return storage.get_proposal(rfp_id)
    except DocumentNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/proposal/{rfp_id}/export/{export_format}")
def export_proposal(rfp_id: str, export_format: str) -> Response:
    """Export proposal in markdown, csv, html, or json."""
    try:
        proposal = storage.get_proposal(rfp_id)
        rfp = storage.get_rfp(rfp_id)
    except DocumentNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    fmt = export_format.lower()
    if fmt == "markdown":
        return Response(content=exporter.to_markdown(proposal, rfp), media_type="text/markdown")
    if fmt == "csv":
        return Response(content=exporter.to_csv(proposal, rfp), media_type="text/csv")
    if fmt == "html":
        return Response(content=exporter.to_html(proposal, rfp), media_type="text/html")
    if fmt == "json":
        return Response(content=exporter.to_json(proposal), media_type="application/json")

    raise HTTPException(status_code=400, detail=f"Unsupported format '{export_format}'.")
