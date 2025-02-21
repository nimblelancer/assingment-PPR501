from apscheduler.schedulers.background import BackgroundScheduler
from services.update_db import update_db
import time

def start_scheduler():
    """Khởi động scheduler để cập nhật database định kỳ."""
    scheduler = BackgroundScheduler()

    # Cập nhật dữ liệu mỗi 24 giờ (tức là 1 lần/ngày)
    scheduler.add_job(update_db, 'interval', hours=24, next_run_time=None)

    scheduler.start()
    print("✅ Scheduler started! Updating data every 24 hours.")

    # Giữ chương trình chạy liên tục nếu chạy độc lập
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("❌ Scheduler stopped.")
