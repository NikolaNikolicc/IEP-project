from datetime import timedelta
import os

databaseUrl = os.environ["DATABASE_URL"]

class Configuration():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/store"
    # SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@localhost:3307/store"
    # definisemo predefinisanu klasnu promenljivu:
    # tip_baze_koju_koristimo://user:password@host[:port]/ime_tabelice
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours = 1)
    # JWT_REFRESH_TOKEN_EXPIRES = timedelta(days = 30)
