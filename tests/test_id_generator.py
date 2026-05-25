from src.services.id_generator import generate_request_id, reset_counter


def test_request_id_format():
    reset_counter()
    request_id = generate_request_id()
    assert request_id.startswith("REQ-")
    parts = request_id.split("-")
    assert len(parts) == 3
    assert parts[1].isdigit() and len(parts[1]) == 4
    assert parts[2].isdigit() and len(parts[2]) == 4


def test_request_id_increments():
    reset_counter()
    id1 = generate_request_id()
    id2 = generate_request_id()
    assert id1 != id2