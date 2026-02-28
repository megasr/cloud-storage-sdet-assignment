import requests
import datetime
from datetime import datetime, timedelta, UTC

# Helper Functions
def mock_last_accessed(base_url, admin_cred, file_id, days_old):

    fake_timestamp = (datetime.now(UTC) - timedelta(days=days_old)).isoformat()
    resp = requests.patch(
        f"{base_url}/files/{file_id}/metadata",
        headers=admin_cred,
        json={"lastAccessed": fake_timestamp}
    )
    assert resp.status_code in [200, 204], f"Failed mock timestamp: {resp.text}"

def trigger_tiering(base_url, admin_cred):
    resp = requests.post(f"{base_url}/admin/tiering/run", headers=admin_cred)
    assert resp.status_code in [200, 202], f"Tiering run failed: {resp.text}"
    return resp.json()

def get_tier(base_url, admin_cred, file_id):
    resp = requests.get(f"{base_url}/files/{file_id}/metadata", headers=admin_cred)
    assert resp.status_code == 200
    return resp.json()["tier"]



# Tiering Boundary Tests cases
def test_tc01_hot_to_warm_at_30_days(upload_file, base_url, admin_cred):
    file_id, _ = upload_file("hot_30.txt", size_mb=2)
    mock_last_accessed(base_url, admin_cred, file_id, 30)
    trigger_tiering(base_url, admin_cred)
    assert get_tier(base_url, admin_cred, file_id) == "WARM"

def test_tc02_warm_to_cold_at_90_days(upload_file, base_url, admin_cred):
    file_id, _ = upload_file("warm_90.txt", size_mb=2)
    mock_last_accessed(base_url, admin_cred, file_id, 90)
    trigger_tiering(base_url, admin_cred)
    assert get_tier(base_url, admin_cred, file_id) == "COLD"

def test_tc03_remain_hot_at_29_days(upload_file, base_url, admin_cred):
    file_id, _ = upload_file("hot_29.txt", size_mb=2)
    mock_last_accessed(base_url, admin_cred, file_id, 29)
    trigger_tiering(base_url, admin_cred)
    assert get_tier(base_url, admin_cred, file_id) == "HOT"

def test_tc04_remain_warm_at_89_days(upload_file, base_url, admin_cred):
    file_id, _ = upload_file("warm_89.txt", size_mb=2)
    mock_last_accessed(base_url, admin_cred, file_id, 89)
    trigger_tiering(base_url, admin_cred)
    assert get_tier(base_url, admin_cred, file_id) == "WARM"

def test_tc05_access_restoration(upload_file, base_url, admin_cred):
    file_id, _ = upload_file("restore.txt", size_mb=2)
    mock_last_accessed(base_url, admin_cred, file_id, 100)
    trigger_tiering(base_url, admin_cred)
    assert get_tier(base_url, admin_cred, file_id) == "COLD"

    # Access file (download)
    requests.get(f"{base_url}/files/{file_id}")

    # Verify restored to HOT
    assert get_tier(base_url, admin_cred, file_id) == "HOT"

def test_tc06_update_last_accessed_negative_days(base_url, upload_file):
    file_id, response = upload_file("neg_date.txt", size_mb=2)
    assert response.status_code == 201


    r = requests.post(f"{base_url}/admin/files/{file_id}/update-last-accessed",
                      json={"days_ago": -5})
    # Expected: should fail with 400
    assert r.status_code == 400


# Bulk Performance Tests


def test_tc07_bulk_upload_files(upload_file, base_url):
    file_ids = []
    for i in range(100):
        file_id, response = upload_file(f"bulk_file_{i}.txt", size_mb=1)
        assert response.status_code == 201
        file_ids.append(file_id)

    # Verify all files accessible
    for file_id in file_ids:
        r = requests.get(f"{base_url}/files/{file_id}")
        assert r.status_code == 200
        assert r.content.startswith(b"test")

def test_tc_08_bulk_delete_files(upload_file, base_url):
    file_ids = []
    for i in range(50):
        file_id, response = upload_file(f"delete_file_{i}.txt", size_mb=1)
        assert response.status_code == 201
        file_ids.append(file_id)

    # Delete all files
    for file_id in file_ids:
        r = requests.delete(f"{base_url}/files/{file_id}")
        assert r.status_code in [200, 204]

    # Verify metadata cleanup
    for file_id in file_ids:
        r = requests.get(f"{base_url}/files/{file_id}/metadata")
        assert r.status_code == 404
