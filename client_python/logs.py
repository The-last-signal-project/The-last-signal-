import inspect
import json
from .packet import Packet, PacketType
def log(client, level, message):
    frame = inspect.currentframe().f_back

    payload = {
        "level": level,
        "module": frame.f_globals["__name__"],
        "file": frame.f_code.co_filename,
        "line": frame.f_lineno,
        "message": message,
    }

    client.send_packet(
        Packet(
            PacketType.LOG,
            json.dumps(payload).encode("utf-8"),
        )
    )
