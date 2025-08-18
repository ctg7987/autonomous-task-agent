from typing import List, Dict

# Best-effort Chroma usage; fallback to in-memory list
try:
    import chromadb  # type: ignore
    from chromadb.utils import embedding_functions  # type: ignore
except Exception:
    chromadb = None  # type: ignore

# Simple in-memory fallback
_FALLBACK_SNIPS: List[Dict] = []

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if chromadb is None:
        return None
    if _client is None:
        _client = chromadb.Client()
    if _collection is None:
        _collection = _client.get_or_create_collection("snippets")
    return _collection


def upsert_snippets(snips: List[Dict]):
    col = _get_collection()
    if col is None:
        _FALLBACK_SNIPS.extend(snips)
        return
    if not snips:
        return
    ids = [str(i) for i in range(len(snips))]
    col.upsert(ids=ids, documents=[s.get("text", "") for s in snips], metadatas=snips)


def query_snippets(query: str, k: int = 5) -> List[Dict]:
    col = _get_collection()
    if col is None:
        # naive contains search
        items = [s for s in _FALLBACK_SNIPS if query.lower() in s.get("text", "").lower()]
        return items[:k]
    res = col.query(query_texts=[query], n_results=k)
    out: List[Dict] = []
    md = res.get("metadatas", [[]])[0]
    for m in md:
        out.append(m)
    return out
