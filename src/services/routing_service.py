from typing import Any


def route_request(category: str, subcategory: str, urgency: str = "medium") -> dict[str, Any]:
    """
    Stub for routing. Returns a placeholder routing target.
    Full implementation in FEATURE-003.
    """
    routing_target = f"{category.lower()}-team"
    if urgency == "high":
        routing_target += "-escalation"
    return {"routing_target": routing_target}