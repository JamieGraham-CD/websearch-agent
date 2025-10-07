import json
import re
import pandas as pd # type: ignore
from collections import defaultdict
from google.cloud import storage # type: ignore
from Workflow.google_storage_workflow import read_csv_from_gcs
from google.cloud import secretmanager # type: ignore
import os
from typing import Tuple, Any
import numpy as np
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import List


def setup_logger(
    name: str = "app_logger",
    log_file: str = "logging/app.log",
    level: int = logging.INFO,
    max_bytes: int = 10_000_000,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up a logger that writes to both console and a rotating log file.

    Args:
        name (str): Name of the logger.
        log_file (str): File path to log to.
        level (int): Logging level (e.g., logging.INFO).
        max_bytes (int): Max size in bytes before rotating.
        backup_count (int): Number of backup files to keep.

    Returns:
        logging.Logger: Configured logger instance.
    """
    os.makedirs("logging", exist_ok=True)  # Ensure the logging directory exists
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    # File handler
    file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Avoid duplicate handlers on multiple calls
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger



def upload_log_to_gcs(bucket_name: str, destination_blob_path: str, log_file: str) -> None:
    """
    Uploads the log file to a GCP bucket.

    Args:
        bucket_name (str): Name of the GCS bucket.
        destination_blob_path (str): Path in the bucket where the log should go.
        log_file (str): Local path to the log file.
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_path)
        blob.upload_from_filename(log_file)
        print(f"✅ Uploaded log to gs://{bucket_name}/{destination_blob_path}")
    except Exception as e:
        print(f"❌ Failed to upload log: {e}")

def list_filenames(folder_path: str) -> List[str]:
    """
    Return a list of filenames in the specified local folder.

    Args:
        folder_path: Path to the folder to list.

    Returns:
        A list of filenames (not including directory names).

    Raises:
        ValueError: If the provided path is not a directory.
    """
    path = Path(folder_path)
    if not path.is_dir():
        raise ValueError(f"'{folder_path}' is not a valid directory.")

    # List only files (skip subdirectories)
    return [item.name for item in path.iterdir() if item.is_file()]