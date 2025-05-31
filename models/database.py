from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

# 🔐 MySQL credentials
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_HOST = "localhost"
MYSQL_PORT = "3307"
MYSQL_DB = "final_database"

# 🧠 SQLAlchemy connection string
DATABASE_URL = (
    f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)

# 🔧 SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ✅ FastAPI dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔁 Test connection
def test_db_connection():
    try:
        with engine.connect() as connection:
            print("✅ MySQL connection successful!")
    except OperationalError as e:
        print("❌ MySQL connection failed!")
        print(f"Error: {e}")

if __name__ == "__main__":
    test_db_connection()
