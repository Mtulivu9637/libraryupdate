import requests
import os
from urllib.parse import urlparse
import uuid
import hashlib
from tqdm import tqdm

# Directory to store images
SAVE_DIR = "Fetched_Images"
os.makedirs(SAVE_DIR, exist_ok=True)

# Keep track of downloaded hashes
downloaded_hashes = set()

def get_file_hash(content):
    """Return MD5 hash of file content to detect duplicates."""
    return hashlib.md5(content).hexdigest()

def fetch_image(url, max_size=10 * 1024 * 1024):  # 10 MB limit
    try:
        response = requests.get(url, timeout=10, stream=True)
        response.raise_for_status()

        # Check important headers
        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            print(f"✗ Skipped {url} (Not an image, Content-Type: {content_type})")
            return

        content_length = response.headers.get("Content-Length")
        total_size = int(content_length) if content_length else None

        if total_size and total_size > max_size:
            print(f"✗ Skipped {url} (File too large: {total_size/1024/1024:.2f} MB)")
            return

        # Extract filename or generate one
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path) or f"image_{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(SAVE_DIR, filename)

        # Stream download with progress bar
        chunk_size = 1024
        content = bytearray()
        with open(filepath, "wb") as f, tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            desc=filename,
            ascii=True,
        ) as bar:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:  # filter out keep-alive chunks
                    content.extend(chunk)
                    f.write(chunk)
                    bar.update(len(chunk))

        # File size safety check
        if len(content) > max_size:
            print(f"✗ Skipped {url} (Downloaded
