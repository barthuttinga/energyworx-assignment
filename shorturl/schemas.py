from datetime import datetime, timezone

from pydantic import BaseModel, model_serializer


class ShortenRequest(BaseModel):
    url: str | None = None
    shortcode: str = ""


class ShortcodeResponse(BaseModel):
    shortcode: str


class StatsResponse(BaseModel):
    created: datetime
    last_redirect: datetime | None = None
    redirect_count: int

    @model_serializer()
    def serialize_model(self):
        return {
            "created": self.format_datetime(self.created),
            "lastRedirect": self.format_datetime(self.last_redirect),
            "redirectCount": self.redirect_count,
        }

    @classmethod
    def format_datetime(cls, dt: datetime | None) -> str | None:
        if dt is None:
            return None
        return (
            dt.astimezone(timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z")
        )
