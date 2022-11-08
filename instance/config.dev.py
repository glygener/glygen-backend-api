
DEBUG = True
TESTING = False

SERVER = "dev"
DB_HOST = "mongodb://localhost:27017"
DB_NAME = "glydb"
DB_USERNAME = "glydbadmin"
DB_PASSWORD = "glydbpass"
DATA_PATH = "/Volumes/disk2/data/shared/glygen"
LOG_PATH = "/Volumes/disk2/data/shared/glygen/logs"
MAX_CONTENT_LENGTH = 16 * 1000 * 1000

TOTP_INTERVAL = 3600

#MAIL_SERVER = "smtp.gmail.com"
#MAIL_PORT = 465
#MAIL_USE_TLS = False
#MAIL_USE_SSL = True
#MAIL_USERNAME = ""
#MAIL_PASSWORD = ""

MAIL_SERVER = "127.17.0.1"
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_SENDER = "no-reply@glygen.gwu.edu"
MAIL_USERNAME = None
MAIL_PASSWORD = None



SECRET_KEY = "9012b212ce1d1184eb764492727ba34ec30e2c98f64406e1ef6a967816011e85"
JWT_SECRET_KEY = "9012b212ce1d1184eb764492727ba34ec30e2c98f64406e1ef6a967816011e85"
SESSION_COOKIE_SECURE = True
JWT_TOKEN_LOCATION = ['cookies']
JWT_COOKIE_SECURE = False
JWT_ACCESS_COOKIE_PATH = '/'
JWT_REFRESH_COOKIE_PATH = '/'
JWT_COOKIE_CSRF_PROTECT = True
JWT_CSRF_IN_COOKIES = False

    


