import random
import re
import string
from datetime import datetime, timezone

from pydantic import BaseModel, field_validator, model_serializer
from sqlalchemy.sql import func
from sqlmodel import TIMESTAMP, Column, Field, SQLModel, String

shortcode_pattern = re.compile("^[A-Za-z0-9_]{6}$")


class Url(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    url: str
    shortcode: str = Field(default="", sa_column=Column(String(length=6), unique=True))
    created: datetime | None = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=func.current_timestamp(),
            nullable=False,
        ),
    )
    last_redirect: datetime | None = Field(
        default=None,
        sa_column=Column(TIMESTAMP(timezone=True), onupdate=func.now()),
    )
    redirect_count: int = Field(default=0)

    @field_validator("url")
    @classmethod
    def url_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("URL cannot be empty")
        return v

    @field_validator("shortcode")
    @classmethod
    def shortcode_must_match_pattern(cls, v: str) -> str:
        if not v:
            return cls.generate_shortcode()
        if not shortcode_pattern.match(v):
            raise ValueError(
                "Shortcode must contain exactly 6 alphanumeric characters or underscores"
            )
        return v

    @classmethod
    def generate_shortcode(cls):
        characters = string.ascii_letters + string.digits + "_"
        return "".join(random.sample(characters, 6))

    def increment_counter(self):
        # increment counter (in a concurrent-safe way)
        self.redirect_count = Url.redirect_count + 1
