from app.database import engine

try:
    conn = engine.connect()
    print("DB CONNECTION SUCCESS")
    conn.close()
except Exception as e:
    print("DB CONNECTION FAILED:", e)