from flask import Flask 

from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from logging_config import configure_logging


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
configure_logging()

from app.model import voucher
from app.model import record_redemption


from app import routes