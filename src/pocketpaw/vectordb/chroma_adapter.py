import asyncio

from .protocol import VectorStoreProtocol


class ChromaAdapter(VectorStoreProtocol):
    def __init__(self, path: str = "./chroma_db"):
        try:
            import chromadb
        except ImportError:
            raise ImportError(
                "chromadb is required for vector backend. Install with: pip install chromadb"
            )

        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(
            name="pocketpaw_memory"
        )

    async def add(self, id: str, text: str) -> None:
        await asyncio.to_thread(
            self.collection.add,
            documents=[text],
            ids=[id],
        )

    async def search(self, query: str, limit: int = 5) -> list[str]:
        results = await asyncio.to_thread(
            self.collection.query,
            query_texts=[query],
            n_results=limit,
        )

        return results["documents"][0] if results["documents"] else []

    async def delete(self, id: str) -> None:
        await asyncio.to_thread(
            self.collection.delete,
            ids=[id],
        )

    async def get_by_id(self, id: str) -> str | None:
        results = await asyncio.to_thread(
            self.collection.get,
            ids=[id],
        )

        docs = results.get("documents")
        if docs:
            return docs[0]

        return None
