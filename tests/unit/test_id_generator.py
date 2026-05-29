import re


def test_request_id_format():
    from src.services.id_generator import generate_request_id
    uid = generate_request_id()
    assert re.match(r"^REQ-\d{4}-\d{4}$", uid), f"Got: {uid}"


def test_request_id_increments():
    from src.services.id_generator import generate_request_id, reset_counter
    reset_counter()
    id1 = generate_request_id()
    id2 = generate_request_id()
    seq1 = int(id1.split("-")[-1])
    seq2 = int(id2.split("-")[-1])
    assert seq2 > seq1