from loguru import logger
from sqlmodel import create_engine, SQLModel
from pathlib import Path


sqlite_file_name = "database.db"
base_path = Path().resolve()
sqlite_url = f"sqlite:///{base_path}/database/data/{sqlite_file_name}"

engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    logger.info(f'Created DB succesfully!')