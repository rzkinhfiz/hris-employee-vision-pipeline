import os
import re
from typing import List, Dict

def scan_employee_folders(target_dir: str) -> List[Dict]:
    """
    Memindai folder target secara aman (Graceful Degradation) dan mengembalikan 
    daftar dictionary berisi metadata karyawan beserta file dokumennya.
    
    Format output:
    [
        {
            "id": "345",
            "nama": "Abdul Ahhas",
            "folder_path": "/path/to/folder",
            "file_paths": ["/path/to/file1.jpg", ...]
        },
        ...
    ]
    """
    results = []
    
    # Menghindari error crash bila folder utama belum ada
    if not os.path.exists(target_dir):
        print(f"[Warning] Direktori sumber tidak ditemukan: {target_dir}")
        return results

    # Regex canggih: menangkap awalan ID, mengabaikan spasi berlebih, 
    # mendeteksi pemisah berupa titik atau strip, dan menangkap sisanya sebagai Nama.
    folder_pattern = re.compile(r"^\s*([\w]+)\s*[\.\-]\s*(.+)$")
    
    valid_extensions = {".jpg", ".jpeg", ".png", ".pdf"}

    # Menggunakan os.scandir untuk performa I/O tinggi
    for entry in os.scandir(target_dir):
        if entry.is_dir():
            folder_name = entry.name
            match = folder_pattern.match(folder_name)
            
            if match:
                emp_id = match.group(1).strip()
                emp_name = match.group(2).strip()
            else:
                # Fallback: jika HRD menamai folder sembarangan tanpa tanda pemisah
                emp_id = "UNKNOWN"
                emp_name = folder_name.strip()
                
            # Kumpulkan hanya file yang valid sesuai ekstensi yang diizinkan (Case-Insensitive)
            file_paths = []
            for file_entry in os.scandir(entry.path):
                if file_entry.is_file():
                    ext = os.path.splitext(file_entry.name)[1].lower()
                    if ext in valid_extensions:
                        file_paths.append(file_entry.path)
            
            # Sortir daftar file agar pembacaan konsisten dari kiri ke kanan (e.g. 1.jpg, 2.jpg)
            file_paths.sort()
            
            results.append({
                "id": emp_id,
                "nama": emp_name,
                "folder_path": entry.path,
                "file_paths": file_paths
            })
            
    # Mengembalikan hasil array berisi list dictionary yang rapi
    return results
