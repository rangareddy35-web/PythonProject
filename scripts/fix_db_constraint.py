import os
from sqlalchemy import create_engine, text
from app.core.config import settings

def drop_constraint():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        print("Dropping constraint 'future_slot' from table 'available_slots'...")
        try:
            conn.execute(text("ALTER TABLE available_slots DROP CONSTRAINT IF EXISTS future_slot;"))
            conn.commit()
            print("Successfully dropped constraint.")
        except Exception as e:
            print(f"Error dropping constraint: {e}")

if __name__ == "__main__":
    drop_constraint()
