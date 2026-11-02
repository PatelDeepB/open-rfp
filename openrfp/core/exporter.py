"""Multi-format Proposal & Compliance Matrix Exporter."""

import csv
import io
import json
from pathlib import Path
from typing import Dict
from openrfp.models import ConfidenceLevel, ProposalSummary, RfpDocument


class ProposalExporter:
    """Exports proposal deliverables into Markdown, CSV, HTML, and JSON."""

    def to_markdown(self, proposal: ProposalSummary, rfp: RfpDocument) -> str:
        """Compile formal Markdown proposal document."""
        lines = [
            f"# Commercial & Technical Proposal Response",
            f"**Client:** {rfp.buyer_name}  ",
            f"**Solicitation:** {rfp.title}  ",
            f"**Win Readiness Score:** {proposal.win_probability_score}%  ",
            f"**Generated:** {proposal.generated_at}  \n",
            "## 1. Executive Summary",
            f"{proposal.executive_summary}\n",
            "## 2. Compliance & Readiness Overview",
            "| Metric | Value |",
            "|---|---|",
            f"| Total Requirements | {proposal.gap_report.total_requirements} |",
            f"| Verified Capabilities (Green) | {proposal.gap_report.green_count} |",
            f"| Configurable / Review (Amber) | {proposal.gap_report.amber_count} |",
            f"| Knowledge Gaps (Red) | {proposal.gap_report.red_count} |",
            f"| Coverage Percentage | {proposal.gap_report.completeness_percentage}% |\n",
            "## 3. Detailed Compliance Matrix & Responses\n",
        ]

        draft_lookup = {d.requirement_id: d for d in proposal.drafts}
        for req in rfp.requirements:
            draft = draft_lookup.get(req.id)
            conf_tag = draft.confidence.value if draft else "Unassigned"
            answer_text = draft.answer_text if draft else "Pending response."
            sources = ", ".join(draft.cited_sources) if draft and draft.cited_sources else "None"

            lines.extend([
                f"### {req.id}: {req.section_title}",
                f"**Requirement:** {req.requirement_text}",
                f"- **Priority:** {req.priority.value} | **Category:** {req.category.value}",
                f"- **Confidence:** {conf_tag}",
                f"- **Sources:** {sources}",
                f"\n**Response:**\n{answer_text}\n",
            ])

        if proposal.gap_report.tasks:
            lines.extend([
                "## 4. Subject Matter Expert Action Items\n",
                "| Task ID | Requirement ID | Department | Question |",
                "|---|---|---|---|",
            ])
            for task in proposal.gap_report.tasks:
                safe_q = task.question.replace("|", "/")
                lines.append(f"| {task.task_id} | {task.requirement_id} | {task.department.value} | {safe_q} |")

        return "\n".join(lines)

    def to_csv(self, proposal: ProposalSummary, rfp: RfpDocument) -> str:
        """Export tabular compliance matrix as standard CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Requirement ID", "Section", "Requirement Text", "Category",
            "Priority", "Confidence Rating", "Confidence Score", "Response",
            "Cited Sources", "Responsible Department"
        ])

        draft_lookup = {d.requirement_id: d for d in proposal.drafts}
        for req in rfp.requirements:
            draft = draft_lookup.get(req.id)
            writer.writerow([
                req.id,
                req.section_title,
                req.requirement_text,
                req.category.value,
                req.priority.value,
                draft.confidence.value if draft else "N/A",
                draft.confidence_score if draft else 0.0,
                draft.answer_text if draft else "",
                "; ".join(draft.cited_sources) if draft else "",
                draft.target_department.value if draft else "",
            ])
        return output.getvalue()

    def to_html(self, proposal: ProposalSummary, rfp: RfpDocument) -> str:
        """Render a standalone executive HTML proposal report."""
        draft_lookup = {d.requirement_id: d for d in proposal.drafts}
        rows_html = []
        for req in rfp.requirements:
            draft = draft_lookup.get(req.id)
            conf = draft.confidence if draft else ConfidenceLevel.RED
            badge_color = "#10b981" if conf == ConfidenceLevel.GREEN else ("#f59e0b" if conf == ConfidenceLevel.AMBER else "#ef4444")
            rows_html.append(f"""
            <tr>
                <td><strong>{req.id}</strong><br><small>{req.section_title}</small></td>
                <td>{req.requirement_text}</td>
                <td><span style="background:{badge_color}; color:#fff; padding:2px 8px; border-radius:12px; font-size:12px;">{conf.value}</span></td>
                <td>{draft.answer_text if draft else 'Pending'}</td>
            </tr>
            """)

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Proposal: {rfp.title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; color: #1e293b; background: #f8fafc; }}
        .card {{ background: white; padding: 28px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 24px; }}
        h1 {{ color: #0f172a; margin-top: 0; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
        th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #e2e8f0; font-size: 14px; vertical-align: top; }}
        th {{ background: #f1f5f9; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>Proposal for {rfp.buyer_name}</h1>
        <p><strong>Solicitation:</strong> {rfp.title} | <strong>Win Readiness:</strong> {proposal.win_probability_score}%</p>
        <p>{proposal.executive_summary}</p>
    </div>
    <div class="card">
        <h2>Compliance Matrix</h2>
        <table>
            <thead><tr><th>ID</th><th>Requirement</th><th>Status</th><th>Response</th></tr></thead>
            <tbody>{''.join(rows_html)}</tbody>
        </table>
    </div>
</body>
</html>"""

    def to_json(self, proposal: ProposalSummary) -> str:
        """Export proposal structure as pretty JSON string."""
        return json.dumps(proposal.model_dump(), indent=2)

    def save_all(
        self, proposal: ProposalSummary, rfp: RfpDocument, output_dir: Path
    ) -> Dict[str, Path]:
        """Save all format variants to output folder and return file paths."""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        base_name = f"{proposal.rfp_id}-proposal"

        files = {
            "markdown": out_path / f"{base_name}.md",
            "csv": out_path / f"{base_name}-matrix.csv",
            "html": out_path / f"{base_name}.html",
            "json": out_path / f"{base_name}.json",
        }

        files["markdown"].write_text(self.to_markdown(proposal, rfp), encoding="utf-8")
        files["csv"].write_text(self.to_csv(proposal, rfp), encoding="utf-8")
        files["html"].write_text(self.to_html(proposal, rfp), encoding="utf-8")
        files["json"].write_text(self.to_json(proposal), encoding="utf-8")

        return files
