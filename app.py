import hashlib
import json
import os
import secrets
from datetime import date, datetime, timedelta
from pathlib import Path

import streamlit as st


st.set_page_config(page_title="Luma | Your clear space", page_icon="✦", layout="wide", initial_sidebar_state="expanded")

DATA_PATH = Path(os.getenv("LUMA_DATA_PATH", ".luma_data.json"))


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split("$", 1)
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()
        return secrets.compare_digest(candidate, digest)
    except ValueError:
        return False


def blank_store() -> dict:
    return {"users": {}}


def load_store() -> dict:
    if not DATA_PATH.exists():
        return blank_store()
    try:
        return json.loads(DATA_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        return blank_store()


def save_store(store: dict) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = DATA_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(store, indent=2))
    temporary.replace(DATA_PATH)


def new_user(email: str, password: str) -> dict:
    today = date.today().isoformat()
    return {
        "password": hash_password(password),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "notes": [
            {"id": secrets.token_hex(5), "title": "A softer start", "body": "What would make today feel lighter?", "color": "coral", "updated": "Today", "pinned": True},
            {"id": secrets.token_hex(5), "title": "Weekend ideas", "body": "Museum, long walk, something new to cook.", "color": "mint", "updated": "Yesterday", "pinned": False},
        ],
        "tasks": [
            {"id": secrets.token_hex(5), "title": "Choose three priorities", "due": today, "project": "Today", "done": False},
            {"id": secrets.token_hex(5), "title": "Send the follow-up email", "due": today, "project": "Work", "done": False},
            {"id": secrets.token_hex(5), "title": "Plan groceries", "due": (date.today() + timedelta(days=1)).isoformat(), "project": "Personal", "done": False},
        ],
    }


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;600;700;800&display=swap');
        :root { --ink:#23312e; --muted:#74817d; --paper:#f7f6f1; --line:#dedfd7; --coral:#e8785d; --mint:#cfe8dc; --yellow:#f5dda0; }
        .stApp { background:var(--paper); color:var(--ink); font-family:'Manrope', sans-serif; }
        .stApp p, .stApp label, .stApp [data-testid="stCaptionContainer"], .stApp .stMarkdown, .stApp .stRadio label { color:var(--ink); }
        .stApp input, .stApp textarea, .stApp select { color:var(--ink) !important; background:#fff !important; }
        .stApp input::placeholder, .stApp textarea::placeholder { color:#66756f !important; opacity:1; }
        .stApp [data-baseweb="select"] * { color:var(--ink) !important; }
        [data-testid="stSidebar"] { background:#e7efe9; border-right:1px solid #d4ded7; }
        [data-testid="stSidebar"] > div:first-child { padding:2rem 1.25rem; }
        h1,h2,h3 { font-family:'Manrope',sans-serif; letter-spacing:-.04em; color:var(--ink); }
        h1 { font-size:clamp(2.1rem, 5vw, 4.4rem); line-height:1; }
        .eyebrow { font:500 .72rem 'DM Mono',monospace; text-transform:uppercase; letter-spacing:.12em; color:var(--coral); }
        .brand { font-weight:800; font-size:1.65rem; letter-spacing:-.07em; margin-bottom:3rem; }
        .brand span { color:var(--coral); }
        .side-note { color:#617069; font-size:.8rem; line-height:1.5; margin:2.5rem 0; }
        .hero { padding:1.25rem 0 1rem; border-bottom:1px solid var(--line); margin-bottom:1.25rem; }
        .hero p { color:#52615c; max-width:34rem; font-size:1.03rem; }
        .stat { background:white; border:1px solid var(--line); border-radius:5px; padding:1.1rem 1.2rem; min-height:7rem; }
        .stat strong { display:block; font-size:2rem; letter-spacing:-.06em; }
        .stat small { color:var(--muted); font:500 .68rem 'DM Mono',monospace; text-transform:uppercase; }
        .note-card { border-radius:5px; padding:1.15rem; min-height:10rem; border:1px solid rgba(35,49,46,.08); margin-bottom:1rem; }
        .note-card h3 { font-size:1rem; margin:.65rem 0 .35rem; }
        .note-card p { color:#293a34; font-size:.86rem; line-height:1.5; }
        .note-card small { color:#42564e; font:500 .66rem 'DM Mono',monospace; }
        .coral { background:#f5c8b8; } .mint { background:#d5eadf; } .yellow { background:#f5e5ad; } .blue { background:#cfe1ee; }
        .section-label { font:500 .72rem 'DM Mono',monospace; text-transform:uppercase; letter-spacing:.1em; color:#52615c; margin:1rem 0; }
        .task-row { background:white; border:1px solid var(--line); border-radius:5px; padding:.55rem .85rem; margin-bottom:.5rem; }
        .keep-board { display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:.8rem; }
        .keep-board .note-card { margin:0; min-height:8.5rem; }
        @media (max-width: 720px) { .keep-board { grid-template-columns:1fr; } }
        .keep-search { background:white; border:1px solid var(--line); border-radius:5px; padding:.2rem .6rem; }
        .today-chip { display:inline-block; background:var(--ink); color:white; border-radius:999px; padding:.32rem .65rem; font:500 .68rem 'DM Mono',monospace; }
        .stButton button { border-radius:4px; border:1px solid var(--ink); font-weight:700; min-height:2.5rem; }
        .stButton button[kind="primary"] { background:var(--coral); border-color:var(--coral); color:white; }
        div[data-testid="stForm"] { border:1px solid var(--line); background:white; border-radius:5px; padding:1rem; }
        [data-testid="stMetric"] { background:white; border:1px solid var(--line); padding:1rem; border-radius:5px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def auth_screen(store: dict) -> None:
    inject_styles()
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "Log in"
    left, right = st.columns([1.08, .92], gap="large")
    with left:
        st.markdown('<div class="eyebrow">One calm place for your day</div>', unsafe_allow_html=True)
        st.title("Make space for what matters.")
        st.markdown("Keep your thoughts, next steps, and plans close at hand. Luma is a lighter way to move through a full day.")
        st.markdown("<br><div class='today-chip'>notes · tasks · today</div>", unsafe_allow_html=True)
    with right:
        st.markdown("### Welcome to Luma")
        st.caption("Log in to your workspace or create a new account. Your workspace is saved on this device.")
        mode = st.radio("Account action", ["Log in", "Create account"], key="auth_mode", horizontal=True, label_visibility="collapsed")
        if mode == "Create account" and st.button("← Back to log in", use_container_width=True):
            st.session_state.auth_mode = "Log in"
            st.rerun()
        with st.form("auth_form", clear_on_submit=False):
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="At least 6 characters")
            submitted = st.form_submit_button("Log in" if mode == "Log in" else "Create account", type="primary", use_container_width=True)
        if submitted:
            normalized = email.strip().lower()
            if "@" not in normalized or len(password) < 6:
                st.error("Enter a valid email and a password with at least 6 characters.")
            elif mode == "Create account" and normalized in store["users"]:
                st.error("An account with that email already exists.")
            elif mode == "Log in" and (normalized not in store["users"] or not verify_password(password, store["users"][normalized]["password"])):
                st.error("That email and password do not match.")
            else:
                if mode == "Create account":
                    store["users"][normalized] = new_user(normalized, password)
                    save_store(store)
                st.session_state.email = normalized
                st.rerun()


def task_label(task: dict) -> str:
    if task["done"]:
        return f"~~{task['title']}~~"
    return task["title"]


def app_screen(store: dict, email: str) -> None:
    user = store["users"][email]
    inject_styles()
    with st.sidebar:
        st.markdown('<div class="brand">lu<span>m</span>a</div>', unsafe_allow_html=True)
        st.markdown('<div class="eyebrow">Your workspace</div>', unsafe_allow_html=True)
        page = st.radio("Navigate", ["Today", "Notes", "Tasks"], label_visibility="collapsed")
        st.markdown('<div class="side-note">A little less noise. A little more room to think, remember, and get things done.</div>', unsafe_allow_html=True)
        st.caption(email)
        if st.button("Log out", use_container_width=True):
            st.session_state.pop("email", None)
            st.session_state.auth_mode = "Log in"
            st.rerun()

    if page == "Today":
        today_view(user, store)
    elif page == "Notes":
        notes_view(user, store)
    else:
        tasks_view(user, store)


def today_view(user: dict, store: dict) -> None:
    today = date.today().isoformat()
    st.markdown('<div class="eyebrow">Luma Keep · your notes</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero"><h1>Today</h1><p>Capture a thought, pin what matters, and find it again when you need it.</p></div>', unsafe_allow_html=True)
    search = st.text_input("Search your notes", placeholder="Search notes", label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("Take a note...", expanded=False):
        with st.form("keep_capture"):
            title = st.text_input("Title", placeholder="Title")
            body = st.text_area("Take a note", placeholder="Write a note...", height=100)
            capture_cols = st.columns([1, 1, .7])
            color = capture_cols[0].selectbox("Color", ["yellow", "coral", "mint", "blue"])
            pinned = capture_cols[1].checkbox("Pin to top")
            captured = capture_cols[2].form_submit_button("Save", type="primary")
            if captured and body.strip():
                user["notes"].insert(0, {"id": secrets.token_hex(5), "title": title.strip() or "Untitled note", "body": body.strip(), "color": color, "updated": "Just now", "pinned": pinned})
                save_store(store)
                st.rerun()
    view = st.radio("Note filter", ["All notes", "Pinned", "Tasks due today"], horizontal=True, label_visibility="collapsed")
    if view == "Tasks due today":
        due = [task for task in user["tasks"] if task["due"] <= today and not task["done"]]
        for task in due:
            if st.checkbox(task["title"], key=f"today_{task['id']}"):
                task["done"] = True
                save_store(store)
                st.rerun()
        if not due:
            st.info("No tasks due today.")
        return
    notes = [note for note in user["notes"] if (not search.strip() or search.lower() in f"{note['title']} {note['body']}".lower()) and (view == "All notes" or note.get("pinned", False))]
    notes.sort(key=lambda note: (not note.get("pinned", False), note.get("updated", "")))
    st.markdown('<div class="section-label">Pinned notes</div>', unsafe_allow_html=True)
    note_columns = st.columns(3)
    for index, note in enumerate(notes):
        if "pinned" not in note:
            note["pinned"] = False
        with note_columns[index % 3]:
            st.markdown(f'<div class="note-card {note.get("color", "yellow")}"><small>{"📌 Pinned" if note.get("pinned") else "Note"} · {note.get("updated", "Saved")}</small><h3>{note["title"]}</h3><p>{note["body"]}</p></div>', unsafe_allow_html=True)
            action_cols = st.columns(2)
            if action_cols[0].button("Unpin" if note.get("pinned") else "Pin", key=f"pin_{note['id']}"):
                note["pinned"] = not note.get("pinned", False)
                save_store(store)
                st.rerun()
            if action_cols[1].button("Delete", key=f"delete_{note['id']}"):
                user["notes"].remove(note)
                save_store(store)
                st.rerun()


def notes_view(user: dict, store: dict) -> None:
    st.markdown('<div class="eyebrow">Notes</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero"><h1>Keep the good ideas.</h1><p>A flexible shelf for thoughts, lists, and little reminders.</p></div>', unsafe_allow_html=True)
    with st.expander("+ New note", expanded=False):
        with st.form("new_note"):
            title = st.text_input("Title", placeholder="A name for this thought")
            body = st.text_area("Note", placeholder="Start writing...", height=120)
            color = st.selectbox("Color", ["coral", "mint", "yellow", "blue"])
            if st.form_submit_button("Save note", type="primary") and body.strip():
                user["notes"].insert(0, {"id": secrets.token_hex(5), "title": title.strip() or "Untitled note", "body": body.strip(), "color": color, "updated": "Just now"})
                save_store(store)
                st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    columns = st.columns(3)
    for index, note in enumerate(user["notes"]):
        with columns[index % 3]:
            st.markdown(f'<div class="note-card {note.get("color", "yellow")}"><small>{note.get("updated", "Saved")}</small><h3>{note["title"]}</h3><p>{note["body"]}</p></div>', unsafe_allow_html=True)


def tasks_view(user: dict, store: dict) -> None:
    st.markdown('<div class="eyebrow">Tasks</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero"><h1>One thing at a time.</h1><p>A focused list that keeps your next steps visible and your head clear.</p></div>', unsafe_allow_html=True)
    with st.form("new_task"):
        cols = st.columns([2, 1, 1, .7])
        title = cols[0].text_input("Task", placeholder="Add a task...")
        due = cols[1].date_input("Due", value=date.today())
        project = cols[2].text_input("List", value="Today")
        submit = cols[3].form_submit_button("Add", type="primary")
        if submit and title.strip():
            user["tasks"].insert(0, {"id": secrets.token_hex(5), "title": title.strip(), "due": due.isoformat(), "project": project.strip() or "Today", "done": False})
            save_store(store)
            st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    for task in user["tasks"]:
        cols = st.columns([.08, 2.8, .8, .8])
        with cols[0]:
            checked = st.checkbox("Done", value=task["done"], key=f"task_{task['id']}", label_visibility="collapsed")
        if checked != task["done"]:
            task["done"] = checked
            save_store(store)
            st.rerun()
        with cols[1]:
            st.markdown(f'<div class="task-row">{task_label(task)}</div>', unsafe_allow_html=True)
        with cols[2]:
            st.caption(task["project"])
        with cols[3]:
            st.caption(task["due"])


store = load_store()
if "email" not in st.session_state or st.session_state.email not in store["users"]:
    auth_screen(store)
else:
    app_screen(store, st.session_state.email)
