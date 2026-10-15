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
| Frontend UI | Done | `static/index.html`, served at `/` |
| Persistent storage (DB) | Planned | Currently in-memory only |
| Search notes | Planned | |
| Tags/categories | Planned | |

## Changes

- **2026-10-15** — Initial note app with full CRUD (in-memory storage)
- **2026-10-15** — Added frontend UI (vanilla HTML/CSS/JS at `static/index.html`)

## Errors / Known Issues

- Notes are lost on server restart (in-memory list). Will be fixed when DB is added.
