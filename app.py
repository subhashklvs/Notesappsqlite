from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

DATABASE = 'notes.db'


# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:

        conn.executescript('''

            CREATE TABLE IF NOT EXISTS users (

                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL

            );

            CREATE TABLE IF NOT EXISTS notes (

                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL,

                FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE

            );

        ''')


def parse_notes(rows):

    result = []

    for row in rows:

        d = dict(row)

        if isinstance(d.get('created_at'), str):

            try:
                d['created_at'] = datetime.strptime(
                    d['created_at'],
                    '%Y-%m-%d %H:%M:%S'
                )

            except:
                d['created_at'] = None

        result.append(d)

    return result


def parse_note(row):

    if row is None:
        return None

    return parse_notes([row])[0]


with app.app_context():
    init_db()


# ─────────────────────────────────────────────
# HOME
# ─────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('home.html')


# ─────────────────────────────────────────────
# ABOUT
# ─────────────────────────────────────────────
@app.route('/about')
def about():
    return render_template('about.html')


# ─────────────────────────────────────────────
# CONTACT
# ─────────────────────────────────────────────
@app.route('/contact', methods=['GET', 'POST'])
def contact():

    if request.method == 'POST':

        fullname = request.form['fullname']
        email = request.form['email']
        message = request.form['message']

        try:

            # Your Gmail
            sender_email = "subhashklvs@gmail.com"

            # Gmail App Password
            sender_password = "yajn mhmb toxu lmrx"

            

            # Email Message
            msg = MIMEMultipart()

            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = "New Contact Message From NotesApp"

            body = f"""
            Name: {fullname}

            Email: {email}

            Message:
            {message}
            """

            msg.attach(MIMEText(body, 'plain'))

            # SMTP Server
            server = smtplib.SMTP('smtp.gmail.com', 587)

            server.starttls()

            server.login(sender_email, sender_password)

            server.send_message(msg)

            server.quit()

            flash(
                'Message sent successfully!',
                'success'
            )

        except Exception as e:

            flash(
                f'Error: {str(e)}',
                'danger'
            )

        return redirect(url_for('contact'))

    return render_template('contact.html')

# ─────────────────────────────────────────────
# REGISTER
# ─────────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']

        with get_db() as conn:

            existing = conn.execute(
                'SELECT * FROM users WHERE email = ?',
                (email,)
            ).fetchone()

            if existing:

                flash(
                    'Email already registered.',
                    'danger'
                )

            elif not re.match(
                r'[^@]+@[^@]+\.[^@]+',
                email
            ):

                flash(
                    'Invalid email address.',
                    'danger'
                )

            elif not username or not password:

                flash(
                    'Please fill all fields.',
                    'danger'
                )

            else:

                hashed_pw = generate_password_hash(password)

                conn.execute(
                    '''
                    INSERT INTO users
                    (username, email, password)

                    VALUES (?, ?, ?)
                    ''',
                    (
                        username,
                        email,
                        hashed_pw
                    )
                )

                flash(
                    'Account created successfully!',
                    'success'
                )

                return redirect(url_for('login'))

    return render_template('register.html')


# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email'].strip()
        password = request.form['password']

        with get_db() as conn:

            user = conn.execute(
                'SELECT * FROM users WHERE email = ?',
                (email,)
            ).fetchone()

        if user and check_password_hash(
            user['password'],
            password
        ):

            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']

            flash(
                f"Welcome back, {user['username']}!",
                'success'
            )

            return redirect(url_for('viewall'))

        else:

            flash(
                'Invalid email or password.',
                'danger'
            )

    return render_template('login.html')


# ─────────────────────────────────────────────
# FORGOT PASSWORD
# ─────────────────────────────────────────────
@app.route('/forgot', methods=['GET', 'POST'])
def forgot():

    if request.method == 'POST':

        email = request.form['email'].strip()
        new_password = request.form['new_password']
        confirm = request.form['confirm_password']

        if new_password != confirm:

            flash(
                'Passwords do not match.',
                'danger'
            )

        else:

            with get_db() as conn:

                user = conn.execute(
                    'SELECT * FROM users WHERE email = ?',
                    (email,)
                ).fetchone()

                if user:

                    hashed_pw = generate_password_hash(
                        new_password
                    )

                    conn.execute(
                        '''
                        UPDATE users
                        SET password = ?
                        WHERE email = ?
                        ''',
                        (
                            hashed_pw,
                            email
                        )
                    )

                    flash(
                        'Password updated successfully!',
                        'success'
                    )

                    return redirect(url_for('login'))

                else:

                    flash(
                        'No account found.',
                        'danger'
                    )

    return render_template('forgot.html')


