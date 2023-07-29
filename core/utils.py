import hashlib
import zipfile
import os
from datetime import datetime

def getFileSha256(filename):
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

def getDateStr():
    return datetime.now().strftime('%Y%m%d')



def zipFolder(folder_path, output_zip_path):
    with zipfile.ZipFile(output_zip_path, 'w') as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Calculate the relative path for the ZIP
                relative_path = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, relative_path)

