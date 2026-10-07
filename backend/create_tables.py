import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS manufacturing;"))
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS inventory;"))
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS procurement;"))
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS orders;"))
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS application;"))
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS audit;"))
    conn.commit()

from app.models.models import Base
Base.metadata.create_all(bind=engine)

print("Schemas and tables created successfully!")
