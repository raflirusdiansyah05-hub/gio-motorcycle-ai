from typing import List, Dict, Any, Tuple

IOA_THRESHOLD = 0.60

def compute_ioa(person_box: List[float], motor_box: List[float]) -> float:
    """
    Menghitung Intersection over Area (IoA) antara bounding box orang (P) dan motor (M).
    IoA(P, M) = Area(P ∩ M) / Area(P)
    
    Bounding box format: [x1, y1, x2, y2]
    """
    px1, py1, px2, py2 = person_box
    mx1, my1, mx2, my2 = motor_box

    # Validasi koordinat
    if px2 <= px1 or py2 <= py1:
        return 0.0
    if mx2 <= mx1 or my2 <= my1:
        return 0.0

    person_area = (px2 - px1) * (py2 - py1)
    if person_area <= 0.0:
        return 0.0

    # Hitung irisan (intersection)
    ix1 = max(px1, mx1)
    iy1 = max(py1, my1)
    ix2 = min(px2, mx2)
    iy2 = min(py2, my2)

    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    intersection_area = iw * ih

    if intersection_area <= 0.0:
        return 0.0

    return float(intersection_area / person_area)


def associate_persons_to_motorcycles(
    persons: List[Dict[str, Any]],
    motorcycles: List[Dict[str, Any]],
    threshold: float = IOA_THRESHOLD
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Mengasosiasikan deteksi orang ke sepeda motor berdasarkan threshold IoA (>= 0.60).
    
    Aturan Proyek (Telah Disetujui):
    1. Jika satu orang memenuhi threshold untuk >1 motor:
       Orang diasosiasikan HANYA ke motor dengan IoA tertinggi (highest IoA).
    2. Satu orang tidak boleh dihitung pada lebih dari satu motor.
    3. Jika terdapat nilai IoA yang sama persis (tie), gunakan aturan deterministik:
       pilih motor dengan indeks deteksi terkecil (indeks pertama).
    4. Orang yang tidak memenuhi threshold untuk motor mana pun dicatat sebagai unassociated.
    5. Motor tanpa orang tetap dipertahankan dengan list associated_persons kosong.

    Input:
      persons: list dict dengan key 'id', 'bbox', 'confidence'
      motorcycles: list dict dengan key 'id', 'bbox', 'confidence'

    Output:
      (motorcycles_with_associations, unassociated_persons)
    """
    # Siapkan container untuk setiap motor
    motor_results = []
    for m in motorcycles:
        motor_results.append({
            "id": m["id"],
            "bbox": m["bbox"],
            "confidence": m["confidence"],
            "associated_persons": []
        })

    unassociated_persons = []

    if not motorcycles:
        # Jika tidak ada motor sama sekali, semua orang unassociated
        return motor_results, persons.copy()

    # Evaluasi setiap orang terhadap semua motor
    for p in persons:
        best_motor_idx = None
        best_ioa = -1.0

        for m_idx, m in enumerate(motorcycles):
            ioa = compute_ioa(p["bbox"], m["bbox"])
            if ioa >= threshold:
                # Cek highest IoA dengan tie-breaker indeks terkecil
                # Menggunakan round(ioa, 6) untuk stabilitas floating point
                if ioa > best_ioa:
                    best_ioa = ioa
                    best_motor_idx = m_idx

        person_id = p.get("person_id", p.get("id", 0))
        if best_motor_idx is not None and best_ioa >= threshold:
            motor_results[best_motor_idx]["associated_persons"].append({
                "id": person_id,
                "person_id": person_id,
                "bbox": p["bbox"],
                "confidence": p["confidence"],
                "ioa": round(best_ioa, 4)
            })
        else:
            unassociated_persons.append({
                "id": person_id,
                "person_id": person_id,
                "bbox": p["bbox"],
                "confidence": p["confidence"]
            })

    return motor_results, unassociated_persons
