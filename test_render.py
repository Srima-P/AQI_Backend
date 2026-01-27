from sqlalchemy import create_engine

# Replace with your Render database URL
DATABASE_URL = "postgresql://df772232fa:492a12132e21ebac@AQI_database.idb-node-01.symcloud.net:56645/AQI_database?sslmode=require"

try:
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    print("✅  PostgreSQL connection successful!")
    connection.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")