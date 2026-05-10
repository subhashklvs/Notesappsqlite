# 📝 Notes Management System
### Built with Flask + SQLite + Bootstrap 5

---

## 📁 Project Structure

```
notes_app/
│
├── app.py                  ← Main Flask application
├── schema.sql              ← SQLite schema (auto-applied on first run)
├── requirements.txt        ← Python dependencies
├── notes.db                ← SQLite database file (auto-created)
│
└── templates/
    ├── base.html           ← Base layout (navbar, footer)
    ├── login.html          ← Login page
    ├── register.html       ← Registration page
    ├── forgot.html         ← Forgot password page
    ├── viewall.html        ← All notes dashboard
    ├── addnote.html        ← Add new note form
    ├── viewnote.html       ← View single note
    └── updatenote.html     ← Edit note form
```

---

## ⚙️ Setup Instructions

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```
> No MySQL server, mysqlclient, or Flask-MySQLdb needed — SQLite is built into Python.

### Step 2 — Run the app
```bash
python app.py
```
The app automatically creates **notes.db** and all tables on the very first run.

Open your browser and go to: **http://127.0.0.1:5000**

### Optional — Inspect the database manually
```bash
sqlite3 notes.db
.tables
SELECT * FROM users;
.quit
```

---

## 🔗 Routes Summary

| Route                     | Method    | Description            |
|---------------------------|-----------|------------------------|
| `/`                       | GET       | Redirects to login     |
| `/register`               | GET/POST  | User registration      |
| `/login`                  | GET/POST  | User login             |
| `/logout`                 | GET       | Logout & clear session |
| `/forgot`                 | GET/POST  | Reset password         |
| `/viewall`                | GET       | View all notes         |
| `/addnote`                | GET/POST  | Add new note           |
| `/viewnotes/<id>`         | GET       | View single note       |
| `/updatenote/<id>`        | GET/POST  | Edit a note            |
| `/deletenote/<id>`        | GET       | Delete a note          |

---

## 🔐 Security
- Passwords hashed using `werkzeug.security.generate_password_hash`
- Notes are user-scoped (users can only access their own notes)
- Flask sessions protect all note routes
- `ON DELETE CASCADE` auto-deletes notes when a user is removed

---

## 🗄️ SQLite vs MySQL — What Changed

| | MySQL (old) | SQLite (new) |
|---|---|---|
| Driver | `Flask-MySQLdb`, `mysqlclient` | Built-in `sqlite3` |
| Placeholders | `%s` | `?` |
| Config | Host / user / password in app.py | Just a `.db` file path |
| Setup | MySQL server required | Zero setup |
| DB file | External server | `notes.db` in project folder |
