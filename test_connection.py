from flask_sqlalchemy import SQLAlchemy

# Database URL Anda
DATABASE_URL = "mysql+pymysql://root:MasterAdnan@123@127.0.0.1:3306/voucher_code"

# Inisialisasi SQLAlchemy tanpa Flask app
db = SQLAlchemy()

try:
    # Bind engine langsung ke db
    db.engine = db.create_engine(DATABASE_URL)
    connection = db.engine.connect()
    print("Koneksi berhasil ke database!")
    connection.close()
except Exception as e:
    print(f"Error: {e}")