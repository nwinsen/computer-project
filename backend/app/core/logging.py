"""Centralized structured JSON logging configuration.

TODO:
1. Import logging, os, sys, RotatingFileHandler from logging.handlers, and jsonlogger from pythonjsonlogger
2. Read LOG_FILE from os.getenv("LOG_FILE_PATH", "/var/log/lolapp/app.log")
3. Read LOG_LEVEL from os.getenv("LOG_LEVEL", "INFO").upper()
4. Create _configure_logging() function that:
   - Creates a JsonFormatter with format "%(asctime)s %(name)s %(levelname)s %(message)s"
   - Gets root logger and sets level to LOG_LEVEL
   - Adds StreamHandler to stdout with JSON formatter
   - If LOG_FILE is set:
     - Create parent directories with os.makedirs(..., exist_ok=True)
     - Add RotatingFileHandler with maxBytes=50_000_000, backupCount=5, JSON formatter
5. Create get_logger(name: str) function that returns logging.getLogger(name)
6. Call _configure_logging() at module import time (side-effect)
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger

LOG_PATH = os.getenv("LOG_FILE_PATH", "/var/log/lolapp/app.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "/var/log/lolapp/app.log")

# TODO: Implement according to docs/observability.md "Structured Logging" section
