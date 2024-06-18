from datetime import datetime

import pytest
from sqlalchemy.sql.elements import BinaryExpression

from ..models import StatsResponse, Url, shortcode_pattern


def test_empty_url_validation():
    with pytest.raises(ValueError):
        Url.url_must_not_be_empty("")

    with pytest.raises(ValueError):
        Url.url_must_not_be_empty("    ")


def test_non_empty_url_validation():
    assert Url.url_must_not_be_empty("test") == "test"


def test_empty_shortcode_validation():
    shortcode = Url.shortcode_must_match_pattern(None)
    assert len(shortcode) == 6
    assert shortcode_pattern.match(shortcode)

    shortcode = Url.shortcode_must_match_pattern("")
    assert len(shortcode) == 6
    assert shortcode_pattern.match(shortcode)


def test_invalid_shortcode_validation():
    with pytest.raises(ValueError):
        Url.shortcode_must_match_pattern("_")

    with pytest.raises(ValueError):
        Url.shortcode_must_match_pattern("$123,45")


def test_valid_shortcode_validation():
    assert Url.shortcode_must_match_pattern("abc_45") == "abc_45"


def test_generate_shortcode():
    shortcode = Url.generate_shortcode()
    assert len(shortcode) == 6
    assert shortcode_pattern.match(shortcode)


def test_increment_counter():
    url = Url()
    assert url.redirect_count == 0

    url.increment_counter()
    assert isinstance(url.redirect_count, BinaryExpression)


def test_serialize_statsresponse():
    resp = StatsResponse(created=datetime(2024, 6, 19, 9, 56), redirect_count=0)
    assert resp.serialize_model() == {
        "created": "2024-06-19T07:56:00.000Z",
        "lastRedirect": None,
        "redirectCount": 0,
    }

    resp.redirect_count += 1
    resp.last_redirect = datetime(2024, 6, 19, 9, 59)
    assert resp.serialize_model() == {
        "created": "2024-06-19T07:56:00.000Z",
        "lastRedirect": "2024-06-19T07:59:00.000Z",
        "redirectCount": 1,
    }


def test_format_datetime():
    assert StatsResponse.format_datetime(None) is None
    assert (
        StatsResponse.format_datetime(datetime(2024, 6, 19, 9, 56))
        == "2024-06-19T07:56:00.000Z"
    )
