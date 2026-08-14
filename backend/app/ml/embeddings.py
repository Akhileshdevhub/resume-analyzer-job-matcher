"""Semantic engine: turns text into comparable vectors.

Two backends implement the same tiny interface:

  * ``TfidfEngine`` — always available (scikit-learn only). Represents text as
    TF-IDF vectors and compares them with cosine similarity. Great for
    document-level similarity where words overlap; weak at relating two *single*
    skills that share no words ("PyTorch" vs "deep learning"), because TF-IDF
    only sees surface tokens.

  * ``EmbeddingEngine`` — optional (sentence-transformers). Encodes text with a
    MiniLM transformer into dense vectors that capture *meaning*, so "built
    neural networks in PyTorch" lands near "experience with deep learning
    frameworks" even with no shared words.

``get_semantic_engine`` picks a backend from settings: ``auto`` uses the
transformer if it's installed and falls back to TF-IDF otherwise. This is why
the app runs with zero heavy dependencies, yet upgrades cleanly when they're
present — and why the interview guide can honestly compare TF-IDF vs embeddings.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)


def _rescale(value: float, lo: float, hi: float) -> float:
    """Linearly map [lo, hi] -> [0, 1] and clamp. Used to turn a raw cosine into
    an interpretable 0..1 score, because the useful cosine range differs a lot
    between backends (TF-IDF sits low; transformer embeddings sit higher)."""
    if hi <= lo:
        return max(0.0, min(1.0, value))
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))


class TfidfEngine:
    """Lightweight semantic engine using TF-IDF + cosine similarity."""

    name = "tfidf"

    def calibrate(self, sim: float) -> float:
        """Map a raw TF-IDF cosine into an interpretable 0..1 score.

        TF-IDF cosine between two different document types (resume vs JD) is
        small even when they're clearly related, so we rescale the observed
        useful band [0.0, 0.35] onto [0, 1].
        """
        return _rescale(sim, 0.0, 0.35)

    def similarity(self, a: str, b: str) -> float:
        """Cosine similarity between two documents (0..1)."""
        a, b = (a or "").strip(), (b or "").strip()
        if not a or not b:
            return 0.0
        try:
            vec = TfidfVectorizer(stop_words="english")
            matrix = vec.fit_transform([a, b])
            return float(cosine_similarity(matrix[0], matrix[1])[0, 0])
        except ValueError:
            # Happens if, after stop-word removal, there is no vocabulary.
            return 0.0

    def similarity_matrix(self, items_a: list[str], items_b: list[str]) -> np.ndarray:
        """Pairwise cosine similarities, shape (len(a), len(b)).

        Fits one shared vocabulary over both lists so the vectors are
        comparable. For single-token skills with no shared words this tends
        toward 0 — a documented limitation of the TF-IDF backend.
        """
        if not items_a or not items_b:
            return np.zeros((len(items_a), len(items_b)))
        corpus = items_a + items_b
        try:
            vec = TfidfVectorizer()
            matrix = vec.fit_transform(corpus)
        except ValueError:
            return np.zeros((len(items_a), len(items_b)))
        a_mat = matrix[: len(items_a)]
        b_mat = matrix[len(items_a):]
        return cosine_similarity(a_mat, b_mat)


class EmbeddingEngine:
    """Semantic engine backed by a sentence-transformers model."""

    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer  # local import: optional dep

        self.name = f"embeddings:{model_name}"
        self._model = SentenceTransformer(model_name)

    def calibrate(self, sim: float) -> float:
        """Map a raw transformer cosine into an interpretable 0..1 score.

        MiniLM cosine between a resume and a JD typically lives in ~[0.2, 0.7]
        even for a strong match, so we rescale that band onto [0, 1].
        """
        return _rescale(sim, 0.20, 0.70)

    def _encode(self, texts: list[str]) -> np.ndarray:
        # normalize_embeddings=True makes cosine similarity a simple dot product.
        return self._model.encode(
            texts, normalize_embeddings=True, show_progress_bar=False
        )

    def similarity(self, a: str, b: str) -> float:
        a, b = (a or "").strip(), (b or "").strip()
        if not a or not b:
            return 0.0
        emb = self._encode([a, b])
        return float(np.clip(emb[0] @ emb[1], 0.0, 1.0))

    def similarity_matrix(self, items_a: list[str], items_b: list[str]) -> np.ndarray:
        if not items_a or not items_b:
            return np.zeros((len(items_a), len(items_b)))
        emb_a = self._encode(items_a)
        emb_b = self._encode(items_b)
        return np.clip(emb_a @ emb_b.T, 0.0, 1.0)


@lru_cache
def get_semantic_engine() -> TfidfEngine | EmbeddingEngine:
    """Return the configured semantic engine (cached for the process).

    settings.semantic_backend:
      * "tfidf"      -> always TF-IDF
      * "embeddings" -> force transformer embeddings (errors if not installed)
      * "auto"       -> transformer if available, else TF-IDF
    """
    backend = get_settings().semantic_backend.lower()
    model_name = get_settings().embedding_model

    if backend == "tfidf":
        logger.info("Semantic backend: TF-IDF (forced).")
        return TfidfEngine()

    if backend in ("auto", "embeddings"):
        try:
            engine = EmbeddingEngine(model_name)
            logger.info("Semantic backend: %s", engine.name)
            return engine
        except Exception as exc:
            if backend == "embeddings":
                # The user explicitly asked for embeddings; don't silently hide it.
                raise
            logger.info("sentence-transformers unavailable (%s); using TF-IDF.", exc)
            return TfidfEngine()

    logger.warning("Unknown SEMANTIC_BACKEND=%r; defaulting to TF-IDF.", backend)
    return TfidfEngine()
