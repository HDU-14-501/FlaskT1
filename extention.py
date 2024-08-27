from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pymysql

pymysql.install_as_MySQLdb()

db = SQLAlchemy()
cors = CORS()
