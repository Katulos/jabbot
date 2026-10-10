from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from ..commands.ping import Ping

router = APIRouter(
    tags=["Root"],
    route_class=DishkaRoute,
)


@router.get("/v1/ping/")
async def ping(command: FromDishka[Ping]) -> str:
    return await command.execute()
