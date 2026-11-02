"""Hybrid Semantic & Lexical Knowledge Base Retriever."""

import math
import re
from typing import Dict, List, Optional, Set
from openrfp.models import KnowledgeItem, RequirementCategory, SearchResult


class KnowledgeRetriever:
    """Manages enterprise truth and provides hybrid lexical-semantic retrieval."""

    def __init__(self, items: Optional[List[KnowledgeItem]] = None) -> None:
        self.items: Dict[str, KnowledgeItem] = {}
        if items:
            self.add_items(items)

    def add_item(self, item: KnowledgeItem) -> None:
        """Add a single verified knowledge item to index."""
        self.items[item.id] = item

    def add_items(self, items: List[KnowledgeItem]) -> None:
        """Batch add verified knowledge items."""
        for item in items:
            self.add_item(item)

    def search(
        self,
        query: str,
        category: Optional[RequirementCategory] = None,
        top_k: int = 3,
        threshold: float = 0.15,
    ) -> List[SearchResult]:
        """Search knowledge base with hybrid scoring and category boosting."""
        if not self.items:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scored_results: List[SearchResult] = []
        for item in self.items.values():
            score, matched_terms = self._calculate_similarity(query_tokens, item, category)
            if score >= threshold:
                scored_results.append(
                    SearchResult(
                        item=item,
                        similarity_score=round(score, 3),
                        matched_terms=sorted(matched_terms),
                    )
                )

        scored_results.sort(key=lambda result: result.similarity_score, reverse=True)
        return scored_results[:top_k]

    def _calculate_similarity(
        self,
        query_tokens: Set[str],
        item: KnowledgeItem,
        target_category: Optional[RequirementCategory],
    ) -> tuple[float, Set[str]]:
        """Calculate hybrid overlap score between query and knowledge item."""
        title_tokens = self._tokenize(item.title)
        content_tokens = self._tokenize(item.content)
        tag_tokens = {tag.lower() for tag in item.tags}
        all_item_tokens = title_tokens | content_tokens | tag_tokens

        overlap = query_tokens.intersection(all_item_tokens)
        if not overlap:
            return 0.0, set()

        query_coverage = len(overlap) / float(len(query_tokens))
        title_bonus = 0.20 if query_tokens.intersection(title_tokens) else 0.0
        tag_bonus = 0.10 if query_tokens.intersection(tag_tokens) else 0.0

        category_bonus = 0.0
        if target_category and item.category == target_category:
            category_bonus = 0.15

        raw_score = (query_coverage * 0.65) + title_bonus + tag_bonus + category_bonus
        final_score = min(1.0, raw_score)
        return final_score, overlap

    def _tokenize(self, text: str) -> Set[str]:
        """Normalize text into alphanumeric token set filtering stop words."""
        stop_words = {
            "a", "an", "the", "and", "or", "in", "on", "at", "to", "for",
            "with", "is", "are", "be", "must", "shall", "will", "can", "of"
        }
        tokens = set(re.findall(r"\b[a-zA-Z0-9_-]{2,}\b", text.lower()))
        return tokens - stop_words

    def get_item_by_id(self, item_id: str) -> Optional[KnowledgeItem]:
        """Retrieve an item by its unique ID."""
        return self.items.get(item_id)

    def count(self) -> int:
        """Return the number of indexed knowledge items."""
        return len(self.items)
