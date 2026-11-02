"""Proposal Synthesis and Context-Aware Proposal Drafting Engine."""

from typing import List, Optional
from openrfp.config import settings
from openrfp.core.gap_analyzer import GapAnalyzer
from openrfp.core.retriever import KnowledgeRetriever
from openrfp.models import (
    ConfidenceLevel,
    Department,
    DraftAnswer,
    ProposalSummary,
    RequirementCategory,
    RfpDocument,
    SearchResult,
)


class ProposalDrafter:
    """Drafts context-aware, grounded proposal answers with confidence scoring."""

    def __init__(self, retriever: KnowledgeRetriever) -> None:
        self.retriever = retriever
        self.gap_analyzer = GapAnalyzer()

    def draft_proposal(
        self, rfp: RfpDocument, custom_notes: Optional[str] = None
    ) -> ProposalSummary:
        """Synthesize answers for all requirements in an RFP solicitation."""
        drafts: List[DraftAnswer] = []

        for req in rfp.requirements:
            search_results = self.retriever.search(
                query=req.requirement_text,
                category=req.category,
                top_k=settings.retrieval_top_k,
                threshold=0.10,
            )
            draft = self._synthesize_answer(req, search_results, rfp.buyer_name)
            drafts.append(draft)

        gap_report = self.gap_analyzer.analyze_gaps(rfp.id, rfp.requirements, drafts)
        win_score = self._calculate_win_probability(drafts, gap_report.completeness_percentage)
        exec_summary = self._generate_executive_summary(rfp, gap_report, win_score)

        return ProposalSummary(
            rfp_id=rfp.id,
            title=rfp.title,
            buyer_name=rfp.buyer_name,
            executive_summary=exec_summary,
            win_probability_score=round(win_score, 1),
            drafts=drafts,
            gap_report=gap_report,
        )

    def _synthesize_answer(
        self, req, results: List[SearchResult], buyer_name: str
    ) -> DraftAnswer:
        """Synthesize a grounded answer for a single requirement."""
        top_match = results[0] if results else None
        top_score = top_match.similarity_score if top_match else 0.0

        confidence = self._determine_confidence(top_score)
        department = self._map_department(req.category)
        cited_sources = [r.item.title for r in results[:2]] if results else []

        assumptions: List[str] = []
        if confidence == ConfidenceLevel.GREEN:
            answer = (
                f"Yes, we fully satisfy this requirement. Grounded in our verified "
                f"specifications ({', '.join(cited_sources)}): {top_match.item.content}"
            )
        elif confidence == ConfidenceLevel.AMBER:
            assumptions.append("Requires alignment on standard multi-tenant vs dedicated VPC.")
            matched_summary = top_match.item.content if top_match else "Partial reference available."
            answer = (
                f"We partially support this requirement for {buyer_name}. {matched_summary} "
                f"[Review recommended for specific SLA or edge-case scope]."
            )
        else:
            assumptions.append(f"No direct knowledge base match found for '{req.requirement_text[:40]}...'")
            answer = (
                f"Pending SME Review: Our standard offering does not have a verified citation for "
                f"this item. Routed to {department.value} for confirmation."
            )

        return DraftAnswer(
            requirement_id=req.id,
            answer_text=answer,
            confidence=confidence,
            confidence_score=top_score,
            cited_sources=cited_sources,
            identified_assumptions=assumptions,
            target_department=department,
        )

    def _determine_confidence(self, score: float) -> ConfidenceLevel:
        """Map similarity score to traffic light confidence rating."""
        if score >= settings.confidence_green:
            return ConfidenceLevel.GREEN
        if score >= settings.confidence_amber:
            return ConfidenceLevel.AMBER
        return ConfidenceLevel.RED

    def _map_department(self, category: RequirementCategory) -> Department:
        """Map requirement category to designated Subject Matter Expert department."""
        mapping = {
            RequirementCategory.SECURITY_COMPLIANCE: Department.SECURITY_INFOSEC,
            RequirementCategory.TECHNICAL_ARCHITECTURE: Department.ENGINEERING_ARCH,
            RequirementCategory.INTEGRATIONS: Department.ENGINEERING_ARCH,
            RequirementCategory.FUNCTIONAL_SPEC: Department.PRODUCT,
            RequirementCategory.SLA_SUPPORT: Department.ENGINEERING_ARCH,
            RequirementCategory.LEGAL_COMMERCIAL: Department.LEGAL_CONTRACTS,
            RequirementCategory.PRICING: Department.PRICING_FINANCE,
        }
        return mapping.get(category, Department.PRODUCT)

    def _calculate_win_probability(
        self, drafts: List[DraftAnswer], completeness: float
    ) -> float:
        """Compute predicted win probability based on verified coverage."""
        if not drafts:
            return 0.0
        green_ratio = sum(1 for d in drafts if d.confidence == ConfidenceLevel.GREEN) / len(drafts)
        amber_ratio = sum(1 for d in drafts if d.confidence == ConfidenceLevel.AMBER) / len(drafts)
        score = (green_ratio * 70.0) + (amber_ratio * 20.0) + (completeness * 0.10)
        return min(98.5, max(15.0, score))

    def _generate_executive_summary(
        self, rfp: RfpDocument, gap_report, win_score: float
    ) -> str:
        """Generate high-level proposal executive narrative."""
        return (
            f"Proposal Response for {rfp.buyer_name}: {rfp.title}. "
            f"Our solution provides {gap_report.completeness_percentage}% compliance coverage "
            f"across {gap_report.total_requirements} identified solicitation requirements. "
            f"With {gap_report.green_count} verified direct capabilities and {gap_report.amber_count} "
            f"configurable items, overall proposal win readiness is rated at {round(win_score, 1)}%."
        )
