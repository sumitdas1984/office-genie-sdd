from src.services.llm_service import classify_request
from src.services.routing_service import route_request


def test_classify_returns_placeholder():
    result = classify_request("test message", "EMP-001", "Engineering")
    assert "category" in result
    assert result["category"] == "Unknown"


def test_route_returns_placeholder():
    result = route_request(category="Unknown", subcategory="needs-review", urgency="medium")
    assert "routing_target" in result