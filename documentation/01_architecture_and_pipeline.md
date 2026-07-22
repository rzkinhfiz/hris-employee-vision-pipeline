# Arsitektur & Pipeline (Multi-Modal HRD Data Extractor)

Proyek ini dibangun dengan arsitektur berbasis *pipeline* linear yang modular dan tanpa persentuhan (*stateless/in-memory*) demi keamanan privasi data karyawan. Sistem ini tidak pernah mengunggah data mentah KTP/dokumen ke server manapun (GCS/Drive), melainkan memprosesnya murni sebagai *bytes* di memori RAM dan mengirimkannya langsung ke Vertex AI / Google Gemini API.

## Struktur Modul Utama

Arsitektur sistem dibagi menjadi 5 komponen (*phases*) utama:

1. **`src/config.py` (Core Config & Initialization)**
   - Bertanggung jawab memuat seluruh variabel *environment* (seperti `GEMINI_API_KEY`) dari `.env`.
   - Mengatur secara otomatis (*fail-safe*) pembentukan struktur folder esensial: `data/source_folders`, `failed_review`, dan template awal.

2. **`src/folder_scanner.py` (Folder Scanner Module)**
   - Pemindai lokal berkecepatan tinggi memanfaatkan `os.scandir`.
   - Menerapkan **Graceful Degradation**:
     - Jika struktur nama folder karyawan sesuai standar `[ID]. [Nama]`, sistem membaginya dengan Regex.
     - Jika tidak standar, seluruh string teks menjadi "Nama" dan ID dicap "UNKNOWN".
     - Jika folder kosong, sistem tidak *crash*, melainkan merespons dengan array file yang kosong.

3. **`src/schema.py` (Pydantic Schema Definition)**
   - Wadah struktur data ketat (*Strict Output Validation*) yang memaksa AI merespons dengan JSON terstruktur.
   - Field mencakup: `nama_depan`, `nama_belakang`, `nik_ktp`, `alamat`, `tempat_lahir`, `tanggal_lahir`, `jenis_kelamin`, `status_perkawinan`, `agama`, `npwp`, `bpjs_kes`, `bpjs_tk`, `rekening_bank`, `status_ptkp`, `golongan_darah`, dan `catatan_dokumen`.

4. **`src/vision_extractor.py` (Vertex AI Core / AI Assistant)**
   - Inti kecerdasan buatan berbasis `google-genai`.
   - **Two-Layer Detection Mechanism**:
     - **Lapis 1 (System-Level)**: Mengamankan file rusak/corrupt agar *looping* karyawan tetap berjalan meski satu gambar rusak.
     - **Lapis 2 (AI-Level)**: Menginstruksikan AI menjadi asisten administratif anti-halusinasi. Jika teks blur, AI tidak akan menebak, melainkan mengembalikan nilai *null* dan mendaftarkan alasan blur di field `catatan_dokumen`.

5. **`src/excel_manager.py` (Explicit Excel Mapping)**
   - Bertanggung jawab menyuntikkan data hasil AI ke `Template saja.xlsx` (khususnya *sheet* `"Inject"`).
   - Menghindari pendekatan massal Pandas dan beralih ke *Explicit Column Mapping* (Pemetaan Sel Eksplisit).
   - Menguasai 75 kolom penuh. Data yang ditarik AI diletakkan persis pada kolom yang ditargetkan (misal Kolom 7 untuk NIK), dan sisanya di-inisialisasi ulang sebagai _string_ kosong agar terhindar dari sampah data peninggalan template. Kolom ke-76 dialokasikan untuk Catatan Error/Buram.

6. **`main.py` (Orchestration & Error Handling)**
   - Menggabungkan seluruh alur dengan *graceful error catching*. 
   - Kegagalan 1 karyawan tidak akan menghentikan ekstraksi karyawan lainnya.
   - Menggunakan jeda waktu (`time.sleep`) yang diatur di `.env` demi menghindari *Rate Limit* dari layanan Google API.
