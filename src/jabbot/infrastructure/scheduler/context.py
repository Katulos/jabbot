from dishka import AsyncContainer
from dishka.integrations.base import wrap_injection


class ScheduledContext:
    container: AsyncContainer


def inject(func):
    async def wrapper(*args, **kwargs):
        async with ScheduledContext.container() as container:
            wrapped = wrap_injection(
                func=func,
                remove_depends=True,
                container_getter=lambda _, __: container,
                is_async=True,
            )
            return await wrapped(*args, **kwargs)

    return wrapper
