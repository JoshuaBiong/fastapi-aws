import os
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from datetime import datetime
from markupsafe import escape
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:masterpassword@database-2.cpcmy2g42nlx.ap-southeast-2.rds.amazonaws.com:5432/postgres",
)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


Base.metadata.create_all(engine)

app = FastAPI()


def note_dict(n: Note) -> dict:
    return {"id": n.id, "title": n.title, "content": n.content, "created_at": n.created_at.isoformat()}


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
    with Session() as s:
        notes = [note_dict(n) for n in s.query(Note).order_by(Note.id).all()]
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
    with Session() as s:
        note = s.query(Note).filter(Note.id == note_id).first()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return render_form(note_dict(note))


@app.post("/notes", response_class=HTMLResponse)
def create_note(title: str = Form(), content: str = Form()):
    with Session() as s:
        s.add(Note(title=title, content=content))
        s.commit()
    return render_list()


@app.put("/notes/{note_id}", response_class=HTMLResponse)
def update_note(note_id: int, title: str = Form(), content: str = Form()):
    with Session() as s:
        note = s.query(Note).filter(Note.id == note_id).first()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        note.title = title
        note.content = content
        s.commit()
    return render_list()


@app.delete("/notes/{note_id}", response_class=HTMLResponse)
def delete_note(note_id: int):
    with Session() as s:
        note = s.query(Note).filter(Note.id == note_id).first()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        s.delete(note)
        s.commit()
    return ""
