from apscheduler.schedulers.background import BackgroundScheduler
from services.update_db import update_db
import time

def start_scheduler():
    """Start the scheduler to update the database periodically."""
    scheduler = BackgroundScheduler()

    scheduler.add_job(update_db, 'interval', hours=24, next_run_time=None)

    scheduler.start()
    print("✅ Scheduler started! Updating data every 24 hours.")

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("❌ Scheduler stopped.")
