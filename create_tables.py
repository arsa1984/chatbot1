from database import engine, Base
import models  # ایمپورت مدل‌ها

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created.")
