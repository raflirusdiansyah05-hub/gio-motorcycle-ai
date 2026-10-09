import pytest
from inference.services.association import compute_ioa, associate_persons_to_motorcycles, IOA_THRESHOLD

def test_compute_ioa_no_overlap():
    # Person dan Motor terpisah sepenuhnya
    person = [0.0, 0.0, 10.0, 10.0]     # area = 100
    motor = [20.0, 20.0, 50.0, 50.0]    # area = 900
    assert compute_ioa(person, motor) == 0.0

def test_compute_ioa_below_threshold():
    # Overlap 50% (50/100) < 0.60
    person = [0.0, 0.0, 10.0, 10.0]     # area = 100
    motor = [0.0, 5.0, 10.0, 15.0]      # overlap y: 5..10 (tinggi 5, lebar 10) -> area 50
    ioa = compute_ioa(person, motor)
    assert abs(ioa - 0.50) < 1e-4

def test_compute_ioa_exact_threshold():
    # Overlap tepat 60% (60/100) == 0.60
    person = [0.0, 0.0, 10.0, 10.0]     # area = 100
    motor = [0.0, 4.0, 10.0, 20.0]      # overlap y: 4..10 (tinggi 6, lebar 10) -> area 60
    ioa = compute_ioa(person, motor)
    assert abs(ioa - 0.60) < 1e-4

def test_compute_ioa_above_threshold():
    # Overlap 100% (person sepenuhnya di dalam motor)
    person = [10.0, 10.0, 20.0, 20.0]   # area = 100
    motor = [0.0, 0.0, 50.0, 50.0]
    ioa = compute_ioa(person, motor)
    assert abs(ioa - 1.0) < 1e-4

def test_compute_ioa_invalid_coordinates():
    # Bounding box dengan koordinat terbalik
    invalid_person = [10.0, 10.0, 5.0, 5.0]
    motor = [0.0, 0.0, 50.0, 50.0]
    assert compute_ioa(invalid_person, motor) == 0.0

def test_associate_highest_ioa_wins():
    # Satu orang overlap dengan dua motor:
    # Motor 1: overlap 65% (0.65)
    # Motor 2: overlap 85% (0.85)
    # Sesuai aturan: orang harus diasosiasikan HANYA ke Motor 2
    person = {"id": 1, "bbox": [10.0, 10.0, 20.0, 20.0], "confidence": 0.90}
    motor_1 = {"id": 1, "bbox": [10.0, 13.5, 20.0, 30.0], "confidence": 0.88} # overlap 6.5 x 10 = 65%
    motor_2 = {"id": 2, "bbox": [10.0, 11.5, 20.0, 30.0], "confidence": 0.85} # overlap 8.5 x 10 = 85%

    motors, unassociated = associate_persons_to_motorcycles([person], [motor_1, motor_2])

    assert len(unassociated) == 0
    assert len(motors[0]["associated_persons"]) == 0 # Motor 1 tidak dapat
    assert len(motors[1]["associated_persons"]) == 1 # Motor 2 dapat
    assert motors[1]["associated_persons"][0]["person_id"] == 1
    assert motors[1]["associated_persons"][0]["ioa"] == 0.85

def test_associate_deterministic_tie_breaking():
    # Satu orang overlap sama persis (misal 80%) dengan dua motor
    # Aturan deterministik: motor dengan indeks lebih kecil (motor 1) harus menang
    person = {"id": 1, "bbox": [10.0, 10.0, 20.0, 20.0], "confidence": 0.90}
    motor_1 = {"id": 1, "bbox": [10.0, 10.0, 20.0, 18.0], "confidence": 0.80} # 8 x 10 = 80
    motor_2 = {"id": 2, "bbox": [10.0, 12.0, 20.0, 20.0], "confidence": 0.80} # 8 x 10 = 80

    motors, unassociated = associate_persons_to_motorcycles([person], [motor_1, motor_2])

    assert len(unassociated) == 0
    assert len(motors[0]["associated_persons"]) == 1
    assert len(motors[1]["associated_persons"]) == 0

def test_unassociated_person_not_counted():
    # Orang dengan IoA < 0.60 tidak diasosiasikan ke motor mana pun
    person = {"id": 1, "bbox": [0.0, 0.0, 10.0, 10.0], "confidence": 0.70}
    motor = {"id": 1, "bbox": [0.0, 5.0, 10.0, 15.0], "confidence": 0.80} # IoA = 0.50

    motors, unassociated = associate_persons_to_motorcycles([person], [motor])

    assert len(motors[0]["associated_persons"]) == 0
    assert len(unassociated) == 1
    assert unassociated[0]["id"] == 1

def test_zero_motorcycles_all_unassociated():
    person_1 = {"id": 1, "bbox": [0.0, 0.0, 10.0, 10.0], "confidence": 0.9}
    person_2 = {"id": 2, "bbox": [20.0, 20.0, 30.0, 30.0], "confidence": 0.8}

    motors, unassociated = associate_persons_to_motorcycles([person_1, person_2], [])
    assert len(motors) == 0
    assert len(unassociated) == 2
