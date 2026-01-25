import os
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from supabase import Client

logger = logging.getLogger(__name__)


class DataCleaner:

    def __init__(self, get_supabase: callable, age_days: int = 2, interval_minutes: int = 60, whitelist: list[str] = None):
        self.get_supabase = get_supabase
        self.age_days = age_days
        self.interval_minutes = interval_minutes
        self.whitelist = set(whitelist) if whitelist else set()
        self.scheduler = BackgroundScheduler()

    def cleanup(self) -> None:
        try:
            supabase = self.get_supabase()
            cutoff = (datetime.now() - timedelta(days=self.age_days)).isoformat()

            old_scans = supabase.table("scans").select("id, image_path").lt("created_at", cutoff).execute()

            if not old_scans.data:
                logger.info("No old scans to clean up")
                return

            # Filter out whitelisted scans
            scans_to_delete = [scan for scan in old_scans.data if scan["id"] not in self.whitelist]
            whitelisted_count = len(old_scans.data) - len(scans_to_delete)

            if whitelisted_count > 0:
                logger.info("Skipping %d whitelisted scans", whitelisted_count)

            if not scans_to_delete:
                logger.info("No scans to clean up after whitelist filter")
                return

            image_paths = [scan["image_path"] for scan in scans_to_delete if scan.get("image_path")]
            scan_ids = [scan["id"] for scan in scans_to_delete]

            if image_paths:
                try:
                    result = supabase.storage.from_("playroom-images").remove(image_paths)
                    logger.info("Deleted %d images from storage: %s", len(image_paths), result)
                except Exception as storage_error:
                    logger.error("Failed to delete images from storage: %s (paths: %s)", storage_error, image_paths)

            # Delete scans by ID to respect whitelist
            for scan_id in scan_ids:
                supabase.table("scans").delete().eq("id", scan_id).execute()
            logger.info("Deleted %d scans older than %d days", len(scan_ids), self.age_days)

        except Exception as e:
            logger.error("Cleanup failed: %s", e)

    def cleanup_orphaned_images(self) -> None:
        """One-time cleanup: delete images not referenced by any scan."""
        try:
            supabase = self.get_supabase()

            # Get all image paths from database
            scans = supabase.table("scans").select("image_path").execute()
            referenced_paths = {scan["image_path"] for scan in scans.data if scan.get("image_path")}

            # List all files in storage
            storage_files = supabase.storage.from_("playroom-images").list("scans")
            if not storage_files:
                logger.info("No files in storage to check for orphans")
                return

            # Find orphaned files (in storage but not in database)
            orphaned_paths = []
            for file in storage_files:
                file_path = f"scans/{file['name']}"
                if file_path not in referenced_paths:
                    orphaned_paths.append(file_path)

            if not orphaned_paths:
                logger.info("No orphaned images found")
                return

            # Delete orphaned files
            try:
                result = supabase.storage.from_("playroom-images").remove(orphaned_paths)
                logger.info("Deleted %d orphaned images: %s", len(orphaned_paths), result)
            except Exception as e:
                logger.error("Failed to delete orphaned images: %s", e)

        except Exception as e:
            logger.error("Orphan cleanup failed: %s", e)

    def start(self) -> None:
        self.cleanup_orphaned_images()  # One-time orphan cleanup on startup
        self.cleanup()
        self.scheduler.add_job(self.cleanup, "interval", minutes=self.interval_minutes)
        self.scheduler.start()
        logger.info("Started data cleaner (age_days=%d, interval=%dm, whitelist=%d)", self.age_days, self.interval_minutes, len(self.whitelist))

    def stop(self) -> None:
        self.scheduler.shutdown()
        logger.info("Stopped data cleaner")
