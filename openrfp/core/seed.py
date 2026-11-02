"""Seed data provider for enterprise knowledge base."""

from typing import List
from openrfp.models import KnowledgeItem, RequirementCategory


def get_sample_enterprise_knowledge() -> List[KnowledgeItem]:
    """Return a curated set of enterprise truth items for seeding."""
    return [
        KnowledgeItem(
            id="KB-SEC-001",
            title="SOC 2 Type II Certification",
            category=RequirementCategory.SECURITY_COMPLIANCE,
            content=(
                "Our platform is audited annually by an independent AICPA-accredited firm and maintains "
                "an active SOC 2 Type II report covering Security, Confidentiality, and Availability. "
                "The report is available under NDA via our trust portal."
            ),
            tags=["SOC 2", "Compliance", "Audit", "AICPA"],
            verified_by="Chief Information Security Officer",
        ),
        KnowledgeItem(
            id="KB-SEC-002",
            title="ISO 27001:2022 Certification",
            category=RequirementCategory.SECURITY_COMPLIANCE,
            content=(
                "We hold global ISO/IEC 27001:2022 certification for our Information Security Management "
                "System (ISMS), audited by BSI. Certificate renewal occurs triennially with annual surveillance."
            ),
            tags=["ISO 27001", "Security", "ISMS", "Compliance"],
            verified_by="Head of Governance & Compliance",
        ),
        KnowledgeItem(
            id="KB-SEC-003",
            title="Data Encryption Standards",
            category=RequirementCategory.SECURITY_COMPLIANCE,
            content=(
                "All customer data is encrypted in transit using TLS 1.3 (with TLS 1.2 fallback) and at rest "
                "using AES-256 with envelope encryption managed via AWS KMS / Azure Key Vault with automatic "
                "annual key rotation."
            ),
            tags=["Encryption", "AES-256", "TLS 1.3", "Key Management"],
            verified_by="Security Architecture Lead",
        ),
        KnowledgeItem(
            id="KB-SEC-004",
            title="Identity, SSO, and SCIM Provisioning",
            category=RequirementCategory.SECURITY_COMPLIANCE,
            content=(
                "Enterprise SSO is supported natively via SAML 2.0 and OIDC (Okta, Microsoft Entra ID, Google "
                "Workspace). Automated user lifecycle management is supported through SCIM 2.0 with JIT provisioning."
            ),
            tags=["SSO", "SAML 2.0", "SCIM", "Okta", "Azure AD"],
            verified_by="Identity & Access Lead",
        ),
        KnowledgeItem(
            id="KB-ARCH-001",
            title="Cloud Multi-Tenant Architecture & Isolation",
            category=RequirementCategory.TECHNICAL_ARCHITECTURE,
            content=(
                "The platform runs on AWS and Azure across multiple availability zones using containerized "
                "Kubernetes clusters. Logical tenant isolation is enforced at the database level with strict row-level "
                "security (RLS) and isolated encryption keys per tenant."
            ),
            tags=["Architecture", "Kubernetes", "AWS", "Multi-tenant", "Isolation"],
            verified_by="VP of Engineering",
        ),
        KnowledgeItem(
            id="KB-INT-001",
            title="Developer REST APIs and Webhook Infrastructure",
            category=RequirementCategory.INTEGRATIONS,
            content=(
                "We provide comprehensive OpenAPI 3.1 REST APIs with rate limiting and idempotency headers, "
                "alongside HMAC-signed real-time webhooks for events. SDKs are maintained for Python, Node.js, and Go."
            ),
            tags=["API", "REST", "Webhooks", "SDK", "Developer"],
            verified_by="Head of Developer Platform",
        ),
        KnowledgeItem(
            id="KB-SLA-001",
            title="High Availability and Service Level Agreement",
            category=RequirementCategory.SLA_SUPPORT,
            content=(
                "Enterprise tier guarantees 99.99% monthly service uptime backed by financial SLA credits. "
                "Recovery Point Objective (RPO) is under 5 minutes; Recovery Time Objective (RTO) is under 1 hour."
            ),
            tags=["SLA", "Uptime", "99.99%", "Disaster Recovery", "RPO", "RTO"],
            verified_by="Site Reliability Engineering Director",
        ),
        KnowledgeItem(
            id="KB-LEG-001",
            title="Data Privacy and GDPR/CCPA Compliance",
            category=RequirementCategory.LEGAL_COMMERCIAL,
            content=(
                "We act as a Data Processor under GDPR and Service Provider under CCPA/CPRA. Standard Contractual "
                "Clauses (SCCs) and a comprehensive Data Processing Addendum (DPA) are executed with all enterprise clients."
            ),
            tags=["GDPR", "CCPA", "DPA", "Privacy", "Legal"],
            verified_by="General Counsel",
        ),
    ]
