from datetime import timedelta
import os

# databaseUrl = os.environ["DATABASE_URL"]

class Configuration():
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost/authentication"
    # definisemo predefinisanu klasnu promenljivu:
    # tip_baze_koju_koristimo://user:password@host[:port]/ime_tabelice
    # JWT_SECRET_KEY = "JWT_SECRET_KEY"
    # JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes = 15)
    # JWT_REFRESH_TOKEN_EXPIRES = timedelta(days = 30)