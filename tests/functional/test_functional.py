import requests

#file operation test_cases
def test_tc01_upload_file(upload_file):
    file_id, response = upload_file("fake_file.txt", size_mb=1)
    assert response.status_code == 201
    assert file_id is not None
    assert "file_id" in response.json()


def test_t02_download_file(upload_file, base_url):
    file_id, _ = upload_file("1mb_file.txt", size_mb=1)
    resp = requests.get(f"{base_url}/files/{file_id}")
    assert resp.status_code == 200
    assert resp.content.startswith(b"test")


def test_tc03_get_metadata(upload_file, base_url):
    file_id, _ = upload_file("meta_check.txt", size_mb=1)
    resp = requests.get(f"{base_url}/files/{file_id}/metadata")
    assert resp.status_code == 200
    metadata = resp.json()
    assert metadata["file_id"] == file_id
    assert "size" in metadata
    assert metadata["size"] > 0


def test_tc04_delete_file(upload_file, base_url):
    file_id, _ = upload_file("don't_delete_me.txt", size_mb=1)
    resp = requests.delete(f"{base_url}/files/{file_id}")
    assert resp.status_code in [200, 204]
    r = requests.get(f"{base_url}/files/{file_id}")
    assert r.status_code == 404



def test_tc05_upload_file_with_malicious_name(base_url):
    files = {"file": ("../../etc/passwd", b"x" * 1048576)}  # 1MB content
    r = requests.post(f"{base_url}/files", files=files)
    assert r.status_code == 400, f"Unexpected success: {r.json()}"


#admin operation test cases

def test_tc06_trigger_manual_tiering(base_url, admin_cred):
    response = requests.post(f"{base_url}/admin/tiering/run", headers=admin_cred)
    assert response.status_code in [200, 202]
    data = response.json()
    assert "status" in data

def test_tc07_get_usage_stats(base_url, admin_cred):
    response = requests.get(f"{base_url}/admin/stats", headers=admin_cred)
    assert response.status_code == 200
    stats = response.json()
    assert "totalFiles" in stats
    assert "totalStorageUsed" in stats




