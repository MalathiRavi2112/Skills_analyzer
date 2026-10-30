from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.core.config import settings

class SemanticSimilarityEngine:
    def __init__(self):
        self.model = None
        self._init_transformer()

    def _init_transformer(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        except Exception as e:
            # Fall back to TF-IDF if model download or PyTorch is unavailable
            self.model = None

    def compute_similarity(self, source_texts: List[str], target_context: str) -> float:
        """
        Computes the semantic similarity score (0.0 to 1.0) between a list of text snippets
        (e.g., candidate's projects or experience) and the target context (e.g., job role / JD).
        """
        if not source_texts or not target_context:
            return 0.50 # Neutral baseline score

        combined_source = " ".join([t.strip() for t in source_texts if t.strip()])
        if not combined_source or len(combined_source) < 10:
            return 0.40

        # Method A: Sentence Transformers (Dense Embeddings)
        if self.model:
            try:
                embeddings = self.model.encode([combined_source, target_context])
                sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
                # Scale from [-1, 1] to [0, 1]
                normalized = max(0.0, min(1.0, float((sim + 1.0) / 2.0)))
                # Adjust curve for resume domain
                return round(normalized * 1.15 if normalized < 0.8 else normalized, 3)
            except Exception:
                pass

        # Method B: TF-IDF Fallback
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([combined_source, target_context])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            # TF-IDF on short texts is conservative, apply scaling boost
            boosted = min(1.0, float(sim) * 1.8 + 0.30)
            return round(boosted, 3)
        except Exception:
            return 0.65

similarity_engine = SemanticSimilarityEngine()

