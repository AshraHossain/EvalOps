"""PostgreSQL pgvector-based document store for persistent semantic search."""

import json
from typing import Optional

import psycopg
from pgvector.psycopg import register_vector

# ponytail: assumes pgvector extension installed; no fallback to FAISS


class PGVectorStore:
    """Document embeddings backed by PostgreSQL pgvector."""

    def __init__(self, connection_string: str, table: str = "documents"):
        self.connection_string = connection_string
        self.table = table
        self._conn = None

    async def init(self):
        """Initialize connection and create table if needed."""
        # Note: pgvector requires async_psycopg or synchronous psycopg
        # For now, this is a sync implementation. Use asyncpg wrapper if async needed.
        self._conn = psycopg.connect(self.connection_string)
        register_vector(self._conn)
        self._create_table()

    def _create_table(self):
        """Create documents table with pgvector column if it doesn't exist."""
        with self._conn.cursor() as cur:
            # Enable pgvector extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")

            # Create table
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table} (
                    id SERIAL PRIMARY KEY,
                    doc_id TEXT NOT NULL UNIQUE,
                    content TEXT NOT NULL,
                    source TEXT,
                    metadata JSONB DEFAULT '{{}}',
                    embedding vector(384),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)

            # Create index for vector similarity search
            cur.execute(f"""
                CREATE INDEX IF NOT EXISTS {self.table}_embedding_idx
                ON {self.table}
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """)

            self._conn.commit()

    async def add(self, doc_id: str, content: str, embedding: list, source: str = None, metadata: dict = None):
        """Add or update a document."""
        with self._conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {self.table} (doc_id, content, embedding, source, metadata)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (doc_id) DO UPDATE SET
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    source = EXCLUDED.source,
                    metadata = EXCLUDED.metadata,
                    updated_at = NOW()
                """,
                (doc_id, content, embedding, source, json.dumps(metadata or {}))
            )
        self._conn.commit()

    async def search(self, embedding: list, top_k: int = 5, threshold: float = 0.5) -> list:
        """Search for similar documents using cosine similarity."""
        with self._conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT doc_id, content, source, metadata,
                       1 - (embedding <=> %s::vector) as similarity
                FROM {self.table}
                WHERE 1 - (embedding <=> %s::vector) > %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (embedding, embedding, threshold, embedding, top_k)
            )
            rows = cur.fetchall()

        return [
            {
                "doc_id": row[0],
                "content": row[1],
                "source": row[2],
                "metadata": json.loads(row[3]),
                "score": float(row[4])
            }
            for row in rows
        ]

    async def delete(self, doc_id: str):
        """Delete a document."""
        with self._conn.cursor() as cur:
            cur.execute(f"DELETE FROM {self.table} WHERE doc_id = %s", (doc_id,))
        self._conn.commit()

    async def count(self) -> int:
        """Get total document count."""
        with self._conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {self.table}")
            return cur.fetchone()[0]

    async def close(self):
        """Close database connection."""
        if self._conn:
            self._conn.close()
