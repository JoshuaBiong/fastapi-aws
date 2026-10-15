from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from datetime import datetime
from markupsafe import escape

app = FastAPI()

notes: list[dict] = []
next_id = 1


def render_note(n: dict) -> str:
    return f"""<div class="note" id="note-{n['id']}">
  <h3>{escape(n['title'])}</h3>
  <p>{escape(n['content'])}</p>
  <small>{datetime.fromisoformat(n['created_at']).strftime('%b %d, %Y %I:%M %p')}</small>
  <div class="actions">
    <button class="edit-btn"
      hx-get="/notes/{n['id']}/edit"
      hx-target="#form-area"
      hx-swap="innerHTML">Edit</button>
    <button class="del-btn"
      hx-delete="/notes/{n['id']}"
      hx-target="#note-{n['id']}"
      hx-swap="outerHTML"
      hx-confirm="Delete this note?">Delete</button>
  </div>
</div>"""


def render_list() -> str:
    if not notes:
        return '<div class="empty">No notes yet.</div>'
    return "".join(render_note(n) for n in notes)


def render_form(note: dict | None = None) -> str:
    if note:
        return f"""<form hx-put="/notes/{note['id']}" hx-target="#list" hx-swap="innerHTML" hx-on::after-request="this.reset()">
  <input name="title" placeholder="Title" value="{escape(note['title'])}" required />
  <textarea name="content" placeholder="Content" required>{escape(note['content'])}</textarea>
  <button type="submit">Update</button>
  <button type="button" class="cancel" hx-get="/notes/form" hx-target="#form-area" hx-swap="innerHTML">Cancel</button>
</form>"""
    return """<form hx-post="/notes" hx-target="#list" hx-swap="innerHTML" hx-on::after-request="this.reset()">
  <input name="title" placeholder="Title" required />
  <textarea name="content" placeholder="Content" required></textarea>
  <button type="submit">Save</button>
</form>"""



@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")


@app.get("/notes", response_class=HTMLResponse)
def list_notes():
    return render_list()


@app.get("/notes/form", response_class=HTMLResponse)
def get_form():
    return render_form()


@app.get("/notes/{note_id}/edit", response_class=HTMLResponse)
def edit_form(note_id: int):
    for note in notes:
        if note["id"] == note_id:
            return render_form(note)
    raise HTTPException(status_code=404, detail="Note not found")


@app.post("/notes", response_class=HTMLResponse)
def create_note(title: str = Form(), content: str = Form()):
    global next_id
    notes.append({
        "id": next_id,
        "title": title,
        "content": content,
        "created_at": datetime.now().isoformat(),
    })
    next_id += 1
    return render_list()


@app.put("/notes/{note_id}", response_class=HTMLResponse)
def update_note(note_id: int, title: str = Form(), content: str = Form()):
    for note in notes:
        if note["id"] == note_id:
            note["title"] = title
            note["content"] = content
            return render_list()
    raise HTTPException(status_code=404, detail="Note not found")


@app.delete("/notes/{note_id}", response_class=HTMLResponse)
def delete_note(note_id: int):
    for i, note in enumerate(notes):
        if note["id"] == note_id:
            notes.pop(i)
            return ""
    raise HTTPException(status_code=404, detail="Note not found")
