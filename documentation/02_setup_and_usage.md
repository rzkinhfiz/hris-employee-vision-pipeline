# Setup & Panduan Penggunaan

Dokumen ini memandu Anda dalam mempersiapkan lingkungan kerja (environment), menyusun folder, dan mengeksekusi pipeline ekstraksi data.

## 1. Persiapan Environment

1. Pastikan **Python 3.9+** telah terpasang. Disarankan menggunakan *virtual environment*.
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Instal seluruh *dependencies* yang diperlukan:
   ```bash
   pip install google-genai pydantic openpyxl pandas python-dotenv
   ```
   *(Atau melalui `pip install -r requirements.txt` jika tersedia).*

3. Konfigurasi Kunci API:
   Buat file `.env` di direktori utama (root) proyek dan isi dengan variabel berikut:
   ```env
   GEMINI_API_KEY=AIzaSy... (Ganti dengan API Key Gemini / Vertex Anda)
   GEMINI_MODEL_NAME=gemini-1.5-flash
   DELAY_BETWEEN_FILES=2
   TARGET_FOLDER_PATH=./data/source_folders
   ```

## 2. Struktur Data Folder

Sistem bergantung pada hierarki folder di `data/source_folders`. Susun dokumen karyawan berdasarkan standar penamaan direktori.

```text
contractfilextractor/
│
├── data/
│   ├── Template saja.xlsx          # File output tempat data disuntikkan
│   └── source_folders/             # Direktori utama target
│       ├── 336. Dita Auliya Nurfalah/
│       │   ├── KTP.jpg
│       │   ├── BPJS.png
│       │   └── Buku Tabungan.jpeg
│       │
│       └── 345. Ghea Farassania/
│           ├── KTP.pdf
│           └── Dokumen Lain.jpg
│
└── main.py
```
> **Catatan Penamaan:** Format `[ID]. [Nama]` (misal `345. Ghea Farassania`) sangat direkomendasikan agar sistem mengidentifikasi ID secara rapi. Jika format tidak sesuai, sistem tetap akan bekerja namun menempatkan keseluruhan nama folder sebagai "Nama" dan ID sebagai "UNKNOWN".

## 3. Eksekusi Skrip

Setelah data tersusun dan `.env` terisi:

1. Jalankan `main.py`:
   ```bash
   python main.py
   ```

2. Pipeline akan secara otomatis:
   - Memindai Karyawan.
   - Mengubah file menjadi bentuk bytes lokal.
   - Berinteraksi dengan Gemini API.
   - Mencetak log keberhasilan maupun log error di konsol.
   - Menambahkan data baris baru di bawah baris terakhir dari `data/Template saja.xlsx` (Sheet: Inject).

3. Buka **`data/Template saja.xlsx`** (Sheet "Inject") setelah program melaporkan "Proses Ekstraksi Selesai!". Jika AI menemukan dokumen buram/terpotong, baca alasannya di **Kolom BX (Kolom 76)**.
