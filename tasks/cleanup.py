# """
# cleanup.py - اسکریپت پاک‌سازی فایل‌های خروجی قدیمی
# ⚠️ این فایل هیچ‌وقت به‌طور خودکار در پروژه اجرا نمی‌شود.
# فقط وقتی مستقیم اجرا کنید (python tasks/cleanup.py) کار می‌کند.
# """

# import os
# import time
# from pathlib import Path

# # فولدرهای خروجی که باید پاک‌سازی شوند
# OUTPUT_DIRS = [
#     Path("static/translated"),
#     Path("converted"),
# ]

# # چند روز نگه‌داری (پیش‌فرض ۳۰ روز)
# MAX_AGE_DAYS = 30


# def cleanup_old_files(max_age_days: int = MAX_AGE_DAYS):
#     """
#     پاک‌سازی فایل‌های قدیمی‌تر از max_age_days روز
#     فقط فایل‌های داخل OUTPUT_DIRS بررسی می‌شوند.
#     """
#     now = time.time()
#     max_age = max_age_days * 24 * 60 * 60  # به ثانیه

#     for output_dir in OUTPUT_DIRS:
#         if not output_dir.exists():
#             continue
#         for user_dir in output_dir.iterdir():
#             if not user_dir.is_dir():
#                 continue
#             for file in user_dir.iterdir():
#                 if file.is_file():
#                     age = now - file.stat().st_mtime
#                     if age > max_age:
#                         try:
#                             print(f"🗑 حذف: {file}")
#                             file.unlink()
#                         except Exception as e:
#                             print(f"❌ خطا در حذف {file}: {e}")


# if __name__ == "__main__":
#     # فقط وقتی مستقیم اجرا کنید کار می‌کند
#     print("🚀 شروع پاک‌سازی فایل‌های قدیمی...")
#     cleanup_old_files()
#     print("✅ پاک‌سازی کامل شد.")
