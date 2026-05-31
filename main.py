import os
import shutil
from fastapi import FastAPI, Depends, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
import models
from database import engine, get_db
import schemas 


app = FastAPI(title="API GriyaData", description="API untuk Aplikasi Manajemen Penjualan Toko Furniture")

# Membuat folder 'uploads' secara otomatis jika belum ada di laptopmu/server
os.makedirs("uploads", exist_ok=True)

# Membuka akses folder 'uploads' ke publik. 
# Jika ada file bernama 'bukti.png', Jaye bisa melihatnya di http://127.0.0.1:8000/uploads/bukti.png
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def read_root():
    return {"message": "Selamat! API GriyaData berhasil terhubung ke Database Supabase."}

@app.post("/api/login")
def login_admin(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    # 1. Cari user di database berdasarkan username yang diinput
    user = db.query(models.User).filter(models.User.username == request.username).first()
    
    # 2. Validasi apakah user ditemukan, password cocok, dan role sesuai
    if user and user.password == request.password and user.role == request.role:
        return {
            "status": "success",
            "message": f"Login berhasil sebagai {user.role}",
            "token": "token_rahasia_griyadata_123",
            "role": user.role
        }
    
    # 3. Jika salah satu data tidak cocok, kembalikan error status 400
    raise HTTPException(status_code=400, detail="Username, password, atau role salah!")

# API untuk MENCATAT pesanan baru (Create)
@app.post("/api/orders")
def create_order(order_data: schemas.OrderCreate, db: Session = Depends(get_db)):
    # 1. Bungkus data yang dikirim menjadi format model tabel Order
    db_order = models.Order(
        nama_pelanggan=order_data.nama_pelanggan,
        product_id=order_data.product_id,
        jumlah=order_data.jumlah,
        total_harga=order_data.total_harga
        # Ingat: status_pesanan dan metode_pembayaran akan otomatis
        # terisi "Pending" dan "Offline/COD" sesuai pengaturan di models.py
    )
    
    # 2. Tambahkan ke sesi database dan simpan permanen
    db.add(db_order)
    db.commit()
    db.refresh(db_order) # Mengambil ID unik yang baru saja dibuat oleh Supabase
    
    return {
        "message": "Berhasil mencatat pesanan baru!",
        "data": db_order
    }

# API untuk MELIHAT semua daftar pesanan (Read)
@app.get("/api/orders")
def get_all_orders(db: Session = Depends(get_db)):
    # Mengambil seluruh baris data dari tabel orders
    orders = db.query(models.Order).all()
    return {
        "total_data": len(orders),
        "data": orders
    }

# API untuk MEMPERBARUI status pesanan (Update)
@app.put("/api/orders/{order_id}")
def update_order_status(order_id: int, request: schemas.OrderUpdate, db: Session = Depends(get_db)):
    # 1. Cari pesanan berdasarkan ID
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    
    # 2. Jika ID tidak ada di database, kembalikan pesan error 404
    if not order:
        raise HTTPException(status_code=404, detail="Pesanan tidak ditemukan")
    
    # 3. Ubah statusnya dan simpan kembali
    order.status_pesanan = request.status_pesanan
    db.commit()
    db.refresh(order)
    
    return {
        "message": f"Status pesanan ID {order_id} berhasil diperbarui menjadi {request.status_pesanan}",
        "data": order
    }

# API untuk MENGHAPUS pesanan (Delete)
@app.delete("/api/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    # 1. Cari pesanan berdasarkan ID
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Pesanan tidak ditemukan")
    
    # 2. Hapus data dari database
    db.delete(order)
    db.commit()
    
    return {
        "message": f"Pesanan ID {order_id} berhasil dihapus dari sistem."
    }

# API untuk MENGUNGGAH file (Upload)
@app.post("/api/upload")
def upload_file(file: UploadFile = File(...)):
    # 1. Tentukan lokasi penyimpanan file beserta nama filenya
    file_location = f"uploads/{file.filename}"
    
    # 2. Simpan file secara fisik ke dalam folder uploads
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 3. Kembalikan data path agar bisa disimpan Jaye ke database jika diperlukan
    return {
        "message": "File berhasil diunggah!",
        "filename": file.filename,
        "file_path": f"/uploads/{file.filename}" 
    }

# ==========================================
# TAMBAHAN API UNTUK PRODUK & BULK IMPORT 
# ==========================================

# 1. GET /api/products — Ambil semua produk (Untuk Dropdown Jaye)
@app.get("/api/products")
def get_all_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return {
        "total_data": len(products),
        "data": products
    }

# 2. POST /api/products — Tambah produk baru
@app.post("/api/products")
def create_product(product_data: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(
        nama_barang=product_data.nama_barang,
        kategori=product_data.kategori,
        harga=product_data.harga
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return {
        "message": "Produk berhasil ditambahkan!",
        "data": db_product
    }

# 3. DELETE /api/products/{id} — Hapus produk
@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    
    db.delete(product)
    db.commit()
    return {"message": f"Produk ID {product_id} berhasil dihapus"}

# 4. POST /api/orders/bulk — Insert banyak pesanan sekaligus (Import CSV/Excel)
@app.post("/api/orders/bulk")
def create_bulk_orders(bulk_data: schemas.BulkOrderCreate, db: Session = Depends(get_db)):
    inserted = 0
    errors = []
    
    # Memasukkan data satu per satu ke dalam antrean database
    for order_data in bulk_data.orders:
        try:
            db_order = models.Order(
                nama_pelanggan=order_data.nama_pelanggan,
                product_id=order_data.product_id,
                jumlah=order_data.jumlah,
                total_harga=order_data.total_harga
            )
            db.add(db_order)
            inserted += 1
        except Exception as e:
            errors.append(str(e))
    
    # Menyimpan semuanya sekaligus ke database (jauh lebih cepat dan aman)
    db.commit() 
    
    return {
        "message": "Bulk insert selesai",
        "inserted": inserted,
        "skipped": len(bulk_data.orders) - inserted,
        "errors": errors
    }