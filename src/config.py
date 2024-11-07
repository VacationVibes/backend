import logging

# database configuration
DATABASE_URL = "postgresql+asyncpg://username:password@localhost/vacation-vibes"

# JWT configuration
SECRET_KEY = "supersecretkey"
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_TIME = 180  # expiry time in minutes

# logging configuration
LOGGING_LEVEL = logging.DEBUG
