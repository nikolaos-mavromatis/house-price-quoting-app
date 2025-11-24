"""Application settings and environment configurations."""

from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
