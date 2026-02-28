import requests

# Edge & Boundary Cases
def test_tc01_upload_no_file(base_url):

    response = requests.post(f"{base_url}/files", files={})
    assert response.status_code in [400, 422]

def test_tc02_upload_zero_byte_file(upload_file, base_url):
    file_id, response = upload_file("emptyfile.txt", size_mb=0)
    # Depending on API design: could be 400 (reject) or 201 (accept empty file)
    assert response.status_code in [400, 201]
    if response.status_code == 201:
        # Verify metadata shows size = 0
        r = requests.get(f"{base_url}/files/{file_id}/metadata")
        assert r.status_code == 200
        assert r.json()["size"] == 0


def test_tc03_upload_almost_one_mb_file(upload_file, base_url):
    file_id, response = upload_file("almost1mb.txt", size_mb=0.999)
    assert response.status_code == 201
    r = requests.get(f"{base_url}/files/{file_id}/metadata")
    assert r.status_code == 200
    size = r.json()["size"]
    assert size < 1048576


def test_tc04_upload_large_file(upload_file, base_url):
    file_id, response = upload_file("large10gb.bin", size_mb=10)
    assert response.status_code in [201, 413]
    if response.status_code == 201:
        r = requests.get(f"{base_url}/files/{file_id}/metadata")
        assert r.status_code == 200
        assert r.json()["size"] >= 10 * 1024 * 1024 * 1024



# Admin Faults Operation  check

def test_tc05_tiering_without_auth(base_url):
    r = requests.post(f"{base_url}/admin/tiering/run")
    assert r.status_code in [401, 403]


def test_tc06_get_stats_without_auth(base_url):
    r = requests.get(f"{base_url}/admin/stats")
    assert r.status_code in [401, 403]
