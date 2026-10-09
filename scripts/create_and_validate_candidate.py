import os
import zipfile
import hashlib
import sys

def pack_and_validate():
    src_dir = os.path.abspath(r".\yolo26m_best.pt\best")
    dest_dir = os.path.abspath(r".\artifacts")
    os.makedirs(dest_dir, exist_ok=True)
    dest_zip = os.path.join(dest_dir, "yolo26m_candidate.pt")

    print(f"Source dir: {src_dir}")
    print(f"Destination: {dest_zip}")

    # Step 1: Collect source files and hashes
    src_files = {}
    for root, dirs, files in os.walk(src_dir):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, src_dir).replace("\\", "/")
            arcname = f"best/{rel_path}"
            with open(full_path, "rb") as fp:
                content = fp.read()
            src_files[arcname] = {
                "size": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
                "content": content
            }

    print(f"Total source files collected: {len(src_files)}")

    # Step 2: Write to ZIP archive (ZIP_STORED is PyTorch standard for raw tensor memory mapping)
    with zipfile.ZipFile(dest_zip, "w", compression=zipfile.ZIP_STORED) as zf:
        for arcname, meta in sorted(src_files.items()):
            zf.writestr(arcname, meta["content"])

    candidate_size = os.path.getsize(dest_zip)
    print(f"Candidate created. Size: {candidate_size} bytes ({candidate_size / (1024*1024):.2f} MB)")

    # Step 3: Validate candidate byte-for-byte against source
    with zipfile.ZipFile(dest_zip, "r") as zf:
        zip_namelist = zf.namelist()
        assert len(zip_namelist) == len(src_files), f"Count mismatch: zip {len(zip_namelist)} vs src {len(src_files)}"
        
        for name in zip_namelist:
            assert name in src_files, f"Unexpected file in zip: {name}"
            zip_content = zf.read(name)
            zip_sha256 = hashlib.sha256(zip_content).hexdigest()
            src_sha256 = src_files[name]["sha256"]
            assert zip_sha256 == src_sha256, f"Hash mismatch for {name}: {zip_sha256} vs {src_sha256}"

    print("Byte-for-byte validation PASSED: All 778 files match source SHA256 exactly.")

    # Step 4: Test loading with PyTorch and Ultralytics
    print("Testing torch.load(..., weights_only=False)...")
    import torch
    ckpt = torch.load(dest_zip, map_location="cpu", weights_only=False)
    print(f"torch.load SUCCESS. Checkpoint keys: {list(ckpt.keys()) if isinstance(ckpt, dict) else type(ckpt)}")

    if isinstance(ckpt, dict):
        if "model" in ckpt:
            model = ckpt["model"]
            print(f"Model type: {type(model)}")
            if hasattr(model, "names"):
                print(f"Model names from model.names: {model.names}")
        if "names" in ckpt:
            print(f"Names from ckpt['names']: {ckpt['names']}")

    print("\nTesting ultralytics.YOLO...")
    from ultralytics import YOLO
    yolo_model = YOLO(dest_zip)
    print(f"ultralytics.YOLO SUCCESS!")
    print(f"YOLO task: {getattr(yolo_model, 'task', None)}")
    print(f"YOLO model.names: {yolo_model.names}")
    print(f"Model arch / type: {type(yolo_model.model)}")

if __name__ == "__main__":
    pack_and_validate()
