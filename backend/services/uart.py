import shlex
import socket
import threading
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

_buffers:    dict[int, list[dict]]       = {}
_next_id:    dict[int, int]              = {}
_readers:    dict[int, threading.Thread] = {}
_stop_flags: dict[int, threading.Event]  = {}
_locks:      dict[int, threading.Lock]   = {}


def _append(session_id: int, direction: str, text: str) -> None:
    lock = _locks.setdefault(session_id, threading.Lock())
    with lock:
        buf = _buffers.setdefault(session_id, [])
        nid = _next_id.get(session_id, 1)
        buf.append({
            "id":        nid,
            "direction": direction,
            "text":      text,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        })
        _next_id[session_id] = nid + 1


def start_reader(session_id: int, target_cfg) -> None:
    t = _readers.get(session_id)
    if t and t.is_alive():
        return
    stop = threading.Event()
    _stop_flags[session_id] = stop
    _buffers.setdefault(session_id, [])
    _next_id.setdefault(session_id, 1)
    _locks.setdefault(session_id, threading.Lock())
    t = threading.Thread(
        target=_reader_loop,
        args=(session_id, target_cfg, stop),
        daemon=True,
        name=f"uart-reader-{session_id}",
    )
    _readers[session_id] = t
    t.start()
    logger.info("[uart] reader started for session %d on %s", session_id, target_cfg.serial_port)


def stop_reader(session_id: int) -> None:
    flag = _stop_flags.pop(session_id, None)
    if flag:
        flag.set()
    _readers.pop(session_id, None)
    logger.info("[uart] reader stopped for session %d", session_id)


def _reader_loop(session_id: int, target_cfg, stop: threading.Event) -> None:
    try:
        from backend.services.ssh import ssh_connect
    except ImportError:
        from services.ssh import ssh_connect

    port = target_cfg.serial_port
    baud = target_cfg.baud_rate

    while not stop.is_set():
        try:
            client    = ssh_connect(target_cfg.pi)
            transport = client.get_transport()
            channel   = transport.open_session()
            channel.settimeout(1.0)
            channel.exec_command(
                f"stty -F {port} {baud} cs8 -cstopb -parenb raw -echo && cat {port}"
            )
            raw = b""
            while not stop.is_set():
                try:
                    chunk = channel.recv(1024)
                    if not chunk:
                        break
                    raw += chunk
                    while b"\n" in raw:
                        line, raw = raw.split(b"\n", 1)
                        text = line.rstrip(b"\r").decode("utf-8", errors="replace").strip()
                        if text:
                            _append(session_id, "rx", text)
                except (socket.timeout, TimeoutError):
                    continue
            channel.close()
        except Exception as e:
            if stop.is_set():
                break
            logger.warning("[uart] session %d error: %s — retry in 3s", session_id, e)
            time.sleep(3)


def get_messages(session_id: int, since_id: int = 0) -> dict:
    lock = _locks.get(session_id)
    if lock is None:
        return {"messages": []}
    with lock:
        buf  = _buffers.get(session_id, [])
        msgs = [m for m in buf if m["id"] > since_id]
    return {"messages": msgs}


def send_text(session_id: int, target_cfg, text: str) -> None:
    try:
        from backend.services.ssh import ssh_connect
    except ImportError:
        from services.ssh import ssh_connect

    client = ssh_connect(target_cfg.pi)
    port   = target_cfg.serial_port
    baud   = target_cfg.baud_rate
    quoted = shlex.quote(text + "\n")
    client.exec_command(f"stty -F {port} {baud} -opost && printf {quoted} > {port}")
    _append(session_id, "tx", text)
