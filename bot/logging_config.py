"""
Centralised logging configuration.
- DEBUG+ goes to trading_bot.log (rotating, 5 MB × 3 backups)
- INFO+  goes to the console (clean, no timestamps)
"""

import logging
import logging.handlers
import os

LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "trading_bot.log")
_configured = False


def setup_logging(level: int = logging.DEBUG) -> None:
    global _configured
    if _configured:
        return
    _configured = True

    root = logging.getLogger()
    root.setLevel(level)

    # --- File handler (rotating) ---
    fh = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    # --- Console handler ---
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    root.addHandler(fh)
    root.addHandler(ch)


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)
