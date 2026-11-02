"""Automated Gap Identification and SME Routing Engine."""

from typing import Dict, List
from openrfp.models import (
    ComplianceRequirement,
    ConfidenceLevel,
    Department,
    DraftAnswer,
    GapReport,
    SmeTask,
)


class GapAnalyzer:
    """Analyzes requirements against drafts to flag gaps and route tasks to specialists."""

    def analyze_gaps(
        self,
        rfp_id: str,
        requirements: List[ComplianceRequirement],
        drafts: List[DraftAnswer],
    ) -> GapReport:
        """Generate a complete audit of gaps, confidence counts, and SME review tasks."""
        total = len(requirements)
        if total == 0:
            return GapReport(
                rfp_id=rfp_id,
                total_requirements=0,
                green_count=0,
                amber_count=0,
                red_count=0,
                completeness_percentage=100.0,
                tasks=[],
            )

        draft_lookup: Dict[str, DraftAnswer] = {draft.requirement_id: draft for draft in drafts}
        green_count = 0
        amber_count = 0
        red_count = 0
        tasks: List[SmeTask] = []
        task_counter = 1

        for req in requirements:
            draft = draft_lookup.get(req.id)
            if not draft:
                red_count += 1
                tasks.append(self._create_task(req, None, task_counter))
                task_counter += 1
                continue

            if draft.confidence == ConfidenceLevel.GREEN:
                green_count += 1
            elif draft.confidence == ConfidenceLevel.AMBER:
                amber_count += 1
                tasks.append(self._create_task(req, draft, task_counter))
                task_counter += 1
            else:
                red_count += 1
                tasks.append(self._create_task(req, draft, task_counter))
                task_counter += 1

        coverage_points = (green_count * 1.0) + (amber_count * 0.6)
        completeness = round((coverage_points / total) * 100.0, 1)

        return GapReport(
            rfp_id=rfp_id,
            total_requirements=total,
            green_count=green_count,
            amber_count=amber_count,
            red_count=red_count,
            completeness_percentage=completeness,
            tasks=tasks,
        )

    def _create_task(
        self, req: ComplianceRequirement, draft: DraftAnswer | None, counter: int
    ) -> SmeTask:
        """Create a targeted micro-question task for an SME."""
        department = draft.target_department if draft else Department.PRODUCT
        preview = draft.answer_text if draft else "No draft synthesized yet."

        if draft and draft.confidence == ConfidenceLevel.AMBER:
            question = (
                f"Please review and validate our partial support for: '{req.requirement_text}'. "
                f"Confirm if any custom architecture or pricing adjustments apply."
            )
        else:
            question = (
                f"CRITICAL GAP: No verified company documentation matches '{req.requirement_text}'. "
                f"Can we support this capability or should we propose an alternative?"
            )

        return SmeTask(
            task_id=f"TASK-{counter:03d}",
            requirement_id=req.id,
            requirement_text=req.requirement_text,
            department=department,
            question=question,
            draft_preview=preview,
            is_resolved=False,
        )
