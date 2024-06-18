import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from .. import db, models
from ..main import app


@pytest.fixture(name="db_session")
def session_fixture():
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        "sqlite://", echo=True, connect_args=connect_args, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(db_session: Session):
    app.dependency_overrides[db.get_session] = lambda: db_session
    client = TestClient(app, follow_redirects=False)
    yield client
    app.dependency_overrides.clear()


def test_post_shorten_without_url(client: TestClient):
    response = client.post(
        "/shorten",
        json={"shortcode": "123456"},
    )
    assert response.status_code == 400


def test_post_shorten_with_empty_url(client: TestClient):
    response = client.post(
        "/shorten",
        json={"url": "", "shortcode": "123456"},
    )
    assert response.status_code == 400


def test_post_shorten_with_invalid_shortcode(client: TestClient):
    response = client.post(
        "/shorten",
        json={"url": "https://example.org/", "shortcode": "1234"},
    )
    assert response.status_code == 412


def test_post_shorten_with_duplicate_shortcode(db_session: Session, client: TestClient):
    url = models.Url(url="https://example.org/", shortcode="abc_45")
    db_session.add(url)
    db_session.commit()
    db_session.refresh(url)

    response = client.post(
        "/shorten",
        json={"url": url.url, "shortcode": url.shortcode},
    )
    assert response.status_code == 409


def test_post_shorten(client: TestClient):
    response = client.post(
        "/shorten",
        json={"url": "https://example.org/", "shortcode": "abc_45"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["shortcode"] == "abc_45"


def test_post_shorten_without_shortcode(client: TestClient):
    response = client.post(
        "/shorten",
        json={"url": "https://example.org/"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["shortcode"] is not None
    assert len(data["shortcode"]) == 6


def test_get_shortcode_non_existing(client: TestClient):
    response = client.get("/______")
    assert response.status_code == 404


def test_get_shortcode(db_session: Session, client: TestClient):
    url = models.Url(url="https://example.org/", shortcode="abc_45")
    db_session.add(url)
    db_session.commit()
    db_session.refresh(url)

    response = client.get(f"/{url.shortcode}")
    assert response.is_redirect
    assert response.has_redirect_location
    assert response.text == ""


def test_get_shortcode_stats(db_session: Session, client: TestClient):
    url = models.Url(url="https://example.org/", shortcode="abc_45")
    db_session.add(url)
    db_session.commit()

    response = client.get(f"/{url.shortcode}/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["created"] is not None
    assert data["lastRedirect"] is None
    assert data["redirectCount"] == 0

    response = client.get(f"/{url.shortcode}")
    assert response.is_redirect

    response = client.get(f"/{url.shortcode}/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["created"] is not None
    assert data["lastRedirect"] is not None
    assert data["redirectCount"] == 1
