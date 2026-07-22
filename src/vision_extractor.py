import os
import time
import mimetypes
from google import genai
from google.genai import types

from src.schema import EmployeeDocumentData
from src.config import GEMINI_API_KEY, GEMINI_MODEL_NAME

# Inisialisasi klien Gemini API (AI Studio)
client = genai.Client(api_key=GEMINI_API_KEY)

def extract_employee_data(file_paths: list[str]) -> tuple[dict, str]:
    """
    Mengekstrak data dari sejumlah file gambar/dokumen karyawan (In-Memory Bytes).
    Mengembalikan tuple (data_dict, final_note).
    """
    contents = []
    lapis_1_errors = []

    # Deteksi Lapis 1: Cek file corrupt atau 0-byte secara lokal
    for path in file_paths:
        try:
            # Periksa eksistensi dan jika file kosong (0 bytes)
            if not os.path.exists(path):
                raise FileNotFoundError("File tidak ditemukan.")
            if os.path.getsize(path) == 0:
                raise ValueError("File berukuran 0 bytes (Kosong atau Corrupt).")
                
            # Coba buka file dan baca sebagai bytes
            with open(path, "rb") as f:
                file_bytes = f.read()
                
            # Deteksi tipe MIME
            mime_type, _ = mimetypes.guess_type(path)
            if mime_type is None:
                if path.lower().endswith(".pdf"):
                    mime_type = "application/pdf"
                else:
                    mime_type = "image/jpeg"
                    
            # Gunakan metode Part.from_bytes milik google-genai agar file dikirim in-memory
            contents.append(
                types.Part.from_bytes(
                    data=file_bytes,
                    mime_type=mime_type
                )
            )
        except Exception as e:
            lapis_1_errors.append(f"Gagal membaca '{os.path.basename(path)}': {str(e)}")

    # Jika semua file gagal dibaca Lapis 1, langsung kembalikan error
    if not contents:
        error_msg = "Semua file gagal dimuat."
        if lapis_1_errors:
            error_msg += " Lapis 1 Error: " + " | ".join(lapis_1_errors)
        return {}, error_msg

    # Tambahkan instruksi System Prompt beserta aturan Lapis 2
    prompt = (
        "You are an HR administrative assistant. I will provide you with several images/documents belonging to a single employee. "
        "Cross-reference them and extract the requested fields.\n"
        "PENTING (Deteksi Lapis 2): Jika ada foto yang blur, terpotong, atau resolusi rendah sehingga teks tidak bisa dibaca yakin, "
        "jangan menebak angkanya. Kosongkan nilai field tersebut (null) dan tuliskan alasannya secara rinci pada `catatan_dokumen`."
    )
    
    contents.append(prompt)
    
    max_retries = 3
    result_data = {}
    lapis_2_note = ""
    
    try:
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=GEMINI_MODEL_NAME,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=EmployeeDocumentData,
                    ),
                )
                
                if response.text:
                    import json
                    result_data = json.loads(response.text)
                break
                
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "Quota exceeded" in error_str:
                    wait_time = 60
                    print(f"[API Rate Limit] Menunggu {wait_time}s agar kuota di-reset (Percobaan {attempt+1}/{max_retries})...")
                else:
                    wait_time = 5 * (attempt + 1)
                    print(f"[API Error] Menunggu {wait_time}s... Error: {e} (Percobaan {attempt+1}/{max_retries}).")
                    
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Gagal memanggil API setelah {max_retries}x percobaan: {error_str}")
                    
    except Exception as e:
        lapis_2_note = str(e)

    # Menggabungkan pesan error Lapis 1 dan catatan Lapis 2 (AI)
    final_note = result_data.get("catatan_dokumen", "") or ""
    
    if lapis_1_errors:
        final_prefix = "Lapis 1 Error: " + " | ".join(lapis_1_errors) + "."
        final_note = f"{final_prefix} {final_note}".strip()
        
    if lapis_2_note:
        final_note += f" Lapis 2 Error (API): {lapis_2_note}"
        
    result_data["catatan_dokumen"] = final_note.strip()
    
    return result_data, final_note.strip()
