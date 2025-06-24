
import hashlib
import os
import tarfile

from unstructured.nlp.tokenize import get_nltk_data_dir

### NLTK DEPENDENCIES ###
NLTK_DATA_FILENAME = "nltk_data_3.8.2.tar.gz"
NLTK_DATA_SHA256 = "ba2ca627c8fb1f1458c15d5a476377a5b664c19deeb99fd088ebf83e140c1663"

nltk_data_dir = get_nltk_data_dir()

if nltk_data_dir is None:
    raise OSError("NLTK data directory does not exist or is not writable.")

# Check if the path ends with "nltk_data" and remove it if it does
if nltk_data_dir.endswith("nltk_data"):
    nltk_data_dir = os.path.dirname(nltk_data_dir)

def sha256_checksum(filename: str, block_size: int = 65536):
    sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            sha256.update(block)
    return sha256.hexdigest()

tgz_file_path = os.path.join(".", NLTK_DATA_FILENAME)

file_hash = sha256_checksum(tgz_file_path)
if file_hash != NLTK_DATA_SHA256:
    os.remove(tgz_file_path)
    raise ValueError(f"SHA-256 mismatch: expected {NLTK_DATA_SHA256}, got {file_hash}")

# Extract the contents
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir)

with tarfile.open(tgz_file_path, "r:gz") as tar:
    tar.extractall(path=nltk_data_dir)
