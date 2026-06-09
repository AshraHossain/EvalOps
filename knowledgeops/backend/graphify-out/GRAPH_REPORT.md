# Graph Report - .  (2026-06-09)

## Corpus Check
- Corpus is ~2,123 words - fits in a single context window. You may not need a graph.

## Summary
- 139 nodes · 215 edges · 28 communities (20 shown, 8 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 20 edges (avg confidence: 0.63)
- Token cost: 23,120 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Query Pipeline|Query Pipeline]]
- [[_COMMUNITY_Retrieval Core|Retrieval Core]]
- [[_COMMUNITY_BM25 Keyword Search|BM25 Keyword Search]]
- [[_COMMUNITY_Test Infrastructure|Test Infrastructure]]
- [[_COMMUNITY_Dependency Injection|Dependency Injection]]
- [[_COMMUNITY_App Bootstrap & Routing|App Bootstrap & Routing]]
- [[_COMMUNITY_Document Ingestion|Document Ingestion]]
- [[_COMMUNITY_App Configuration|App Configuration]]
- [[_COMMUNITY_Search Dependencies|Search Dependencies]]
- [[_COMMUNITY_Observability Stack|Observability Stack]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]

## God Nodes (most connected - your core abstractions)
1. `HybridRetriever` - 18 edges
2. `DocumentChunk` - 17 edges
3. `BM25Retriever` - 12 edges
4. `query()` - 10 edges
5. `VectorRetriever` - 8 edges
6. `evaluate_answer()` - 7 edges
7. `LLMClient` - 7 edges
8. `CrossEncoderReranker` - 7 edges
9. `get_retriever()` - 6 edges
10. `DocumentChunk` - 6 edges

## Surprising Connections (you probably didn't know these)
- `HybridRetriever` --uses--> `HybridRetriever`  [INFERRED]
  tests/test_query_route.py → app/retrieval/hybrid.py
- `DocumentChunk` --uses--> `DocumentChunk`  [INFERRED]
  tests/test_retrieval.py → app/schemas/document.py
- `DocumentChunk` --uses--> `BM25Retriever`  [INFERRED]
  tests/test_retrieval.py → app/retrieval/bm25.py
- `test_bm25_empty_index_returns_empty()` --calls--> `BM25Retriever`  [EXTRACTED]
  tests/test_retrieval.py → app/retrieval/bm25.py
- `_seeded_retriever()` --calls--> `HybridRetriever`  [EXTRACTED]
  tests/test_query_route.py → app/retrieval/hybrid.py

## Import Cycles
- None detected.

## Communities (28 total, 8 thin omitted)

### Community 0 - "Query Pipeline"
Cohesion: 0.14
Nodes (21): HybridRetriever, LLMClient, DocumentChunk, DocumentChunk, AsyncClient, BaseModel, evaluate_answer(), _poll_result() (+13 more)

### Community 1 - "Retrieval Core"
Cohesion: 0.14
Nodes (9): DocumentChunk, DocumentChunk, DocumentChunk, Hybrid retrieval: fuses BM25 and vector scores via Reciprocal Rank Fusion., _reciprocal_rank_fusion(), CrossEncoderReranker, Cross-encoder reranker: re-scores (query, passage) pairs for higher relevance., Dense vector retrieval using sentence-transformers + in-memory FAISS index. (+1 more)

### Community 2 - "BM25 Keyword Search"
Cohesion: 0.26
Nodes (10): DocumentChunk, BM25Retriever, HybridRetriever, _make_chunk(), DocumentChunk, Unit tests for the hybrid retrieval pipeline., test_bm25_empty_index_returns_empty(), test_bm25_returns_relevant_chunk() (+2 more)

### Community 3 - "Test Infrastructure"
Cohesion: 0.18
Nodes (5): ndarray, _FakeCrossEncoder, _FakeIndexFlatIP, _FakeSentenceTransformer, Stub heavy ML dependencies so the test suite runs without a full GPU/ML install.

### Community 4 - "Dependency Injection"
Cohesion: 0.20
Nodes (7): get_llm(), get_retriever(), FastAPI dependency providers — singletons shared across requests., HybridRetriever, LLMClient, LLMClient, LLM client — targets Ollama (local) with an OpenAI-compatible fallback.

### Community 5 - "App Bootstrap & Routing"
Cohesion: 0.21
Nodes (5): DocumentChunk, client(), HybridRetriever, Integration tests for the /api/v1/query endpoint., _seeded_retriever()

### Community 6 - "Document Ingestion"
Cohesion: 0.25
Nodes (8): DocumentChunk, HybridRetriever, DocumentIngestRequest, BM25 keyword retrieval over the document chunk store., _chunk_text(), ingest_document(), DocumentIngestRequest, IngestResponse

### Community 7 - "App Configuration"
Cohesion: 0.50
Nodes (3): Config, Settings, BaseSettings

### Community 8 - "Search Dependencies"
Cohesion: 0.50
Nodes (4): FAISS CPU 1.8.0, Rank-BM25 0.2.2, Semantic Search Capability, Sentence Transformers 3.1.1

### Community 9 - "Observability Stack"
Cohesion: 0.50
Nodes (4): Observability Stack, OpenTelemetry API 1.27.0, OpenTelemetry SDK 1.27.0, Prometheus Client 0.21.0

## Knowledge Gaps
- **23 isolated node(s):** `HybridRetriever`, `LLMClient`, `DocumentChunk`, `DocumentIngestRequest`, `HybridRetriever` (+18 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `HybridRetriever` connect `BM25 Keyword Search` to `Query Pipeline`, `Retrieval Core`, `Dependency Injection`, `App Bootstrap & Routing`, `Document Ingestion`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Why does `DocumentChunk` connect `App Bootstrap & Routing` to `Query Pipeline`, `Retrieval Core`, `BM25 Keyword Search`, `Document Ingestion`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `BM25Retriever` connect `BM25 Keyword Search` to `Retrieval Core`, `Document Ingestion`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `HybridRetriever` (e.g. with `BM25Retriever` and `CrossEncoderReranker`) actually correct?**
  _`HybridRetriever` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `DocumentChunk` (e.g. with `HybridRetriever` and `DocumentChunk`) actually correct?**
  _`DocumentChunk` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `BM25Retriever` (e.g. with `DocumentChunk` and `HybridRetriever`) actually correct?**
  _`BM25Retriever` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `VectorRetriever` (e.g. with `DocumentChunk` and `HybridRetriever`) actually correct?**
  _`VectorRetriever` has 2 INFERRED edges - model-reasoned connections that need verification._