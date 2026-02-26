"""RAG knowledge retrieval using TF-IDF similarity.

Loads markdown files from knowledge_base/, splits them into chunks,
and returns the most relevant chunks for a given query.

Falls back gracefully if scikit-learn is unavailable.
"""

import os
import re
from typing import Optional

_KB_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")


def _load_documents() -> list[dict]:
    """Read all .md files and split into section-level chunks."""
    chunks: list[dict] = []
    kb_dir = os.path.normpath(_KB_DIR)

    if not os.path.isdir(kb_dir):
        return chunks

    for fname in sorted(os.listdir(kb_dir)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(kb_dir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()

        sections = re.split(r"\n(?=## )", text)
        for section in sections:
            section = section.strip()
            if len(section) < 40:
                continue
            heading_match = re.match(r"^#{1,3}\s+(.+)", section)
            heading = heading_match.group(1) if heading_match else fname.replace(".md", "").replace("_", " ").title()
            chunks.append({
                "source": fname,
                "title": heading,
                "text": section,
            })
    return chunks


_retriever: Optional["TFIDFRetriever"] = None


class TFIDFRetriever:
    """Simple TF-IDF retriever over knowledge base chunks."""

    def __init__(self):
        self.chunks = _load_documents()
        self._vectorizer = None
        self._tfidf_matrix = None
        self._available = False

        if not self.chunks:
            return

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            self._cos_sim = cosine_similarity
            self._vectorizer = TfidfVectorizer(
                stop_words="english",
                max_features=5000,
                ngram_range=(1, 2),
            )
            corpus = [c["text"] for c in self.chunks]
            self._tfidf_matrix = self._vectorizer.fit_transform(corpus)
            self._available = True
        except ImportError:
            self._available = False

    @property
    def is_available(self) -> bool:
        return self._available and len(self.chunks) > 0

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        if not self.chunks:
            return []
        if self._available and self._vectorizer and self._tfidf_matrix is not None:
            return self._retrieve_tfidf(query, top_k)
        return self._retrieve_keyword(query, top_k)

    def _retrieve_tfidf(self, query: str, top_k: int) -> list[dict]:
        query_vec = self._vectorizer.transform([query])
        scores = self._cos_sim(query_vec, self._tfidf_matrix).flatten()
        top_indices = scores.argsort()[-top_k:][::-1]
        results = []
        for idx in top_indices:
            if scores[idx] > 0.05:
                chunk = self.chunks[idx].copy()
                chunk["score"] = float(scores[idx])
                results.append(chunk)
        return results

    def _retrieve_keyword(self, query: str, top_k: int) -> list[dict]:
        query_words = set(query.lower().split())
        scored = []
        for chunk in self.chunks:
            text_lower = chunk["text"].lower()
            matches = sum(1 for w in query_words if w in text_lower)
            if matches > 0:
                score = matches / max(len(query_words), 1)
                entry = chunk.copy()
                entry["score"] = score
                scored.append(entry)
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]


def get_retriever() -> TFIDFRetriever:
    global _retriever
    if _retriever is None:
        _retriever = TFIDFRetriever()
    return _retriever


def retrieve_context(query: str, top_k: int = 3) -> str:
    """High-level helper: retrieve the most relevant text for a query."""
    retriever = get_retriever()
    results = retriever.retrieve(query, top_k=top_k)
    if not results:
        return ""

    parts = ["[Relevant knowledge base context]"]
    for r in results:
        parts.append(f"\n--- {r['title']} (from {r['source']}) ---")
        text = r["text"]
        if len(text) > 800:
            text = text[:800] + "..."
        parts.append(text)
    return "\n".join(parts)
