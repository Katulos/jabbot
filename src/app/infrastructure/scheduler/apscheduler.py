from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dishka import AsyncContainer

from ...client import Client
from ...core.config import settings
from .context import ScheduledContext
from .scheduler import Scheduler
from .wrappers import send_delay_message as _send_delay_message_func


class ApScheduler(Scheduler):
    def __init__(
        self,
        container: AsyncContainer,
        client: Client,
    ) -> None:
        ScheduledContext.container = container

        self.container = container

        self.client = client

        self.executor = AsyncIOExecutor()

        self.job_store = MemoryJobStore()

        job_defaults = {
            "coalesce": settings.get("coalesce"),
            "max_instances": settings.get("max_instances"),
            "misfire_grace_time": settings.get("misfire_grace_time"),
        }

        self.scheduler = AsyncIOScheduler(
            jobstores={"default": self.job_store},
            job_defaults=job_defaults,
            executors={"default": self.executor},
        )

    async def send_delay_message_task(self) -> None:
        if not self.scheduler:
            raise RuntimeError("Scheduler not initialized")

        jobs = self.scheduler.get_jobs()

        if not any(job.id == "send_delay_message" for job in jobs):
            self.scheduler.add_job(
                id="send_delay_message",
                func=_send_delay_message_func,
                kwargs={
                    "client": self.client,
                    "message": settings.get("message"),
                },
                trigger=CronTrigger(
                    day_of_week="mon-fri",
                    hour="*",
                    minute="*",
                    timezone=settings.get("scheduler_timezone"),
                ),
                replace_existing=True,
            )

    async def start(self) -> None:
        await self.send_delay_message_task()
        self.scheduler.start()

    async def close(self) -> None:
        self.scheduler.shutdown()
        self.executor.shutdown()
        self.job_store.shutdown()
