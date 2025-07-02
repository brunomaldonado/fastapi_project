from sqlmodel import SQLModel, Session, create_engine
from typing import Annotated
from fastapi import Depends
from fastapi import FastAPI

from pathlib import Path
base_dir = Path(__file__).resolve().parent.parent

sqlite_name = base_dir / "db.sqlite3"
sqlite_url = f"sqlite:///{sqlite_name}"

engine = create_engine(sqlite_url)

def get_session():
  with Session(engine) as session:
    yield session

SessionDep = Annotated[Session, Depends(get_session)]

def create_all_tables(app: FastAPI):
  SQLModel.metadata.create_all(engine)
  yield
