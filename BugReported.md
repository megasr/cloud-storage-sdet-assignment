Bug Reports
Bug #1
Title: Negative value is accepted for the update-last-accessed API endpoint
Testcase #: TC06
Steps:

Upload a file with valid size and name.

Call the POST /admin/files/{file_id}/update-last-accessed endpoint with days_ago = -5.

Retrieve the file metadata.

Expected vs Actual:

Expected: Input validation should reject negative values. Only positive integers should be accepted.

Actual: Negative values are accepted, causing the last_accessed timestamp to appear in the future, which is not reasonable.

Logs:  
File upload response:
{"file_id":"6fc425e8-e6e1-4577-a1d2-13f37aa07f90","filename":"neg_date.txt","size":1048576,"tier":"HOT","created_at":"2025-11-20T17:44:31.756090","last_accessed":"2025-11-20T17:44:31.756090","content_type":"application/octet-stream","etag":"ae4790b5-cfd1-4cc2-8929-199804b987ac"}

Metadata after update with days_ago = -5:
{"file_id":"6fc425e8-e6e1-4577-a1d2-13f37aa07f90","filename":"neg_date.txt","size":1048576,"tier":"HOT","created_at":"2025-11-20T17:44:31.756090","last_accessed":"2025-11-25T17:44:31.758601","content_type":"application/octet-stream","etag":"ae4790b5-cfd1-4cc2-8929-199804b987ac"}

Bug #2
Title: File with malicious name is uploaded
Testcase #: TC05
Steps:

Upload a file with the name "../../etc/passwd" or "/etc/passwd".

Observe the response.

Expected vs Actual:

Expected: File name validation should reject names containing Unix-like path structures.

Actual: The server accepts the malicious filename without validation.

Logs:
{"file_id":"da21dc78-b53f-43d0-84e7-8486de48f5eb","filename":"../../etc/passwd","size":2097152,"tier":"HOT","created_at":"2025-11-20T17:44:32.718086","last_accessed":"2025-11-20T17:44:32.718086","content_type":"application/octet-stream","etag":"dfdf2275-06ed-4de5-adac-ff4c1ca96819"}
