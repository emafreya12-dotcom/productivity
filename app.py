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
        "habits": [
            {"id": secrets.token_hex(5), "name": "Drink water", "goal": "8 glasses", "color": "blue", "history": {}},
            {"id": secrets.token_hex(5), "name": "Read", "goal": "10 minutes", "color": "mint", "history": {}},
        ],
        "events": [
            {"id": secrets.token_hex(5), "title": "Weekly planning", "date": today, "time": "09:00", "color": "coral"},
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


def edit_note_form(user: dict, store: dict, note: dict) -> None:
    with st.form(f"edit_note_{note['id']}"):
        title = st.text_input("Title", value=note.get("title", ""))
        body = st.text_area("Note", value=note.get("body", ""), height=120)
        cols = st.columns([1, 1, .8])
        colors = ["yellow", "coral", "mint", "blue"]
        color = cols[0].selectbox("Color", colors, index=colors.index(note.get("color", "yellow")) if note.get("color", "yellow") in colors else 0)
        pinned = cols[1].checkbox("Pin to top", value=note.get("pinned", False))
        saved = cols[2].form_submit_button("Save changes", type="primary")
        if saved and body.strip():
            note.update({"title": title.strip() or "Untitled note", "body": body.strip(), "color": color, "pinned": pinned, "updated": "Just now"})
            save_store(store)
            st.session_state.pop("edit_note_id", None)
            st.rerun()


def edit_task_form(store: dict, task: dict) -> None:
    with st.form(f"edit_task_{task['id']}"):
        cols = st.columns([2, 1, 1, .8])
        title = cols[0].text_input("Task", value=task["title"])
        due = cols[1].date_input("Due", value=date.fromisoformat(task["due"]))
        project = cols[2].text_input("List", value=task.get("project", "Today"))
        saved = cols[3].form_submit_button("Save", type="primary")
        if saved and title.strip():
            task.update({"title": title.strip(), "due": due.isoformat(), "project": project.strip() or "Today"})
            save_store(store)
            st.session_state.pop("edit_task_id", None)
            st.rerun()


def app_screen(store: dict, email: str) -> None:
    user = store["users"][email]
    migrated = False
    if "habits" not in user:
        user["habits"] = []
        migrated = True
    if "events" not in user:
        user["events"] = []
        migrated = True
    for note in user.get("notes", []):
        if "pinned" not in note:
            note["pinned"] = False
            migrated = True
    if migrated:
        save_store(store)
    inject_styles()
    with st.sidebar:
        st.markdown('<div class="brand">lu<span>m</span>a</div>', unsafe_allow_html=True)
        st.markdown('<div class="eyebrow">Your workspace</div>', unsafe_allow_html=True)
        page = st.radio("Navigate", ["Today", "Notes", "Tasks", "Habits", "Calendar"], label_visibility="collapsed")
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
    elif page == "Tasks":
        tasks_view(user, store)
    elif page == "Habits":
        habits_view(user, store)
    else:
        calendar_view(user, store)


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
    editing_id = st.session_state.get("edit_note_id")
    if editing_id:
        editing_note = next((note for note in user["notes"] if note["id"] == editing_id), None)
        if editing_note:
            st.markdown('<div class="section-label">Edit note</div>', unsafe_allow_html=True)
            edit_note_form(user, store, editing_note)
            if st.button("Cancel editing", key="cancel_note_edit"):
                st.session_state.pop("edit_note_id", None)
                st.rerun()
    note_columns = st.columns(3)
    for index, note in enumerate(notes):
        if "pinned" not in note:
            note["pinned"] = False
        with note_columns[index % 3]:
            st.markdown(f'<div class="note-card {note.get("color", "yellow")}"><small>{"📌 Pinned" if note.get("pinned") else "Note"} · {note.get("updated", "Saved")}</small><h3>{note["title"]}</h3><p>{note["body"]}</p></div>', unsafe_allow_html=True)
            action_cols = st.columns(2)
            if action_cols[0].button("Edit", key=f"edit_{note['id']}"):
                st.session_state.edit_note_id = note["id"]
                st.rerun()
            if action_cols[1].button("Unpin" if note.get("pinned") else "Pin", key=f"pin_{note['id']}"):
                note["pinned"] = not note.get("pinned", False)
                save_store(store)
                st.rerun()
            delete_cols = st.columns(1)
            if delete_cols[0].button("Delete note", key=f"delete_{note['id']}"):
                user["notes"].remove(note)
                if st.session_state.get("edit_note_id") == note["id"]:
                    st.session_state.pop("edit_note_id", None)
                save_store(store)
                st.rerun()


def habits_view(user: dict, store: dict) -> None:
    today = date.today()
    st.markdown('<div class="eyebrow">Habits · small actions, visible progress</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero"><h1>Build a rhythm.</h1><p>Check in once a day. The graph makes consistency feel concrete.</p></div>', unsafe_allow_html=True)
    if not user["habits"]:
        st.info("Add your first habit below to begin your streak.")
    for habit in user["habits"]:
        history = habit.setdefault("history", {})
        completed_days = sum(1 for day in history.values() if day)
        current = history.get(today.isoformat(), False)
        cols = st.columns([2.3, 1.1, .8])
        with cols[0]:
            st.markdown(f'<div class="note-card {habit.get("color", "mint")}" style="min-height:5.5rem"><small>{habit["goal"]} · {completed_days} check-ins</small><h3>{habit["name"]}</h3><p>{"Done today" if current else "Ready for today"}</p></div>', unsafe_allow_html=True)
        with cols[1]:
            checked = st.checkbox("Complete today", value=current, key=f"habit_{habit['id']}")
            if checked != current:
                history[today.isoformat()] = checked
                save_store(store)
                st.rerun()
        with cols[2]:
            if st.button("Delete", key=f"habit_delete_{habit['id']}"):
                user["habits"].remove(habit)
                save_store(store)
                st.rerun()
        graph_values = {}
        for offset in range(6, -1, -1):
            day = today - timedelta(days=offset)
            graph_values[day.strftime("%a")] = 1 if history.get(day.isoformat(), False) else 0
        st.bar_chart(graph_values, height=120, color="#e8785d")
    with st.expander("+ Add a habit", expanded=not user["habits"]):
        with st.form("new_habit"):
            cols = st.columns([1.4, 1, .8])
            name = cols[0].text_input("Habit", placeholder="Stretch, journal, walk...")
            goal = cols[1].text_input("Tiny goal", placeholder="10 minutes")
            color = cols[2].selectbox("Color", ["mint", "blue", "yellow", "coral"])
            if st.form_submit_button("Add habit", type="primary") and name.strip():
                user["habits"].append({"id": secrets.token_hex(5), "name": name.strip(), "goal": goal.strip() or "Daily", "color": color, "history": {}})
                save_store(store)
                st.rerun()


def calendar_view(user: dict, store: dict) -> None:
    today = date.today()
    st.markdown('<div class="eyebrow">Calendar · what has a place in your day</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero"><h1>Make time visible.</h1><p>A simple agenda for appointments, plans, and the moments your tasks depend on.</p></div>', unsafe_allow_html=True)
    with st.expander("+ Add an event", expanded=False):
        with st.form("new_event"):
            cols = st.columns([1.7, 1, .8, .7])
            title = cols[0].text_input("Event", placeholder="Dentist, focus block, dinner...")
            event_date = cols[1].date_input("Date", value=today)
            event_time = cols[2].time_input("Time", value=datetime.now().replace(second=0, microsecond=0).time())
            color = cols[3].selectbox("Color", ["coral", "blue", "mint", "yellow"])
            if st.form_submit_button("Add event", type="primary") and title.strip():
                user["events"].append({"id": secrets.token_hex(5), "title": title.strip(), "date": event_date.isoformat(), "time": event_time.strftime("%H:%M"), "color": color})
                save_store(store)
                st.rerun()
    st.markdown('<div class="section-label">Next 30 days</div>', unsafe_allow_html=True)
    events = sorted(user["events"], key=lambda event: (event["date"], event["time"]))
    upcoming = [event for event in events if event["date"] >= today.isoformat()]
    if not upcoming:
        st.info("Your calendar is clear. Add an event above.")
    for event in upcoming:
        event_day = date.fromisoformat(event["date"])
        if event_day > today + timedelta(days=30):
            continue
        cols = st.columns([.8, 2.5, .8, .5])
        with cols[0]:
            st.markdown(f'<div class="today-chip">{event_day.strftime("%b %-d")}</div>', unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f'<div class="task-row"><strong>{event["title"]}</strong><br><small>{event_day.strftime("%A")} · {event["time"]}</small></div>', unsafe_allow_html=True)
        with cols[2]:
            st.caption(event.get("color", "event"))
        with cols[3]:
            if st.button("×", key=f"event_delete_{event['id']}"):
                user["events"].remove(event)
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
    editing_id = st.session_state.get("edit_note_id")
    if editing_id:
        editing_note = next((note for note in user["notes"] if note["id"] == editing_id), None)
        if editing_note:
            st.markdown('<div class="section-label">Edit note</div>', unsafe_allow_html=True)
            edit_note_form(user, store, editing_note)
            if st.button("Cancel editing", key="cancel_notes_edit"):
                st.session_state.pop("edit_note_id", None)
                st.rerun()
    columns = st.columns(3)
    for index, note in enumerate(user["notes"]):
        with columns[index % 3]:
            st.markdown(f'<div class="note-card {note.get("color", "yellow")}"><small>{note.get("updated", "Saved")}</small><h3>{note["title"]}</h3><p>{note["body"]}</p></div>', unsafe_allow_html=True)
            if st.button("Edit", key=f"notes_edit_{note['id']}"):
                st.session_state.edit_note_id = note["id"]
                st.rerun()
            if st.button("Delete note", key=f"notes_delete_{note['id']}"):
                user["notes"].remove(note)
                if st.session_state.get("edit_note_id") == note["id"]:
                    st.session_state.pop("edit_note_id", None)
                save_store(store)
                st.rerun()


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
    editing_id = st.session_state.get("edit_task_id")
    if editing_id:
        editing_task = next((task for task in user["tasks"] if task["id"] == editing_id), None)
        if editing_task:
            st.markdown('<div class="section-label">Edit task</div>', unsafe_allow_html=True)
            edit_task_form(store, editing_task)
            if st.button("Cancel editing", key="cancel_task_edit"):
                st.session_state.pop("edit_task_id", None)
                st.rerun()
    for task in user["tasks"]:
        cols = st.columns([.08, 2.2, .7, .7, .7])
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
        with cols[4]:
            if st.button("Edit", key=f"task_edit_{task['id']}"):
                st.session_state.edit_task_id = task["id"]
                st.rerun()
            if st.button("Delete", key=f"task_delete_{task['id']}"):
                user["tasks"].remove(task)
                if st.session_state.get("edit_task_id") == task["id"]:
                    st.session_state.pop("edit_task_id", None)
                save_store(store)
                st.rerun()


store = load_store()
if "email" not in st.session_state or st.session_state.email not in store["users"]:
    auth_screen(store)
else:
    app_screen(store, st.session_state.email)
