from sqlalchemy import create_engine

# Database URL Anda
DATABASE_URL = "mysql+pymysql://root:MasterAdnan@123@127.0.0.1:3306/voucher_code"

def test_connection():
    try:
        # Buat engine langsung
        engine = create_engine(DATABASE_URL)
        connection = engine.connect()
        print("Koneksi berhasil ke database!")
        connection.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_connection()