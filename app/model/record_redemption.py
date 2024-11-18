from app import db


class Record_Redemption(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    position = db.Column(db.Integer,unique = True, nullable = False)
    total_redeemed = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<Record_Redemption(id={self.id}, total_redeemed={self.total_redeemed})>"