# ─────────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────────
@app.route('/logout')
def logout():

    session.clear()

    flash(
        'Logged out successfully.',
        'info'
    )

    return redirect(url_for('login'))


# ─────────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────────
@app.route('/profile')
def profile():

    if 'loggedin' not in session:
        return redirect(url_for('login'))

    with get_db() as conn:

        user = conn.execute(
            'SELECT * FROM users WHERE id = ?',
            (session['id'],)
        ).fetchone()

    return render_template(
        'profile.html',
        user=user
    )


# ─────────────────────────────────────────────
# VIEW ALL NOTES
# ─────────────────────────────────────────────
@app.route('/viewall')
def viewall():

    if 'loggedin' not in session:
        return redirect(url_for('login'))

    search = request.args.get('search')

    with get_db() as conn:

        if search:

            notes = conn.execute(
                '''
                SELECT * FROM notes

                WHERE user_id = ?
                AND (
                    title LIKE ?
                    OR content LIKE ?
                )
                ''',
                (
                    session['id'],
                    f'%{search}%',
                    f'%{search}%'
                )
            ).fetchall()

        else:

            notes = conn.execute(
                '''
                SELECT * FROM notes
                WHERE user_id = ?
                ORDER BY created_at DESC
                ''',
                (session['id'],)
            ).fetchall()

    return render_template(
        'viewall.html',
        notes=parse_notes(notes)
    )


# ─────────────────────────────────────────────
# ADD NOTE
# ─────────────────────────────────────────────
@app.route('/addnote', methods=['GET', 'POST'])
def addnote():

    if 'loggedin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        title = request.form['title'].strip()
        content = request.form['content'].strip()

        if not title or not content:

            flash(
                'Title and content are required.',
                'danger'
            )

        else:

            with get_db() as conn:

                conn.execute(
                    '''
                    INSERT INTO notes
                    (title, content, user_id)

                    VALUES (?, ?, ?)
                    ''',
                    (
                        title,
                        content,
                        session['id']
                    )
                )

            flash(
                'Note added successfully!',
                'success'
            )

            return redirect(url_for('viewall'))

    return render_template('addnote.html')


# ─────────────────────────────────────────────
# VIEW SINGLE NOTE
# ─────────────────────────────────────────────
@app.route('/viewnotes/<int:note_id>')
def viewnotes(note_id):

    if 'loggedin' not in session:
        return redirect(url_for('login'))

    with get_db() as conn:

        note = conn.execute(
            '''
            SELECT * FROM notes

            WHERE id = ?
            AND user_id = ?
            ''',
            (
                note_id,
                session['id']
            )
        ).fetchone()

    if not note:

        flash(
            'Note not found.',
            'danger'
        )

        return redirect(url_for('viewall'))

    return render_template(
        'viewnote.html',
        note=parse_note(note)
    )


# ─────────────────────────────────────────────
# UPDATE NOTE
# ─────────────────────────────────────────────
@app.route('/updatenote/<int:note_id>', methods=['GET', 'POST'])
def updatenote(note_id):

    if 'loggedin' not in session:
        return redirect(url_for('login'))

    with get_db() as conn:

        if request.method == 'POST':

            title = request.form['title'].strip()
            content = request.form['content'].strip()

            if not title or not content:

                flash(
                    'Title and content are required.',
                    'danger'
                )

            else:

                conn.execute(
                    '''
                    UPDATE notes

                    SET
                        title = ?,
                        content = ?

                    WHERE
                        id = ?
                        AND user_id = ?
                    ''',
                    (
                        title,
                        content,
                        note_id,
                        session['id']
                    )
                )

                flash(
                    'Note updated successfully!',
                    'success'
                )

                return redirect(url_for('viewall'))

        note = conn.execute(
            '''
            SELECT * FROM notes

            WHERE id = ?
            AND user_id = ?
            ''',
            (
                note_id,
                session['id']
            )
        ).fetchone()

    if not note:

        flash(
            'Note not found.',
            'danger'
        )

        return redirect(url_for('viewall'))

    return render_template(
        'updatenote.html',
        note=parse_note(note)
    )


# ─────────────────────────────────────────────
# DELETE NOTE
# ─────────────────────────────────────────────
@app.route('/deletenote/<int:note_id>')
def deletenote(note_id):

    if 'loggedin' not in session:
        return redirect(url_for('login'))

    with get_db() as conn:

        conn.execute(
            '''
            DELETE FROM notes

            WHERE id = ?
            AND user_id = ?
            ''',
            (
                note_id,
                session['id']
            )
        )

    flash(
        'Note deleted successfully.',
        'success'
    )

    return redirect(url_for('viewall'))


# ─────────────────────────────────────────────
# RUN APP
# ─────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)