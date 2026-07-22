# Zero-Trace HRIS Data Pipeline

![Data Engineering](https://img.shields.io/badge/Data_Engineering-Automated_Pipeline-blue)
![Computer Vision](https://img.shields.io/badge/AI_Vision-Gemini_1.5_Flash-orange)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![Pydantic](https://img.shields.io/badge/Pydantic-Strict_Schema-red)

**Zero-Trace HRIS Data Pipeline** adalah sebuah proyek *Data Engineering* & *Data Processing* skala produksi yang dirancang untuk mengotomatisasi ekstraksi dokumen administratif kompleks (seperti KTP, NPWP, BPJS, Buku Tabungan, dan Kontrak) milik ratusan karyawan menjadi *dataset* terstruktur.

Proyek ini dibangun sebagai solusi untuk mengatasi pekerjaan *data entry* manual di bidang HRD, dengan mengubah ratusan jam kerja administratif menjadi proses otomatis berbasis AI (Google Gemini Vision API) dalam hitungan menit.

---

## 🌟 Sorotan Data Engineering & Arsitektur

### 1. *Zero-Trace Stateless Architecture* (Keamanan Privasi Tingkat Tinggi)
Dokumen *Human Resources* memuat **Personally Identifiable Information (PII)** kelas A (seperti foto wajah, NIK, dan Mutasi Rekening). Sistem ini dirancang secara *Stateless / In-Memory*: file gambar atau PDF fisik dibaca ke dalam memori (sebagai `bytes`) dan *streaming* langsung ke API Vertex/Gemini, lalu dihapus dari memori sesaat setelah dieksekusi. Tidak ada *upload* dokumen mentah secara permanen ke server manapun (GCS/Drive/Cloud), sehingga menghindari risiko *Data Breach*.

### 2. *Strict Output Validation* dengan Pydantic
Alih-alih menggunakan pemrosesan teks mentah yang rawan halusinasi, saya mendesain infrastruktur ini dengan **Pydantic Model Schema**. Model AI dipaksa *(constrained)* untuk menghasilkan JSON murni yang tervalidasi secara ketat berdasarkan 15+ tipe data HRIS (Nama, NIK, Tempat/Tanggal Lahir, Status Pernikahan, dsb). Jika AI melanggar skema, sistem akan menolak datanya.

### 3. *Explicit Column Mapping* & Data Integrity
Hasil dari AI disuntikkan ke dalam Excel *template* menggunakan perpustakaan *low-level* (`openpyxl`). 
- **Mapping Absolut:** Pemetaan 75 kolom secara manual dan presisi menggunakan *Explicit Mapping*.
- **Data Cleansing Otomatis:** Sistem membersihkan kolom sisa dari *template* awal dengan string kosong (`""`) agar tidak ada data residu tak kasatmata *(hidden artifacts)* yang tertinggal.

### 4. *Graceful Degradation* & *Two-Layer Detection*
- **Level Sistem:** Jika sebuah gambar rusak (*corrupt file*), hanya *batch* gambar spesifik karyawan tersebut yang ditolak *(isolated failure)*. Ratusan folder karyawan lainnya akan tetap berjalan.
- **Level AI:** Dilengkapi Prompt anti-halusinasi. Jika gambar *blur* atau terpotong, model diinstruksikan untuk menghasilkan *Null/None* daripada menebak data, dan otomatis mencatatkan alasan di `catatan_dokumen`.

### 5. *Smart Resume Mode* & *Rate Limit Handler*
Dirancang untuk menghadapi pembatasan kuota (*Rate Limits* `429 RESOURCE_EXHAUSTED`). Skrip *orchestrator* ini akan secara proaktif membaca riwayat baris dari `Template saja.xlsx`. Jika terjadi kegagalan sistematis (komputer mati / koneksi putus), sistem dapat kembali dijalankan dan akan langsung melompati *folder* yang sudah pernah diproses tanpa menghabiskan kuota ganda.

---

## 📂 Struktur Proyek Terpenting

```text
contractfilextractor/
│
├── src/
│   ├── config.py           # Validasi fail-safe environment & manajemen path.
│   ├── schema.py           # Model Pydantic untuk ekstraksi Strict JSON.
│   ├── folder_scanner.py   # Pemindai lokal efisien via `os.scandir` dengan regex.
│   ├── vision_extractor.py # Jantung API Vertex / Gemini Vision (Two-Layer Detection).
│   └── excel_manager.py    # Injeksi data low-level dengan Explicit 75-Column Mapping.
│
├── documentation/
│   ├── 01_architecture_and_pipeline.md # Dokumentasi mendalam arsitektur pipeline.
│   └── 02_setup_and_usage.md           # Panduan lengkap persiapan environment.
│
├── data/
│   ├── source_folders/     # [TEMPATKAN FOLDER KARYAWAN ANDA DI SINI]
│   └── Template saja.xlsx  # File master HRD (Output).
│
├── main.py                 # File orkestrator (titik eksekusi).
└── .env.example            # Template API Keys (jangan di-commit).
```

---

## 🚀 Panduan Setup & Instalasi (Quick Start)

Panduan yang lebih detail dapat Anda temukan di: [Setup & Panduan Penggunaan](documentation/02_setup_and_usage.md).

1. **Clone repository ini:**
   ```bash
   git clone https://github.com/rzkinhfiz/hris-employee-vision-pipeline.git
   cd hris-employee-vision-pipeline
   ```

2. **Siapkan Virtual Environment & Dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Untuk Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Atur Variabel Environment:**
   ```bash
   cp .env.example .env
   ```
   Buka file `.env` dan masukkan Google AI Studio / Gemini API Key Anda.

4. **Siapkan Data (Folders):**
   Taruh direktori dokumen karyawan Anda (misal `336. Dita Auliya`) di dalam direktori `data/source_folders/`.

5. **Jalankan Pipeline Data:**
   ```bash
   python main.py
   ```
   Pantau konsol log Anda (dilengkapi log *progress*, *rate limit warnings*, dan *Success Injection*).

---

## 👤 Profil

Proyek ini dibangun sebagai demonstrasi keahlian di bidang integrasi AI, *Data Processing*, dan Otomasi Skala Perusahaan (Enterprise Automation). Terbuka untuk diskusi mengenai peran *Data Engineer* / *Data Analyst*!

**Dibuat oleh:** Rizki Nurhafizd Achmad (2026)
