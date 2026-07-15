# KnowledgeOps M10: Persistent Vector Store with pgvector

## Overview

M10 replaces the in-memory FAISS index with PostgreSQL + pgvector for persistent, production-ready semantic search storage.

## Architecture

```
Query → Embedding Model → pgvector (PostgreSQL) → Ranked Results
                               ↓
                            IVFFlat Index
                         (384-dim, cosine)
```

## Implementation

### 1. Database Setup

KnowledgeOps now requires PostgreSQL with the pgvector extension:

```bash
# Docker: automatically included in docker-compose.yml
docker-compose up postgres

# Manual installation on existing Postgres:
psql -U postgres -c "CREATE EXTENSION IF NOT EXISTS vector"
```

**Connection string:**
```
postgresql://knowledgeops:knowledgeops@localhost:5433/knowledgeops
```

### 2. Vector Store API

`PGVectorStore` class handles all semantic search operations:

```python
from app.retrieval.pgvector_store import PGVectorStore

store = PGVectorStore(
    connection_string="postgresql://user:pass@host/db",
    table="documents"
)
await store.init()

# Add document
await store.add(
    doc_id="doc-1",
    content="Document text...",
    embedding=[0.1, 0.2, ...],  # 384-dim from sentence-transformers
    source="docs/example.txt",
    metadata={"title": "Example"}
)

# Search
results = await store.search(
    embedding=[0.1, 0.2, ...],
    top_k=5,
    threshold=0.5  # cosine similarity > 0.5
)
# Returns: [{"doc_id": "doc-1", "content": "...", "score": 0.87, ...}, ...]
```

### 3. Index Strategy

- **Index Type**: IVFFlat (Inverted File Flat)
- **Distance Metric**: Cosine similarity (1 - dot product for normalized vectors)
- **Lists**: 100 (tune based on corpus size)
- **Probing**: Auto-tuned by pgvector

For >100k documents, consider tuning:
```sql
ALTER INDEX documents_embedding_idx SET (lists = 500);
ANALYZE documents;
```

### 4. Migration from FAISS

If migrating existing FAISS indices:

```python
import json
from faiss_store import FaissStore  # Old in-memory store
from pgvector_store import PGVectorStore  # New persistent store

# Read all docs from FAISS
faiss_store = FaissStore()
faiss_store.load()  # Load from disk

# Write to pgvector
pg_store = PGVectorStore(connection_string)
await pg_store.init()

for doc_id, embedding in faiss_store.embeddings.items():
    doc = faiss_store.documents[doc_id]
    await pg_store.add(
        doc_id=doc_id,
        content=doc["content"],
        embedding=embedding.tolist(),
        source=doc.get("source"),
        metadata=doc.get("metadata", {})
    )
```

### 5. Configuration

Add to `.env`:
```
KNOWLEDGEOPS_POSTGRES_DSN=postgresql://knowledgeops:knowledgeops@localhost:5433/knowledgeops
KNOWLEDGEOPS_VECTOR_TABLE=documents
KNOWLEDGEOPS_VECTOR_DIM=384  # sentence-transformers default
KNOWLEDGEOPS_VECTOR_SIMILARITY_THRESHOLD=0.5
```

### 6. Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Insert | 5–50ms | Includes embedding compute |
| Search (cold) | 50–200ms | First query, index not in memory |
| Search (warm) | 10–50ms | Index cached, ~1000 documents |
| Batch insert (1000 docs) | 5–30s | Depends on embedding model |

## Roadmap Beyond M10

- **M11**: Add embedding caching layer (Redis) for frequently queried documents
- **M12**: Partitioning strategy for >1M document corpora (sharding by metadata)
- **M13**: Batch ingestion API with progress tracking
- **M14**: Vector index rebuilds and maintenance automation

## Troubleshooting

**"vector extension not found"**
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**Slow search queries**
- Check index stats: `SELECT * FROM pg_stat_user_indexes WHERE relname = 'documents_embedding_idx'`
- Rebuild if needed: `REINDEX INDEX documents_embedding_idx`
- Increase `lists` parameter if corpus grew significantly

**Out of memory**
- pgvector loads the index into shared memory; ensure `shared_buffers >= index_size`
- Reduce `lists` parameter to trade recall for memory

## References

- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [PostgreSQL IVFFlat docs](https://github.com/pgvector/pgvector#indexing)
- [Sentence Transformers models](https://www.sbert.net/docs/pretrained_models.html)
