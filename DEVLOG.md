# Dev Log

Track features, progress, changes, and errors for the Note App.

## Features

| Feature | Status | Notes |
|---------|--------|-------|
| List all notes | Done | `GET /notes` |
| Get single note | Done | `GET /notes/{id}` |
| Create note | Done | `POST /notes` |
| Update note | Done | `PUT /notes/{id}` |
| Delete note | Done | `DELETE /notes/{id}` |
| Frontend UI (htmx) | Done | `static/index.html`, served at `/` |
| AWS EC2 deployment | Done | Amazon Linux, t2.micro, port 8000 |
| Persistent storage (DB) | Planned | Currently in-memory only |
| Search notes | Planned | |
| Tags/categories | Planned | |

## Changes

- **2026-10-15** — Initial note app with full CRUD (in-memory storage)
- **2026-10-15** — Added frontend UI (vanilla HTML/CSS/JS at `static/index.html`)
- **2026-10-15** — Deployed to AWS EC2 (ap-southeast-2, Amazon Linux, port 8000)

## Errors / Known Issues

- Notes are lost on server restart (in-memory list). Will be fixed when DB is added.

## Deployment Errors & Troubleshooting Log (2026-10-15)

### 1. SSH connection timed out
- **Error**: `ssh: connect to host 15.135.164.138 port 22: Operation timed out`
- **Tried**: Checking security group inbound rules for SSH (port 22)
- **Solution**: Security group needed SSH rule with correct source. Added SSH (port 22) → My IP.

### 2. EC2 instance had no internet access
- **Error**: `curl example.com` and `curl parrot.live` hung indefinitely from inside the instance
- **Tried**:
  - Checked security group outbound rules (all traffic → 0.0.0.0/0) ✅
  - Checked VPC had Internet Gateway attached ✅
  - Checked route table had 0.0.0.0/0 → igw route ✅
  - Checked Network ACLs ✅
  - Tried switching region from Sydney to Singapore — got `instance ID does not exist` error (instances are region-specific)
- **Solution**: Terminated the broken instance. Launched a fresh EC2 instance in Sydney with **default VPC**, **default subnet**, and **Auto-assign public IP enabled**. New instance had working internet.

### 3. Git not installed
- **Error**: `-bash: git: command not found`
- **Tried**: `sudo apt install git` (wrong — this is Amazon Linux, not Ubuntu)
- **Solution**: `sudo yum install git -y`

### 4. Port 80 already in use
- **Error**: `[Errno 98] error while attempting to bind on address ('0.0.0.0', 80): address already in use`
- **Cause**: Previous `nohup` run left a process on port 80
- **Solution**: `sudo kill $(sudo lsof -t -i:80)` then restart the server

### 5. Server wouldn't bind to port 80
- **Error**: `curl localhost` returned `Could not connect to server` even after killing old process
- **Tried**: Restarting on port 80 — kept failing
- **Solution**: Switched to port 8000: `sudo uv run fastapi run main.py --host 0.0.0.0 --port 8000`

### 6. Browser couldn't reach the app
- **Error**: `ERR_CONNECTION_REFUSED` when accessing `http://54.79.37.199`
- **Cause**: Security group only allowed port 80, app was running on port 8000
- **Solution**: Added inbound rule: Custom TCP → port 8000 → Source 0.0.0.0/0

### 7. Browser auto-redirected to HTTPS
- **Error**: Browser sent requests to `https://54.79.37.199/` instead of `http://`
- **Cause**: Chrome auto-upgrades URLs to HTTPS
- **Solution**: Explicitly type `http://54.79.37.199:8000` or use incognito window

### 8. POST requests going to wrong host
- **Error**: Network tab showed requests going to `http://0.0.0.0:8000/notes`
- **Cause**: Accessed the app via `0.0.0.0:8000` instead of the public IP
- **Solution**: Access via public IP `http://54.79.37.199:8000` — htmx uses relative URLs so requests route correctly
