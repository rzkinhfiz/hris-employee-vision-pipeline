import time
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import Optional

# Impor konfigurasi dari config.py
from src.config import GEMINI_API_KEY, GEMINI_MODEL_NAME

# 1. Definisikan Schema menggunakan Pydantic (Pendekatan Hybrid: Deskripsi Bahasa Indonesia)
class ContractData(BaseModel):
    Nama_File_ID: str = Field(description="Nama asli dari file PDF")
    Jenis_Dokumen: Optional[str] = Field(description="Klasifikasi dokumen, misal: Perjanjian Kerja, NDA, Kontrak Proyek")
    Pihak_Pertama: Optional[str] = Field(description="Nama perusahaan atau individu dari pihak pertama")
    Pihak_Kedua: Optional[str] = Field(description="Nama klien, vendor, atau individu dari pihak kedua")
    Nilai_Kontrak_IDR: int = Field(description="Nominal uang kontrak dalam Rupiah murni sebagai integer. Jika tidak ada, kembalikan 0.")
    Tanggal_Mulai: Optional[str] = Field(description="Tanggal efektif atau mulai kontrak (Format YYYY-MM-DD)")
    Tanggal_Selesai: Optional[str] = Field(description="Tanggal berakhirnya kontrak (Format YYYY-MM-DD)")
    Ruang_Lingkup_Proyek: Optional[str] = Field(description="Ringkasan singkat mengenai objek atau pekerjaan proyek")
    Klausul_Penting_or_Penalti: Optional[str] = Field(description="Catatan khusus, syarat, atau denda penalti")
    Status_Ekstraksi: str = Field(description="Nilai harus selalu 'Success' untuk respon JSON yang normal")


# 2. Fungsi Utama Ekstraksi
def extract_contract_info(text: str, filename: str = "Unknown") -> dict:
    """
    Memanggil Gemini API untuk mengekstrak informasi entitas dari teks dokumen.
    """
    if not GEMINI_API_KEY:
        raise ValueError("API Key Gemini tidak ditemukan. Periksa file .env Anda.")

    # Inisialisasi client dari SDK google-genai yang baru
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # System Prompt Murni Bahasa Inggris (Hybrid Approach)
    system_prompt = """You are an expert legal assistant and contract analyst. 
Your task is to carefully read the provided contract text and extract key business entities exactly as described in the schema.
Analyze the context to identify parties, contract values, and dates. Ensure maximum accuracy. 
If an information is completely missing or cannot be inferred from the text, strictly follow the default value rules specified in the schema. 
Do NOT invent or hallucinate information. 
The input text might be noisy OCR text. Focus on finding the relevant details and structuring them."""

    full_prompt = f"{system_prompt}\n\nDocument Filename: {filename}\n\nContract Text:\n{text}"
    
    # 3. Exponential Backoff Retry Logic
    max_retries = 3
    delays = [2, 4, 8]  # Waktu tunggu bertingkat dalam detik
    
    for attempt in range(max_retries):
        try:
            # Memanggil API dengan sintaks google-genai dan variabel model
            response = client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ContractData,
                    temperature=0.1,  # Temperature rendah agar ekstraksi data sangat faktual
                )
            )
            
            # API mengembalikan string berbentuk JSON, kita parse menjadi Python Dictionary
            extracted_data = json.loads(response.text)
            
            # Memastikan Nama_File dipaksa sesuai argumen agar tidak di-hallucinate
            extracted_data["Nama_File_ID"] = filename
            
            return extracted_data
            
        except Exception as e:
            error_str = str(e)
            # Logika khusus untuk penanganan Rate Limit (429 / Kuota)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "Quota exceeded" in error_str:
                wait_time = 60
                print(f"[Warning] API Rate Limit (Percobaan {attempt+1}/{max_retries}). Menunggu {wait_time}s agar kuota di-reset...")
            else:
                wait_time = delays[attempt]
                print(f"[Warning] Gemini API Error (Percobaan {attempt+1}/{max_retries}). Menunggu {wait_time}s... Error: {e}")
                
            if attempt < max_retries - 1:
                time.sleep(wait_time)
            else:
                # Jika sudah retry maksimal dan gagal, lemparkan error
                raise Exception(f"API Error setelah {max_retries}x percobaan: {error_str}")


# 4. Blok Pengujian (Testing)
if __name__ == "__main__":
    print("=== Testing Modul AI Extractor (src/ai_extractor.py) dengan google-genai ===")
    
    dummy_text = """
    PERJANJIAN KERJASAMA PEMBUATAN APLIKASI
    
    Pada hari ini, Senin tanggal 1 Januari 2024, bertempat di Jakarta, telah disepakati perjanjian kerjasama antara:
    1. PT Maju Jaya Tekno, selanjutnya disebut sebagai PIHAK PERTAMA.
    2. Bapak Budi Santoso (Freelancer), selanjutnya disebut sebagai PIHAK KEDUA.
    
    PIHAK PERTAMA sepakat menunjuk PIHAK KEDUA untuk membangun Sistem ERP. 
    Total nilai proyek ini adalah Rp 150.000.000 (Seratus lima puluh juta rupiah).
    Proyek dimulai pada 10 Januari 2024 dan wajib diselesaikan selambatnya pada 10 Mei 2024.
    Jika terjadi keterlambatan, PIHAK KEDUA akan dikenakan denda keterlambatan sebesar 1% dari nilai kontrak per minggu keterlambatan.
    """
    
    print("Teks Dummy:")
    print(dummy_text.strip())
    print("-" * 40)
    print("Memanggil Gemini API (Structured Output)...")
    
    try:
        start_time = time.time()
        result = extract_contract_info(dummy_text, filename="Kontrak_ERP_Budi.pdf")
        elapsed = time.time() - start_time
        
        print(f"Status: Berhasil dalam {elapsed:.2f} detik!\n")
        print("Hasil Ekstraksi (Format JSON):")
        print(json.dumps(result, indent=4))
        
        # Validasi apakah default value (0 untuk IDR) berjalan jika tidak ada nominal
        print("\n--- Testing Penanganan Default Value (Tanpa Nilai Kontrak) ---")
        text_without_money = "Surat perjanjian NDA antara Anto dan Budi. Tidak ada pembayaran."
        result2 = extract_contract_info(text_without_money, filename="NDA_Anto.pdf")
        print(f"Nilai Kontrak (Seharusnya 0): {result2.get('Nilai_Kontrak_IDR')}")
        
    except Exception as e:
        print(f"Error Eksekusi: {e}")
