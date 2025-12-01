#!/usr/bin/env python3
"""
create_users_table.py

Create a `users` table in `brain_etl.db` and populate it with:
- one admin user (`admin` / `password123`)
- patient users for each distinct `patient_id` in `mri_scans`, with default
  password equal to their patient_id (as a string).

This script creates a timestamped backup of the DB before making changes.
Passwords are stored using PBKDF2-HMAC-SHA256 with a per-user salt.
"""
from __future__ import annotations
import sqlite3
import os
import shutil
from datetime import datetime
import hashlib
import binascii
import secrets


DB_NAME = 'brain_etl.db'
ITERATIONS = 100_000


def backup_db(db_path: str) -> str:
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    backup = f"{db_path}.bak.{ts}"
    shutil.copy2(db_path, backup)
    print(f"Backed up DB: {backup}")
    return backup


def hash_password(password: str, salt: bytes | None = None, iterations: int = ITERATIONS) -> tuple[str, str, int]:
    if salt is None:
        salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    return binascii.hexlify(dk).decode('ascii'), binascii.hexlify(salt).decode('ascii'), iterations


def ensure_users_table(conn: sqlite3.Connection):
    conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL,
        password_salt TEXT NOT NULL,
        iterations INTEGER NOT NULL,
        role TEXT NOT NULL,
        patient_id INTEGER,
        created_on TEXT NOT NULL
    )
    ''')


def user_exists(conn: sqlite3.Connection, username: str) -> bool:
    cur = conn.execute('SELECT 1 FROM users WHERE username = ? LIMIT 1', (username,))
    return cur.fetchone() is not None


def insert_user(conn: sqlite3.Connection, username: str, password: str, role: str, patient_id: int | None = None):
    if user_exists(conn, username):
        print(f"User already exists, skipping: {username}")
        return False
    pwd_hash, salt_hex, iters = hash_password(password)
    conn.execute(
        'INSERT INTO users (username, password_hash, password_salt, iterations, role, patient_id, created_on) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (username, pwd_hash, salt_hex, iters, role, patient_id, datetime.utcnow().isoformat())
    )
    print(f"Inserted user: {username} (role={role})")
    return True


def main():
    # use central helper to determine DB path
    from db import get_db_path
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    backup_db(db_path)

    conn = sqlite3.connect(db_path)
    ensure_users_table(conn)

    # Add admin user
    insert_user(conn, 'admin', 'password123', 'admin', None)

    # Add radiologist users (rad1..rad5) with default password 'password123'
    rad_count = 0
    for i in range(1, 6):
        rad_name = f"rad{i}"
        if insert_user(conn, rad_name, 'password123', 'radiologist', None):
            rad_count += 1

    # Add patient users with default password = their patient_id
    cur = conn.execute('SELECT DISTINCT patient_id FROM mri_scans WHERE patient_id IS NOT NULL')
    added = 0
    for (pid,) in cur.fetchall():
        username = str(pid)
        # default password is the patient id string
        ok = insert_user(conn, username, username, 'patient', pid)
        if ok:
            added += 1

    conn.commit()
    conn.close()

    print(f"Done. Added {added} patient users and {rad_count} radiologist users.")


if __name__ == '__main__':
    main()
