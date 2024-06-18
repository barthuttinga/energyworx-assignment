import os

from sqlalchemy.engine import URL
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, create_engine, select

from . import exc, models

url = URL.create(
    drivername="mysql+mysqlconnector",
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
)
engine = create_engine(url, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


def create_url(db_session: Session, url: models.Url):
    try:
        db_session.add(url)
        db_session.commit()
    except IntegrityError:
        raise exc.DuplicateShortcodeError()
    db_session.refresh(url)


def update_url(db_session: Session, url: models.Url):
    db_session.add(url)
    db_session.commit()
    db_session.refresh(url)


def get_url(db_session: Session, shortcode: str) -> models.Url:
    statement = select(models.Url).where(models.Url.shortcode == shortcode)
    return db_session.exec(statement).first()
