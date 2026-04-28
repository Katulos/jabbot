from typing import Protocol


class Scheduler(Protocol):
    async def __aenter__(self) -> "Scheduler":
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def start(self) -> None:
        raise NotImplementedError

    async def close(self) -> None:
        raise NotImplementedError
