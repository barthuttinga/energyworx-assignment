from datetime import datetime

from ..schemas import StatsResponse


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
