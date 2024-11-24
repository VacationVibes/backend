import logging

# database configuration
DATABASE_URL = "postgresql+asyncpg://username:password@localhost/vacation-vibes"

# JWT configuration
SECRET_KEY = "supersecretkey"
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_TIME = 5_256_000  # 10 years (expiry time in minutes)

# logging configuration
LOGGING_LEVEL = logging.DEBUG
