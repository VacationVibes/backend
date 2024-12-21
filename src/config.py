import logging
import os

# database configuration
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME", "username")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_NAME = os.getenv("DATABASE_NAME", "vacation-vibes")
DATABASE_URL = f"postgresql+asyncpg://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"

# JWT configuration
SECRET_KEY = "supersecretkey"
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_TIME = 5_256_000  # 10 years (expiry time in minutes)

# logging configuration
LOGGING_LEVEL = logging.DEBUG
