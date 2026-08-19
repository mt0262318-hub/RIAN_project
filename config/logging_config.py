import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def configure_logging() -> None:
    """R.I.A.N. Assistant ke liye global logging setup karta hai."""
    
    # Logs folder banaye agar wo nahi hai
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Main logger create karein
    logger = logging.getLogger("rian")
    logger.setLevel(logging.DEBUG) # Root par sab kuch catch karega

    # Message ka format kaisa dikhega (Date | Name | Level | Message)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. File Handler (Background mein har detail save karne ke liye)
    # Max 5MB ki file banayega, uske baad nayi file bana dega (taaki PC na bhare)
    file_handler = RotatingFileHandler(
        "logs/app.log", maxBytes=5*1024*1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # 2. Console Handler (Terminal par sirf zaroori INFO dikhane ke liye)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Handlers ko logger mein add karein (check karke taaki double na ho jaye)
    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

def get_logger(name: str) -> logging.Logger:
    """Kisi specific file ke liye logger nikalne ka shortcut."""
    return logging.getLogger(name)