from logging.config import fileConfig
from sqlalchemy import engine_from_config , pool
from alembic import context
import os
import sys
from database import Base
import auth.models   # این باید User و بقیه جداول رو لود کنه



# مسیر پروژه رو اضافه می‌کنیم (یک پوشه بالاتر از مسیر فعلی Alembic)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# حالا مدل‌ها رو ایمپورت می‌کنیم تا Alembic بشناسه
from models import Base  # این باید دقیقا همون Base پروژه باشه
import models  # اگر همه مدل‌ها در models.py هستند، همین کافیه
import auth.models
from database import Base
# اینجا تنظیمات Alembic.ini رو می‌گیریم
config = context.config

# اگه فایل لاگ موجود بود، کانفیگش رو می‌گیریم
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# متادیتای مدل‌ها رو معرفی می‌کنیم
target_metadata = Base.metadata

# تابع گرفتن URL دیتابیس (از env یا مستقیم)
def get_url():
    return os.getenv("DATABASE_URL", "sqlite:///./test.db")  # تغییر بده به URL واقعی دیتابیس

# اجرای migration در حالت offline
def run_migrations_offline():
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# اجرای migration در حالت online
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},  # پیش‌فرض خالی
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
