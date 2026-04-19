from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlmodel import Session, select
from db.database import engine
from db.models import ScheduledAutomation, Thread, ThreadTask
import logging
from utils.procedures import generate_thread_id

logger = logging.getLogger(__name__)

class AutomationScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def start(self):
        self.scheduler.start()
        logger.info("Automation Scheduler started.")
        self.load_jobs()

    def load_jobs(self):
        with Session(engine) as db:
            automations = db.exec(select(ScheduledAutomation).where(ScheduledAutomation.is_active == True)).all()
            for auto in automations:
                self.add_automation_job(auto)

    def add_automation_job(self, auto: ScheduledAutomation):
        job_id = f"auto_{auto.id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        self.scheduler.add_job(
            self.trigger_automation,
            CronTrigger.from_crontab(auto.cron_expression),
            args=[auto.id],
            id=job_id
        )
        logger.info(f"Scheduled automation '{auto.name}' with cron '{auto.cron_expression}'")

    async def trigger_automation(self, auto_id: int):
        with Session(engine) as db:
            auto = db.get(ScheduledAutomation, auto_id)
            if not auto or not auto.is_active: return

            logger.info(f"Triggering scheduled automation: {auto.name}")

            # Create a new thread for this run
            new_thread = Thread(
                title=f"Scheduled: {auto.name}",
                user_id=auto.user_id
            )
            db.add(new_thread)
            db.commit()
            db.refresh(new_thread)

            # Create the task
            task = ThreadTask(
                thread_id=new_thread.id,
                task_text=auto.task_text
            )
            db.add(task)
            db.commit()

automation_scheduler = AutomationScheduler()
