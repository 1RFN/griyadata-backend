from pydantic import BaseModel

# Skema untuk Jaye mengirim data Login
class LoginRequest(BaseModel):
    username: str
    password: str
    role: str

# Skema untuk Jaye mengirim data Pesanan Baru (Create/POST)
class OrderCreate(BaseModel):
    nama_pelanggan: str
    product_id: int
    jumlah: int
    total_harga: float
    # Catatan: status_pesanan & metode_pembayaran tidak perlu dimasukkan
    # karena kita sudah set otomatis ke "Pending" dan "Offline/COD" di models.py

class OrderUpdate(BaseModel):
    status_pesanan: str