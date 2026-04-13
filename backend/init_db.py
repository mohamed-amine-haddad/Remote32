import sqlite3

conn = sqlite3.connect("remote32.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS boards (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    serial_number TEXT    NOT NULL UNIQUE,
    config_file   TEXT    NOT NULL,
    gdb_port      INTEGER NOT NULL UNIQUE,
    telnet_port   INTEGER NOT NULL UNIQUE,
    tcl_port      INTEGER NOT NULL UNIQUE,
    status        TEXT    NOT NULL DEFAULT 'idle',
    openocd_pid   INTEGER,
    pi_host       TEXT    NOT NULL
);""")

cursor.execute("""
ALTER TABLE boards ADD COLUMN pi_host TEXT NOT NULL DEFAULT 'localhost';
""")


conn.commit()
conn.close()
