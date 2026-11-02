"""Domain models and schemas for OpenRFP."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class RequirementCategory(str, Enum):
    """Functional categories for RFP requirements."""

    SECURITY_COMPLIANCE = "Security & Compliance"
    TECHNICAL_ARCHITECTURE = "Technical Architecture"
    FUNCTIONAL_SPEC = "Functional Specifications"
    INTEGRATIONS = "Integrations & APIs"
    SLA_SUPPORT = "SLA & Support"
    LEGAL_COMMERCIAL = "Legal & Terms"
    PRICING = "Pricing & Commercials"
    GENERAL = "General Company Info"


class PriorityLevel(str, Enum):
    """Priority and mandatory status of a requirement."""

    MANDATORY = "Mandatory"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    OPTIONAL = "Optional"


class ConfidenceLevel(str, Enum):
    """Traffic-light confidence rating for generated answers."""

    GREEN = "Green (Verified)"
    AMBER = "Amber (Partial/Review)"
    RED = "Red (Knowledge Gap)"


class ReviewStatus(str, Enum):
    """Human-in-the-loop sign-off status."""

    PENDING = "Pending"
    APPROVED = "Approved"
    REVISED = "Revised"
    REJECTED = "Rejected"


class Department(str, Enum):
    """Subject Matter Expert department responsible for review."""

    SECURITY_INFOSEC = "Security & Infosec"
    ENGINEERING_ARCH = "Cloud & Engineering"
    PRODUCT = "Product Management"
    LEGAL_CONTRACTS = "Legal & Contracts"
    PRICING_FINANCE = "Finance & Pricing"
    EXECUTIVE = "Executive Leadership"


class ComplianceRequirement(BaseModel):
    """A discrete, parsed requirement from an RFP solicitation."""

    id: str
    section_title: str
    requirement_text: str
    category: RequirementCategory = RequirementCategory.GENERAL
    priority: PriorityLevel = PriorityLevel.MEDIUM
    evaluation_criteria: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class RfpDocument(BaseModel):
    """Parsed RFP document structure."""

    id: str
    title: str
    buyer_name: str
    industry: Optional[str] = "Enterprise"
    submission_deadline: Optional[str] = None
    raw_text: str
    requirements: List[ComplianceRequirement] = Field(default_factory=list)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class KnowledgeItem(BaseModel):
    """Verified enterprise truth item in the knowledge repository."""

    id: str
    title: str
    category: RequirementCategory
    content: str
    tags: List[str] = Field(default_factory=list)
    verified_by: Optional[str] = "Security Team"
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class SearchResult(BaseModel):
    """Retrieved knowledge snippet with relevance score."""

    item: KnowledgeItem
    similarity_score: float
    matched_terms: List[str] = Field(default_factory=list)


class DraftAnswer(BaseModel):
    """AI-synthesized answer grounded in enterprise knowledge."""

    requirement_id: str
    answer_text: str
    confidence: ConfidenceLevel
    confidence_score: float
    cited_sources: List[str] = Field(default_factory=list)
    identified_assumptions: List[str] = Field(default_factory=list)
    target_department: Department = Department.PRODUCT
    review_status: ReviewStatus = ReviewStatus.PENDING
    reviewer_notes: Optional[str] = None


class SmeTask(BaseModel):
    """Actionable task routed to a department specialist."""

    task_id: str
    requirement_id: str
    requirement_text: str
    department: Department
    question: str
    draft_preview: Optional[str] = None
    is_resolved: bool = False


class GapReport(BaseModel):
    """Audit of requirement readiness, highlighting risks and gaps."""

    rfp_id: str
    total_requirements: int
    green_count: int
    amber_count: int
    red_count: int
    completeness_percentage: float
    tasks: List[SmeTask] = Field(default_factory=list)


class ProposalSummary(BaseModel):
    """Complete assembled proposal response package."""

    rfp_id: str
    title: str
    buyer_name: str
    executive_summary: str
    win_probability_score: float
    drafts: List[DraftAnswer] = Field(default_factory=list)
    gap_report: GapReport
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
