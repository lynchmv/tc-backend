import os
import sys
import getpass
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User
from app.security import get_password_hash
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL environment variable not set.")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_superuser(email, password, first_name, last_name):
    db = SessionLocal()
    try:
        if len(password.encode('utf-8')) > 72:
            raise ValueError("Password cannot be longer than 72 bytes.")
        hashed_password = get_password_hash(password)
        superuser = User(
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            role="admin"
        )
        db.add(superuser)
        db.commit()
        db.refresh(superuser)
        print(f"Superuser {email} created successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error creating superuser: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating Superuser...")
    email = input("Enter superuser email: ")
    password = getpass.getpass("Enter superuser password: ")
    first_name = input("Enter superuser first name: ")
    last_name = input("Enter superuser last name: ")

    create_superuser(email, password, first_name, last_name)
