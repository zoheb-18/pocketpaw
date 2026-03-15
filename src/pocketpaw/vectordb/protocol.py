from typing import Protocol


class VectorStoreProtocol(Protocol):
    async def add(self, id: str, text: str) -> None:
        ...

    async def search(self, query: str, limit: int = 5) -> list[str]:
        ...

    async def delete(self, id: str) -> None:
        ...

    async def get_by_id(self, id: str) -> str | None:
        ...
