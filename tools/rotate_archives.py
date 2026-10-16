import os
import shutil
from pathlib import Path

def rotate_directory(active_dir, archive_dir, max_active=5):
    active_path = Path(active_dir)
    archive_path = Path(archive_dir)
    
    active_path.mkdir(parents=True, exist_ok=True)
    archive_path.mkdir(parents=True, exist_ok=True)
    
    # Get all files in active directory sorted by modification time (oldest first)
    files = sorted([f for f in active_path.iterdir() if f.is_file()], key=os.path.getmtime)
    
    if len(files) > max_active:
        excess_count = len(files) - max_active
        files_to_archive = files[:excess_count]
        
        for file_to_move in files_to_archive:
            dest = archive_path / file_to_move.name
            shutil.move(str(file_to_move), str(dest))
            print(f"Rotated to archive: {file_to_move.name} -> {archive_dir}")

if __name__ == "__main__":
    # Target rotation directories
    rotate_directory("benchmarks/latest", "benchmarks/archive", max_active=5)
    rotate_directory("configs", "configs/archive", max_active=5)
    print("Archive rotation check complete.")
