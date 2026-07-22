from pydantic import BaseModel, Field
from typing import Optional

class EmployeeDocumentData(BaseModel):
    nama_depan: Optional[str] = Field(None, description="Nama depan karyawan (First Name)")
    nama_belakang: Optional[str] = Field(None, description="Nama belakang karyawan (Last Name). Kosongkan jika tidak ada.")
    nik_ktp: Optional[str] = Field(None, description="Nomor Induk Kependudukan (NIK) 16 digit")
    alamat: Optional[str] = Field(None, description="Alamat lengkap sesuai KTP")
    tempat_lahir: Optional[str] = Field(None, description="Tempat lahir")
    tanggal_lahir: Optional[str] = Field(None, description="Tanggal lahir (Format: YYYY-MM-DD atau sesuai dokumen)")
    jenis_kelamin: Optional[str] = Field(None, description="Jenis kelamin (Laki-laki / Perempuan)")
    status_perkawinan: Optional[str] = Field(None, description="Status Perkawinan (Belum Kawin / Kawin / Cerai)")
    agama: Optional[str] = Field(None, description="Agama")
    npwp: Optional[str] = Field(None, description="Nomor Pokok Wajib Pajak 15 atau 16 digit")
    bpjs_kes: Optional[str] = Field(None, description="Nomor identitas BPJS Kesehatan")
    bpjs_tk: Optional[str] = Field(None, description="Nomor identitas BPJS Ketenagakerjaan")
    rekening_bank: Optional[str] = Field(None, description="Nomor rekening bank beserta nama bank jika tertera")
    status_ptkp: Optional[str] = Field(None, description="Status Perkawinan dan Tanggungan (PTKP) misalnya TK/0, K/1")
    golongan_darah: Optional[str] = Field(None, description="Golongan Darah (A/B/AB/O)")
    catatan_dokumen: Optional[str] = Field(None, description="Catatan jika ada foto dokumen yang buram, terpotong, atau resolusi rendah.")
