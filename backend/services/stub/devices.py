# STUB — delegates to stub/applications, filtered to device-type entries
# (applications with no control boards, currently IDs 4–7).
# Replace with real backend/services/devices.py when implementing.

import backend.services.stub.applications as _apps

_DEVICE_IDS = {4, 5, 6, 7}


def get_all(session) -> list[dict]:
    return [
        {"id": a["id"], "name": a["name"], "status": a["status"], "description": a["description"]}
        for a in _apps._APPLICATIONS.values()
        if a["id"] in _DEVICE_IDS
    ]
