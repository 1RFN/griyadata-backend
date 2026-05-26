import sys
import requests
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GriyaData - Login System")
        self.setFixedSize(400, 500) # Ukuran jendela tetap agar proporsional
        
        # Alamat API FastAPI Lokal kamu (Nanti bisa diganti URL Render kalau sudah di-deploy)
        self.API_URL = "http://127.0.0.1:8000/api/login"
        
        self.initUI()
        
    def initUI(self):
        # Widget Utama dan Layout Pusat
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(15)
        
        # --- Bagian Header/Judul ---
        title_label = QLabel("GriyaData", self)
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2C3E50;")
        
        subtitle_label = QLabel("Aplikasi Manajemen Toko Furniture", self)
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #7F8C8D;")
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addSpacing(20) # Memberi jarak vertikal
        
        # --- Form Input Username ---
        username_label = QLabel("Username", self)
        username_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Masukkan username Anda")
        self.username_input.setStyleSheet(self.input_style())
        
        main_layout.addWidget(username_label)
        main_layout.addWidget(self.username_input)
        
        # --- Form Input Password ---
        password_label = QLabel("Password", self)
        password_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Masukkan password Anda")
        self.password_input.setEchoMode(QLineEdit.Password) # Menyembunyikan input password
        self.password_input.setStyleSheet(self.input_style())
        
        main_layout.addWidget(password_label)
        main_layout.addWidget(self.password_input)
        main_layout.addSpacing(10)
        
        # --- Tombol Login ---
        self.login_button = QPushButton("Masuk Ke Sistem", self)
        self.login_button.setFont(QFont("Arial", 11, QFont.Bold))
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #2980B9;
                color: white;
                border-radius: 6px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #3498DB;
            }
            QPushButton:pressed {
                background-color: #1F618D;
            }
        """)
        # Menghubungkan klik tombol dengan fungsi proses login
        self.login_button.clicked.connect(self.handle_login)
        main_layout.addWidget(self.login_button)
        
        main_layout.addStretch() # Mendorong semua elemen ke atas agar rapi
        
    def input_style(self):
        # Desain CSS untuk form input agar terlihat modern
        return """
            QLineEdit {
                border: 2px solid #BDC3C7;
                border-radius: 6px;
                padding: 10px;
                font-size: 11px;
                background-color: #FAFAFA;
            }
            QLineEdit:focus {
                border: 2px solid #2980B9;
                background-color: white;
            }
        """
        
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # Validasi dasar agar input tidak kosong
        if not username or not password:
            QMessageBox.warning(self, "Peringatan", "Username dan Password wajib diisi!")
            return
            
        # Data yang akan dikirim ke API FastAPI
        payload = {
            "username": username,
            "password": password
        }
        
        try:
            # Mengirim permintaan POST ke backend FastAPI
            response = requests.post(self.API_URL, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                QMessageBox.information(self, "Sukses", f"Selamat Datang, {username}!\nLogin berhasil.")
                # Di sini nanti Jaye tinggal menyambungkan untuk membuka Jendela Dashboard Utama
                # self.open_dashboard() 
                # self.close()
            else:
                # Mengambil pesan error dari HTTPException milik FastAPI
                error_detail = response.json().get("detail", "Login gagal.")
                QMessageBox.critical(self, "Gagal", error_detail)
                
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Error Koneksi", "Gagal terhubung ke server API. Pastikan FastAPI sudah dinyalakan!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())