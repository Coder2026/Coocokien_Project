from app import db
import string
import secrets

class Voucher(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.Boolean,nullable = False)
    discount_status = db.Column(db.Boolean,nullable = False)

    def __repr__(self):
                return '<User {}>'.format(self.id)
   
    @staticmethod
    def generate_unique_code(length=8):
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(secrets.choice(characters) for _ in range(length))
            # Pastikan kode unik dengan memeriksa di database
            if not Voucher.query.filter_by(code=code).first():
                return code
            

