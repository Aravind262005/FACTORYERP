import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv('backend/.env')
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    tables = conn.execute(text("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema IN ('manufacturing', 'inventory', 'procurement', 'orders', 'application', 'audit')")).fetchall()
    print("Tables found:", tables)
