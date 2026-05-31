import os
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import models
from database import engine, get_db
import schemas

app = FastAPI(
    title="API GriyaData",
    description="API untuk Aplikasi Manajemen Penjualan Miniatur"
)

# Buat folder uploads untuk jaga-jaga
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# --- ROOT ---
@app.get("/")
def read_root():
    return {"message": "API GriyaData berhasil menyala di Safe Mode!"}

# --- AUTH ---
@app.post("/api/login")
def login_admin(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    
    if user and user.password == request.password:
        return {
            "status": "success",
            "message": f"Login berhasil sebagai {user.role}",
            "token": "token_rahasia_123",
            "role": user.role # Beritahu frontend role aslinya apa
        }
    raise HTTPException(status_code=400, detail="Username atau password salah!")

# --- PRODUCTS ---
@app.get("/api/products")
def get_all_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return {"total_data": len(products), "data": products}

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
    return {"message": "Produk berhasil ditambahkan", "data": db_product}

@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    db.delete(product)
    db.commit()
    return {"message": "Produk dihapus"}

# --- ORDERS ---
@app.post("/api/orders/bulk")
def create_bulk_orders(bulk_data: schemas.BulkOrderCreate, db: Session = Depends(get_db)):
    inserted = 0
    errors = []
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
    db.commit()
    return {
        "message": "Bulk insert selesai",
        "inserted": inserted,
        "skipped": len(bulk_data.orders) - inserted,
        "errors": errors
    }