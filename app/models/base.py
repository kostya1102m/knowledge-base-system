import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models.entities import Base


def _get_app_dir() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


APP_DIR = _get_app_dir()
DB_PATH = os.environ.get(
    'WHALE_DB_PATH',
    os.path.join(APP_DIR, 'whales.db')
)

os.makedirs(os.path.dirname(DB_PATH) or '.', exist_ok=True)

ENGINE = create_engine(f'sqlite:///{DB_PATH}', echo=False)
SessionLocal = sessionmaker(bind=ENGINE)


def init_db():
    Base.metadata.create_all(ENGINE)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()