import numpy as np
from PIL import Image
from ultralytics import YOLO

def run_smoke_inference():
    candidate_path = r".\artifacts\yolo26m_candidate.pt"
    print(f"Loading candidate model from {candidate_path}...")
    model = YOLO(candidate_path)

    print(f"Model task: {model.task}")
    print(f"Class mapping: {model.names}")

    # Generate synthetic RGB test image (640x640x3)
    # Note: Synthetic image verifies pipeline tensor execution and output shape, not real-world CV accuracy.
    print("Generating synthetic 640x640 RGB test image...")
    img_array = np.zeros((640, 640, 3), dtype=np.uint8)
    # Add a mock colored rectangle
    img_array[100:500, 150:450, 0] = 200 # Red channel
    img_array[200:400, 200:400, 1] = 150 # Green channel
    img = Image.fromarray(img_array)

    print("Running inference...")
    results = model(img, conf=0.1)

    print("\n--- INFERENCE RESULTS ---")
    print(f"Number of results: {len(results)}")
    res = results[0]
    print(f"Original shape: {res.orig_shape}")
    print(f"Boxes count: {len(res.boxes)}")
    print(f"Speed: {res.speed}")
    print(f"Output classes metadata: {res.names}")

    if len(res.boxes) > 0:
        for idx, box in enumerate(res.boxes):
            cls_id = int(box.cls.item())
            cls_name = res.names.get(cls_id, "unknown")
            conf = float(box.conf.item())
            xyxy = box.xyxy[0].tolist()
            print(f"  Box #{idx}: Class {cls_id} ({cls_name}), Conf={conf:.4f}, BBox={xyxy}")
    else:
        print("No detections on synthetic image (expected for mock solid colors). Pipeline execution succeeded without errors.")

    print("\nInference smoke test COMPLETED SUCCESSFULLY.")

if __name__ == "__main__":
    run_smoke_inference()
