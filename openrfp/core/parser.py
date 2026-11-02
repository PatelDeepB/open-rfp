"""RFP Document Shredder and Compliance Matrix Extractor."""

import re
from pathlib import Path
from typing import List, Optional, Tuple
from openrfp.exceptions import DocumentNotFoundError, ParseError
from openrfp.models import (
    ComplianceRequirement,
    PriorityLevel,
    RequirementCategory,
    RfpDocument,
)


class RfpParser:
    """Parses raw RFP solicitations into structured compliance requirements."""

    CATEGORY_KEYWORDS = {
        RequirementCategory.SECURITY_COMPLIANCE: [
            "soc 2", "iso 27001", "gdpr", "hipaa", "security", "encryption",
            "audit", "penetration", "access control", "mfa", "vulnerability"
        ],
        RequirementCategory.TECHNICAL_ARCHITECTURE: [
            "architecture", "cloud", "aws", "azure", "docker", "kubernetes",
            "microservices", "latency", "scalability", "multi-tenant"
        ],
        RequirementCategory.INTEGRATIONS: [
            "api", "webhook", "rest", "graphql", "oauth", "sso", "salesforce",
            "hubspot", "connector", "sdk"
        ],
        RequirementCategory.SLA_SUPPORT: [
            "sla", "uptime", "availability", "support", "ticket", "response time",
            "disaster recovery", "rpo", "rto"
        ],
        RequirementCategory.PRICING: [
            "pricing", "fee", "cost", "license", "payment", "rate card",
            "discount", "subscription"
        ],
        RequirementCategory.LEGAL_COMMERCIAL: [
            "indemnity", "liability", "warranty", "governing law", "termination",
            "intellectual property", "confidentiality"
        ],
        RequirementCategory.FUNCTIONAL_SPEC: [
            "feature", "workflow", "dashboard", "export", "import", "report",
            "user role", "permission", "notification"
        ],
    }

    def parse_file(self, file_path: Path, buyer_name: str = "Client") -> RfpDocument:
        """Parse an RFP from a local file path (PDF, DOCX, CSV, MD, TXT)."""
        path = Path(file_path)
        if not path.exists():
            raise DocumentNotFoundError(f"File '{path}' does not exist.")

        raw_text = self._extract_text_from_file(path)
        title = path.stem.replace("_", " ").title()
        return self.parse_text(raw_text, title=title, buyer_name=buyer_name)

    def _extract_text_from_file(self, path: Path) -> str:
        """Extract plain text from supported document extensions."""
        suffix = path.suffix.lower()
        try:
            if suffix == ".pdf":
                return self._extract_pdf_text(path)
            if suffix == ".docx":
                return self._extract_docx_text(path)
            if suffix == ".csv":
                return self._extract_csv_text(path)
            return path.read_text(encoding="utf-8")
        except OSError as error:
            raise ParseError(f"Failed to read file {path}: {error}") from error
        except Exception as error:
            raise ParseError(f"Failed to parse document {path}: {error}") from error

    def _extract_pdf_text(self, path: Path) -> str:
        """Extract text content from all pages of a PDF."""
        import pypdf
        reader = pypdf.PdfReader(str(path))
        pages_text = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages_text)

    def _extract_docx_text(self, path: Path) -> str:
        """Extract paragraphs and table text from a DOCX file."""
        import docx
        doc = docx.Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    paragraphs.append(row_text)
        return "\n\n".join(paragraphs)

    def _extract_csv_text(self, path: Path) -> str:
        """Convert CSV rows into requirement statements."""
        import csv
        lines: List[str] = ["# Imported Compliance Matrix"]
        with open(path, "r", encoding="utf-8", errors="ignore") as file:
            reader = csv.reader(file)
            for row in reader:
                joined = " - ".join(cell.strip() for cell in row if cell.strip())
                if joined:
                    lines.append(f"* {joined}")
        return "\n".join(lines)

    def parse_text(
        self, raw_text: str, title: str = "Untitled RFP", buyer_name: str = "Client"
    ) -> RfpDocument:
        """Parse raw solicitation text into a structured RfpDocument."""
        clean_text = raw_text.strip()
        if not clean_text:
            raise ParseError("Cannot parse empty RFP text.")

        sections = self._split_into_sections(clean_text)
        requirements: List[ComplianceRequirement] = []
        requirement_index = 1

        for section_title, content in sections:
            extracted = self._extract_requirements(section_title, content, requirement_index)
            requirements.extend(extracted)
            requirement_index += len(extracted)

        rfp_id = re.sub(r"[^a-zA-Z0-9_-]", "-", title.lower()).strip("-")
        return RfpDocument(
            id=rfp_id or "rfp-solicitation",
            title=title,
            buyer_name=buyer_name,
            raw_text=clean_text,
            requirements=requirements,
        )

    def _split_into_sections(self, text: str) -> List[Tuple[str, str]]:
        """Split solicitation into sections based on headers or numbered blocks."""
        header_pattern = r"(?m)^(?:#{1,3}\s+|Section\s+[A-Z0-9]+[:\.\-]?\s*)(.+)$"
        matches = list(re.finditer(header_pattern, text))
        if not matches:
            return [("General Requirements", text)]

        sections: List[Tuple[str, str]] = []
        for index, match in enumerate(matches):
            section_title = match.group(1).strip()
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            if body:
                sections.append((section_title, body))
        return sections

    def _extract_requirements(
        self, section_title: str, content: str, start_index: int
    ) -> List[ComplianceRequirement]:
        """Extract individual discrete requirement items from a section body."""
        candidates = self._find_requirement_lines(content)
        requirements: List[ComplianceRequirement] = []

        for offset, raw_line in enumerate(candidates):
            req_id = f"REQ-{start_index + offset:03d}"
            category = self._classify_category(raw_line, section_title)
            priority = self._classify_priority(raw_line)
            tags = self._extract_tags(raw_line)

            requirements.append(
                ComplianceRequirement(
                    id=req_id,
                    section_title=section_title,
                    requirement_text=raw_line,
                    category=category,
                    priority=priority,
                    tags=tags,
                )
            )
        return requirements

    def _find_requirement_lines(self, content: str) -> List[str]:
        """Isolate requirement candidate lines using lists, bullets, or modal phrases."""
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        matched: List[str] = []

        for line in lines:
            cleaned = re.sub(r"^(\*|-|\d+[\.\)]|REQ-\d+:?)\s*", "", line).strip()
            if not cleaned or len(cleaned) < 15:
                continue

            is_bullet = bool(re.match(r"^(\*|-|\d+[\.\)])", line))
            has_modal = bool(re.search(r"\b(must|shall|required|will|should|can|needs to)\b", cleaned, re.IGNORECASE))
            has_question = "?" in cleaned

            if is_bullet or has_modal or has_question:
                matched.append(cleaned)

        if not matched and lines:
            return [line for line in lines if len(line) >= 20][:10]
        return matched

    def _classify_category(self, text: str, section: str) -> RequirementCategory:
        """Assign category based on keyword density in text and section title."""
        target_corpus = f"{section.lower()} {text.lower()}"
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in target_corpus for keyword in keywords):
                return category
        return RequirementCategory.FUNCTIONAL_SPEC

    def _classify_priority(self, text: str) -> PriorityLevel:
        """Determine priority level based on solicitation modal language."""
        lowered = text.lower()
        if any(word in lowered for word in ["must", "shall", "mandatory", "non-negotiable"]):
            return PriorityLevel.MANDATORY
        if any(word in lowered for word in ["should", "high priority", "strongly preferred"]):
            return PriorityLevel.HIGH
        if any(word in lowered for word in ["nice to have", "optional", "bonus"]):
            return PriorityLevel.OPTIONAL
        return PriorityLevel.MEDIUM

    def _extract_tags(self, text: str) -> List[str]:
        """Extract key technical tags from requirement text."""
        potential = [
            "SOC 2", "ISO 27001", "GDPR", "HIPAA", "API", "REST", "SSO",
            "AWS", "Azure", "SLA", "RBAC", "Encryption", "SaaS"
        ]
        return [tag for tag in potential if re.search(rf"\b{re.escape(tag)}\b", text, re.IGNORECASE)]
