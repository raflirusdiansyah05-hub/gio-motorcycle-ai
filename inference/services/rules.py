from typing import List, Dict, Any, Tuple

STATUS_AMAN = "AMAN"
STATUS_PELANGGARAN = "PELANGGARAN"
VIOLATION_THRESHOLD = 3  # >= 3 orang terasosiasi = PELANGGARAN

def evaluate_motorcycle_status(associated_person_count: int) -> str:
    """
    Menentukan status kepatuhan penumpang untuk satu sepeda motor:
    - 0, 1, atau 2 orang: AMAN
    - 3 orang atau lebih: PELANGGARAN
    """
    if associated_person_count >= VIOLATION_THRESHOLD:
        return STATUS_PELANGGARAN
    return STATUS_AMAN


def apply_decision_rules(
    associated_motorcycles: List[Dict[str, Any]],
    total_persons_detected: int
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    Menerapkan aturan status keputusan pada setiap sepeda motor dan menyusun ringkasan (summary).

    Input:
      associated_motorcycles: list dari motor yang telah diasosiasikan (memuat 'associated_persons')
      total_persons_detected: total orang yang terdeteksi oleh model

    Output:
      (motorcycle_results, summary)
    """
    motorcycle_results = []
    total_violations = 0
    total_safe = 0

    for m in associated_motorcycles:
        count = len(m.get("associated_persons", []))
        status = evaluate_motorcycle_status(count)

        if status == STATUS_PELANGGARAN:
            total_violations += 1
        else:
            total_safe += 1

        motorcycle_results.append({
            "id": m["id"],
            "bbox": m["bbox"],
            "confidence": m["confidence"],
            "person_count": count,
            "status": status,
            "associated_persons": m.get("associated_persons", [])
        })

    summary = {
        "motorcycles": len(associated_motorcycles),
        "persons": total_persons_detected,
        "violations": total_violations,
        "safe": total_safe
    }

    return motorcycle_results, summary
