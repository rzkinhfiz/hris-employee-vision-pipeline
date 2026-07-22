import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# Definisikan root direktori proyek (satu tingkat di atas folder src)
ROOT_DIR = Path(__file__).resolve().parent.parent

# 2. Ambil variabel dari .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("[Error] GEMINI_API_KEY tidak ditemukan. Harap isi API Key Anda di file .env terlebih dahulu.")
    exit(1)
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")
DELAY_BETWEEN_FILES = int(os.getenv("DELAY_BETWEEN_FILES", "1"))

# Ambil TARGET_FOLDER_PATH, gunakan fallback default jika kosong
TARGET_FOLDER_PATH = os.getenv("TARGET_FOLDER_PATH", "./data/source_folders")

# 3. Tetapkan path untuk folder dan file database Excel
# Menggunakan pathlib untuk mempermudah manipulasi path lintas OS
TARGET_DIR = ROOT_DIR / TARGET_FOLDER_PATH
FAILED_REVIEW_DIR = ROOT_DIR / "failed_review"
DATA_DIR = ROOT_DIR / "data"
EXCEL_TEMPLATE_PATH = DATA_DIR / "Template saja.xlsx"

# 4. Logika inisialisasi folder otomatis & fail-safe Template Excel
def setup_directories_and_files():
    """
    Fungsi untuk memvalidasi dan membuat otomatis folder-folder
    serta file template Excel yang dibutuhkan jika belum ada.
    """
    # Membuat folder data/source_folders
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    
    # Membuat folder failed_review/
    FAILED_REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    
    # Membuat folder data/
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Fail-safe: Membuat Template saja.xlsx beserta headers jika belum ada
    if not EXCEL_TEMPLATE_PATH.exists():
        headers = [
            "ID", "Nama", "NIK", "NPWP", "BPJS Kesehatan", 
            "BPJS Ketenagakerjaan", "Rekening Bank", "Status PTKP", 
            "Catatan / Status"
        ]
        df = pd.DataFrame(columns=headers)
        # Menyimpan ke Excel
        df.to_excel(EXCEL_TEMPLATE_PATH, index=False)

# Jalankan setup folder & file setiap kali modul ini di-import
setup_directories_and_files()

# Blok pengujian sederhana
if __name__ == "__main__":
    print("=== Testing Konfigurasi (src/config.py) ===")
    print(f"GEMINI_API_KEY Terbaca : {'Ya' if GEMINI_API_KEY else 'TIDAK (Periksa .env)'}")
    print(f"TARGET_DIR             : {TARGET_DIR} (Ada: {TARGET_DIR.exists()})")
    print(f"FAILED_REVIEW_DIR      : {FAILED_REVIEW_DIR} (Ada: {FAILED_REVIEW_DIR.exists()})")
    print(f"EXCEL_TEMPLATE_PATH    : {EXCEL_TEMPLATE_PATH} (Ada: {EXCEL_TEMPLATE_PATH.exists()})")
    print("\nStatus: Semua variabel dan environment berhasil diinisialisasi.")
