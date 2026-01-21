import os
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from supabase import Client

logger = logging.getLogger(__name__)


class DataCleaner:

    def __init__(self, get_supabase: callable, age_days: int = 2, interval_minutes: int = 60):
        self.get_supabase = get_supabase
        self.age_days = age_days
        self.interval_minutes = interval_minutes
        self.scheduler = BackgroundScheduler()

    def cleanup(self) -> None:
        try:
            supabase = self.get_supabase()
            cutoff = (datetime.now() - timedelta(days=self.age_days)).isoformat()

            old_scans = supabase.table("scans").select("id, image_path").lt("created_at", cutoff).execute()

            if not old_scans.data:
                logger.info("No old scans to clean up")
                return

            image_paths = [scan["image_path"] for scan in old_scans.data if scan.get("image_path")]
            scan_ids = [scan["id"] for scan in old_scans.data]

            if image_paths:
                supabase.storage.from_("playroom-images").remove(image_paths)
                logger.info("Deleted %d images from storage", len(image_paths))

            supabase.table("scans").delete().lt("created_at", cutoff).execute()
            logger.info("Deleted %d scans older than %d days", len(scan_ids), self.age_days)

        except Exception as e:
            logger.error("Cleanup failed: %s", e)

    def start(self) -> None:
        self.cleanup()
        self.scheduler.add_job(self.cleanup, "interval", minutes=self.interval_minutes)
        self.scheduler.start()
        logger.info("Started data cleaner (age_days=%d, interval=%dm)", self.age_days, self.interval_minutes)

    def stop(self) -> None:
        self.scheduler.shutdown()
        logger.info("Stopped data cleaner")
