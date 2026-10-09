import pytest
from inference.services.rules import (
    evaluate_motorcycle_status,
    apply_decision_rules,
    STATUS_AMAN,
    STATUS_PELANGGARAN,
)

def test_evaluate_status_boundaries():
    # 0, 1, 2 orang = AMAN
    assert evaluate_motorcycle_status(0) == STATUS_AMAN
    assert evaluate_motorcycle_status(1) == STATUS_AMAN
    assert evaluate_motorcycle_status(2) == STATUS_AMAN

    # >= 3 orang = PELANGGARAN
    assert evaluate_motorcycle_status(3) == STATUS_PELANGGARAN
    assert evaluate_motorcycle_status(4) == STATUS_PELANGGARAN
    assert evaluate_motorcycle_status(5) == STATUS_PELANGGARAN

def test_apply_decision_rules_multiple_motorcycles():
    # Motor 1: 1 orang (AMAN)
    # Motor 2: 2 orang (AMAN)
    # Motor 3: 3 orang (PELANGGARAN)
    # Motor 4: 0 orang (AMAN)
    associated_motors = [
        {
            "id": 1,
            "bbox": [0, 0, 10, 10],
            "confidence": 0.9,
            "associated_persons": [{"person_id": 1, "ioa": 0.8}]
        },
        {
            "id": 2,
            "bbox": [20, 20, 30, 30],
            "confidence": 0.85,
            "associated_persons": [{"person_id": 2, "ioa": 0.7}, {"person_id": 3, "ioa": 0.9}]
        },
        {
            "id": 3,
            "bbox": [40, 40, 50, 50],
            "confidence": 0.95,
            "associated_persons": [
                {"person_id": 4, "ioa": 0.65},
                {"person_id": 5, "ioa": 0.75},
                {"person_id": 6, "ioa": 0.85}
            ]
        },
        {
            "id": 4,
            "bbox": [60, 60, 70, 70],
            "confidence": 0.8,
            "associated_persons": []
        }
    ]

    results, summary = apply_decision_rules(associated_motors, total_persons_detected=7)

    assert len(results) == 4
    assert results[0]["status"] == STATUS_AMAN
    assert results[0]["person_count"] == 1

    assert results[1]["status"] == STATUS_AMAN
    assert results[1]["person_count"] == 2

    assert results[2]["status"] == STATUS_PELANGGARAN
    assert results[2]["person_count"] == 3

    assert results[3]["status"] == STATUS_AMAN
    assert results[3]["person_count"] == 0

    assert summary["motorcycles"] == 4
    assert summary["persons"] == 7
    assert summary["violations"] == 1
    assert summary["safe"] == 3
