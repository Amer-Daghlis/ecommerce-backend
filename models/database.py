from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

# 🔐 MySQL credentials (change these for your own setup)
MYSQL_USER = "root"
MYSQL_PASSWORD = ""   
MYSQL_HOST = "localhost"
MYSQL_PORT = "3308"
MYSQL_DB = "ecommerce_database"

# 🧠 SQLAlchemy connection string (MySQL with mysql-connector)
DATABASE_URL = (
    f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)

# 🔧 SQLAlchemy engine setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ✅ Optional test function
def test_db_connection():
    try:
        with engine.connect() as connection:
            print("✅ MySQL connection successful!")
    except OperationalError as e:
        print("❌ MySQL connection failed!")
        print(f"Error: {e}")

# 🔁 Run test manually (only when executing this file directly)
if __name__ == "__main__":
    test_db_connection()
