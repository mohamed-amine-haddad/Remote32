import sqlite3

conn = sqlite3.connect("remote32.db")
cursor = conn.cursor()

boards = [
    ("Nucleo-F401RE", "066FFF3632524B3043205333", 3333, 4444, 6666, "localhost"),
    ("Nucleo-F103RB", "066DFF535550755187063847", 3334, 4445, 6667, "localhost"),
]

for name, serial, gdb_port, telnet_port, tcl_port, pi_host in boards:
    # Insert boards in db
    cursor.execute("""
        INSERT OR IGNORE INTO boards (name, serial_number, config_file, gdb_port, telnet_port, tcl_port, pi_host)
        VALUES (?, ?, '', ?, ?, ?, ?)
    """, (name, serial, gdb_port, telnet_port, tcl_port, pi_host))

    # Assign a unique .cfg file to each board
    cursor.execute("SELECT id FROM boards WHERE serial_number = ?", (serial,))
    board_id = cursor.fetchone()[0]

    model = name.lower().replace("-", "_")
    config_file = f"configs/devices/{model}_{board_id}.cfg"

    cursor.execute("UPDATE boards SET config_file = ? WHERE id = ?", (config_file, board_id))

conn.commit()
conn.close()
