import shlex
import socket
import threading
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

_buffers:    dict[int, list[dict]]        = {}
_next_id:    dict[int, int]               = {}
_readers:    dict[tuple, threading.Thread] = {}  # (session_id, source) -> thread
_stop_flags: dict[tuple, threading.Event]  = {}  # (session_id, source) -> event
_locks:      dict[int, threading.Lock]    = {}


def _append(session_id: int, direction: str, text: str, source: str) -> None:
    lock = _locks.setdefault(session_id, threading.Lock())
    with lock:
        buf = _buffers.setdefault(session_id, [])
        nid = _next_id.get(session_id, 1)
        buf.append({
            "id":        nid,
            "direction": direction,
            "text":      text,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "source":    source,
        })
        _next_id[session_id] = nid + 1


def start_reader(session_id: int, board_cfg, source: str) -> None:
    key = (session_id, source)
    t = _readers.get(key)
    if t and t.is_alive():
        return
    stop = threading.Event()
    _stop_flags[key] = stop
    _buffers.setdefault(session_id, [])
    _next_id.setdefault(session_id, 1)
    _locks.setdefault(session_id, threading.Lock())
    t = threading.Thread(
        target=_reader_loop,
        args=(session_id, board_cfg, stop, source),
        daemon=True,
        name=f"uart-reader-{session_id}-{source}",
    )
    _readers[key] = t
    t.start()
    logger.info("[uart] %s reader started for session %d on %s", source, session_id, board_cfg.serial_port)


def stop_reader(session_id: int) -> None:
    for source in ('target', 'control'):
        key = (session_id, source)
        flag = _stop_flags.pop(key, None)
        if flag:
            flag.set()
        _readers.pop(key, None)
    logger.info("[uart] readers stopped for session %d", session_id)


def _reader_loop(session_id: int, board_cfg, stop: threading.Event, source: str) -> None:
    try:
        from backend.services.ssh import ssh_connect
    except ImportError:
        from services.ssh import ssh_connect

    port = board_cfg.serial_port
    baud = board_cfg.baud_rate

    while not stop.is_set():
        try:
            client    = ssh_connect(board_cfg.pi)
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
                            _append(session_id, "rx", text, source)
                except (socket.timeout, TimeoutError):
                    continue
            channel.close()
        except Exception as e:
            if stop.is_set():
                break
            logger.warning("[uart] session %d %s error: %s — retry in 3s", session_id, source, e)
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
    _append(session_id, "tx", text, "target")
