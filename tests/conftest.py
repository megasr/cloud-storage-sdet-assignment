import pytest
import requests
import os
import tempfile

# Base URL
BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session")
def base_url():

    return BASE_URL

#uploaded file_ids for cleanup after tests.
@pytest.fixture
def cleanup_lst():

    file_ids = []
    yield file_ids
    for file_id in file_ids:
        try:
            requests.delete(f"{BASE_URL}/files/{file_id}")
        except Exception as e:
            print(f"Cleanup error while deleting file {file_id}: {e}")

#Factory fixture to generate files of specific size and name on disk.
@pytest.fixture
def generate_file():

    created_files = []

    def _create(filename: str, size_in_mb: float = 1, content_prefix: bytes = b"test"):
        file_path = os.path.join(tempfile.gettempdir(), filename)  #cross‑platform safe temporary file paths
        with open(file_path, "wb") as f:
            f.write(content_prefix)
            remaining = int(size_in_mb * 1024 * 1024) - len(content_prefix)
            if remaining > 0:
                if size_in_mb > 100:
                    f.seek(remaining, 1)
                    f.write(b'\0')
                else:
                    f.write(b"0" * remaining)
        created_files.append(file_path)
        return file_path

    yield _create
    for path in created_files:
        if os.path.exists(path):
            os.remove(path)

#fixture to upload a file and return  file_id
@pytest.fixture
def upload_file(base_url, cleanup_lst, generate_file):
    def _upload(filename: str = "test.txt", size_mb: float = 1):
        path = generate_file(filename, size_mb)
        with open(path, "rb") as f:
            response = requests.post(f"{base_url}/files", files={"file": (filename, f)})

        if response.status_code == 201:
            data = response.json()
            file_id = data.get("file_id")  # match API contract
            if file_id:
                cleanup_lst.append(file_id)
            return file_id, response
        return None, response

    return _upload

#admin credentials

@pytest.fixture(scope="session")
def admin_cred():
    token = os.getenv("ADMIN_ID", "Admin Password")
    return {"Authorization": f"Bearer {token}"}
