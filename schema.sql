-- ================================================
--  Notes Management System — SQLite Database Schema
--  NOTE: The app auto-creates this on first run.
--  To apply manually: sqlite3 notes.db < schema.sql
-- ================================================

CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email    TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
    id         INTEGER   PRIMARY KEY AUTOINCREMENT,
    title      TEXT      NOT NULL,
    content    TEXT      NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id    INTEGER   NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
