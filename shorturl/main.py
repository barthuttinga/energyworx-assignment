from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlmodel import Session

from . import db
from .exc import DuplicateShortcodeError
from .models import Url
from .schemas import ShortcodeResponse, ShortenRequest, StatsResponse

app = FastAPI()


@app.post("/shorten", response_model=ShortcodeResponse)
def post_shorten_handler(
    req: ShortenRequest, db_session: Session = Depends(db.get_session)
):
    """Shortens the given URL and stores it in the datastore.

    A shortcode of 6 characters (alphanumeric characters or underscores) may be
    provided. If omitted a rondom shortcode is generated.
    """

    try:
        url = Url.model_validate(req)
    except ValidationError as exc:
        for e in exc.errors():
            if e["loc"] == ("url",):
                raise HTTPException(status_code=400, detail="Url not present")
            if e["loc"] == ("shortcode",):
                raise HTTPException(
                    status_code=412, detail="The provided shortcode is invalid"
                )

    try:
        db.create_url(db_session, url)
    except DuplicateShortcodeError:
        raise HTTPException(status_code=409, detail="Shortcode already in use")
    return url


@app.get("/{shortcode}")
def get_shortcode_handler(
    shortcode: str, db_session: Session = Depends(db.get_session)
) -> RedirectResponse:
    """Returns the URL for the provided shortcode.

    When the shortcode is found, the HTTP-reponse has status code 302 and the
    Location header contains the URL. HTTP status code 404 when the shortcode
    is not found.
    """

    # get URL or respond with 404
    url = db.get_url(db_session, shortcode)
    if url is None:
        raise HTTPException(status_code=404, detail="Shortcode not found")

    url.increment_counter()
    db.update_url(db_session, url)

    return RedirectResponse(url=url.url, status_code=302)


@app.get("/{shortcode}/stats", response_model=StatsResponse)
def get_shortcode_stats_handler(
    shortcode: str, db_session: Session = Depends(db.get_session)
):
    """Returns the URL-stats for the provided shortcode."""

    # get URL or respond with 404
    url = db.get_url(db_session, shortcode)
    if url is None:
        raise HTTPException(status_code=404, detail="Shortcode not found")

    return url
