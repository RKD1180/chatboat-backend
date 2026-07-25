import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
from config.database import get_connection
from typing import Optional, List
import threading

# Thread-safe vectorizer cache per project
_project_vectorizers = {}
_vectorizer_lock = threading.Lock()


def get_project_vectorizer(project_id: str, texts: List[str] = None) -> TfidfVectorizer:
    """Get or create a TF-IDF vectorizer for a project."""
    with _vectorizer_lock:
        if project_id not in _project_vectorizers:
            if texts:
                vectorizer = TfidfVectorizer(
                    max_features=768,
                    stop_words="english",
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                )
                vectorizer.fit(texts)
                _project_vectorizers[project_id] = vectorizer
            else:
                # Create empty vectorizer (will be rebuilt)
                _project_vectorizers[project_id] = TfidfVectorizer(
                    max_features=768,
                    stop_words="english",
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                )
        return _project_vectorizers[project_id]


def rebuild_project_vectorizer(project_id: str, texts: List[str]):
    """Rebuild the TF-IDF vectorizer for a project."""
    with _vectorizer_lock:
        vectorizer = TfidfVectorizer(
            max_features=768,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        if texts:
            vectorizer.fit(texts)
        _project_vectorizers[project_id] = vectorizer


async def generate_embedding(text: str) -> Optional[List[float]]:
    """Generate TF-IDF embedding for text."""
    try:
        vectorizer = TfidfVectorizer(
            max_features=768,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        tfidf_matrix = vectorizer.fit_transform([text])
        embedding = tfidf_matrix.toarray()[0].tolist()
        # Pad to 768 dimensions if needed
        while len(embedding) < 768:
            embedding.append(0.0)
        return embedding[:768]
    except Exception:
        return None


async def generate_embeddings_batch(texts: List[str]) -> List[Optional[List[float]]]:
    """Generate TF-IDF embeddings for a batch of texts."""
    try:
        vectorizer = TfidfVectorizer(
            max_features=768,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        if texts:
            vectorizer.fit(texts)
        embeddings = vectorizer.transform(texts).toarray().tolist()
        # Pad each embedding to 768 dimensions
        padded = []
        for emb in embeddings:
            while len(emb) < 768:
                emb.append(0.0)
            padded.append(emb[:768])
        return padded
    except Exception:
        return [None] * len(texts)


async def generate_query_embedding(query: str, project_id: str) -> Optional[List[float]]:
    """Generate embedding for a query using project's cached vectorizer."""
    try:
        with _vectorizer_lock:
            if project_id in _project_vectorizers:
                vectorizer = _project_vectorizers[project_id]
                embedding = vectorizer.transform([query]).toarray()[0].tolist()
            else:
                # Fallback to single-use vectorizer
                return await generate_embedding(query)
        
        # Pad to 768 dimensions
        while len(embedding) < 768:
            embedding.append(0.0)
        return embedding[:768]
    except Exception:
        return await generate_embedding(query)


async def store_embeddings_to_db(project_id: str, user_id: str):
    """Regenerate and store embeddings for all training data in a project."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # Get all training data for this project
        cur.execute(
            "SELECT id, content FROM training_data WHERE user_id = %s AND project_id = %s",
            (user_id, project_id),
        )
        rows = cur.fetchall()
        
        if not rows:
            cur.close()
            return
        
        ids = [r[0] for r in rows]
        contents = [r[1] for r in rows]
        
        # Rebuild vectorizer for this project and generate embeddings
        rebuild_project_vectorizer(project_id, contents)
        vectorizer = get_project_vectorizer(project_id)
        embeddings = vectorizer.transform(contents).toarray().tolist()
        
        # Pad and store each embedding
        for row_id, embedding in zip(ids, embeddings):
            padded = embedding.tolist()
            while len(padded) < 768:
                padded.append(0.0)
            padded = padded[:768]
            embedding_str = f"[{','.join(str(x) for x in padded)}]"
            cur.execute(
                "UPDATE training_data SET embeddings = %s::vector WHERE id = %s",
                (embedding_str, row_id),
            )
        
        conn.commit()
        cur.close()
    finally:
        conn.close()


async def find_relevant_chunks_from_db(
    user_id: str,
    project_id: str,
    query: str,
    top_k: int = 5,
) -> List[dict]:
    """Find relevant chunks using vector similarity search from database."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # Generate query embedding (using cached vectorizer if available)
        query_embedding = await generate_query_embedding(query, project_id)
        
        if not query_embedding:
            # Fallback: return all training data
            cur.execute(
                "SELECT id, content, type, file_name FROM training_data WHERE user_id = %s AND project_id = %s",
                (user_id, project_id),
            )
            rows = cur.fetchall()
            cur.close()
            return [{"content": r[1], "similarity": 0.5, "type": r[2], "fileName": r[3]} for r in rows[:top_k]]
        
        # Try vector search first
        query_embedding_str = f"[{','.join(str(x) for x in query_embedding)}]"
        
        try:
            cur.execute(
                """SELECT id, content, type, file_name, 
                   1 - (embeddings <=> %s::vector) as similarity
                   FROM training_data 
                   WHERE user_id = %s AND project_id = %s AND embeddings IS NOT NULL
                   ORDER BY embeddings <=> %s::vector
                   LIMIT %s""",
                (query_embedding_str, user_id, project_id, query_embedding_str, top_k),
            )
            rows = cur.fetchall()
        except Exception:
            # If vector search fails, fallback to getting all data
            cur.execute(
                "SELECT id, content, type, file_name FROM training_data WHERE user_id = %s AND project_id = %s",
                (user_id, project_id),
            )
            rows = cur.fetchall()
            rows = [(r[0], r[1], r[2], r[3], 0.5) for r in rows[:top_k]]
        
        cur.close()
        
        if rows:
            return [
                {"content": r[1], "similarity": float(r[4]) if r[4] else 0.5, "type": r[2], "fileName": r[3]}
                for r in rows
            ]
        
        return []
    finally:
        conn.close()
