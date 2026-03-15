import pytest

from pocketpaw.vectordb.chroma_adapter import ChromaAdapter


@pytest.mark.asyncio
async def test_add_and_search():
    adapter = ChromaAdapter("./test_db")

    await adapter.add("1", "User likes python")

    results = await adapter.search("python")

    assert "User likes python" in results
