import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from ..db import create_url, get_url, update_url
from ..models import Url


@pytest.fixture(name="db_session")
def session_fixture():
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        "sqlite://", echo=True, connect_args=connect_args, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_create_url(db_session: Session):
    url = Url(url="https://example.org/", shortcode="abc_45")
    assert url.id is None
    create_url(db_session, url)
    assert url.id is not None


def test_update_url(db_session: Session):
    url = Url(url="https://example.org/", shortcode="abc_45")
    create_url(db_session, url)
    assert url.redirect_count == 0
    url.increment_counter()
    update_url(db_session, url)
    assert url.redirect_count == 1


def test_get_url(db_session: Session):
    url = Url(url="https://example.org/", shortcode="abc_45")
    create_url(db_session, url)
    url = get_url(db_session, "abc_45")
    assert url.id is not None
