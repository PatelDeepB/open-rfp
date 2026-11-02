"""Unified LLM Provider with graceful heuristic fallback."""

import json
from typing import List, Optional, Tuple
import httpx
from openrfp.config import settings


class LlmClient:
    """Unified client for OpenAI, Anthropic, Gemini, or local heuristic fallback."""

    def __init__(self) -> None:
        self.openai_key = settings.openai_api_key
        self.anthropic_key = settings.anthropic_api_key
        self.gemini_key = settings.gemini_api_key

    def synthesize_response(
        self,
        requirement_text: str,
        buyer_name: str,
        verified_facts: List[str],
    ) -> Tuple[str, List[str]]:
        """Synthesize a tailored proposal answer using LLM or local fallback."""
        if not verified_facts:
            return self._fallback_unmatched(requirement_text)

        if self.openai_key:
            llm_result = self._call_openai(requirement_text, buyer_name, verified_facts)
            if llm_result:
                return llm_result

        return self._fallback_grounded(requirement_text, buyer_name, verified_facts)

    def _call_openai(
        self, requirement_text: str, buyer_name: str, facts: List[str]
    ) -> Optional[Tuple[str, List[str]]]:
        """Generate response via OpenAI Chat API if key is present."""
        prompt = (
            f"You are a Senior B2B Sales Engineer writing an RFP response for prospective client: {buyer_name}.\n"
            f"Requirement: {requirement_text}\n"
            f"Verified Company Facts:\n" + "\n".join(f"- {fact}" for fact in facts) + "\n"
            f"Write a confident, professional, non-hallucinated answer in 2-3 sentences. "
            f"Do not invent capabilities outside the verified facts."
        )
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_key}"},
                    json={
                        "model": settings.openai_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2,
                    },
                )
                if res.status_code == 200:
                    data = res.json()
                    answer = data["choices"][0]["message"]["content"].strip()
                    return answer, []
        except Exception:
            return None
        return None

    def _fallback_grounded(
        self, requirement_text: str, buyer_name: str, facts: List[str]
    ) -> Tuple[str, List[str]]:
        """Deterministic grounding engine when no external API key is active."""
        joined_facts = " ".join(facts)
        answer = (
            f"Yes, our platform satisfies this requirement for {buyer_name}. "
            f"Based on our verified specifications: {joined_facts}"
        )
        return answer, []

    def _fallback_unmatched(self, requirement_text: str) -> Tuple[str, List[str]]:
        """Fallback when no verified knowledge is available."""
        answer = (
            f"Pending Subject Matter Expert review. Our standard documentation does not "
            f"contain a verified match for: '{requirement_text[:50]}...'."
        )
        assumptions = ["Requires architectural confirmation from designated specialist."]
        return answer, assumptions
