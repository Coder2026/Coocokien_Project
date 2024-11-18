from app import app
from app import db
from app.model.record_redemption import Record_Redemption

def add_records():
    try:
        # Siapkan data
        data = [
            Record_Redemption(position=0, total_redeemed=0),
            Record_Redemption(position=1, total_redeemed=0),
            Record_Redemption(position=2, total_redeemed=0),
            Record_Redemption(position=3, total_redeemed=0),
            Record_Redemption(position=4, total_redeemed=0),
            Record_Redemption(position=5, total_redeemed=0),
        ]

        # Tambahkan data ke database
        db.session.add_all(data)
        db.session.commit()
        print("Data successfully added.")

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")

if __name__ == "__main__":
    # Pastikan fungsi berjalan di dalam app context
    with app.app_context():
        add_records()