"""
tests/test_server.py

Pytest integration tests for the *authoritative* DNS server.

* Spin up the UDP server in a on a random high port
  (40 000-50 000) so we don't need root or collide with another test run.
* Use dnslib to craft/parse real DNS packets.
* tests:
    1. Known names resolve with RCODE 0 and the right A record.
    2. Unknown names produce RCODE 3 (NXDOMAIN).
"""

import random
import socket
import threading
import time
from typing import Tuple

from dnslib import DNSRecord
from dns_server.server import serve

# ---------------------------------------------------------------------------#
# Test helpers                                                               #
# ---------------------------------------------------------------------------#
def _start(port: int) -> threading.Thread:
    """
    Launch the DNS server in a background thread.

    Parameters
    ----------
    port : int | UDP port the server should bind to.

    Returns
    -------
    threading.Thread
        The daemon thread running ``serve()``.
    """
    t = threading.Thread(
        target=serve,
        kwargs={"host": "127.0.0.1", "port": port},
        daemon=True,             # dies automatically when pytest exits
    )
    t.start()
    time.sleep(0.05)             # give bind() a moment
    return t


def _query(name: str, port: int) -> DNSRecord:
    """
    Send an A‑query to name via UDP and parse the reply.

    Returns
    -------
    dnslib.DNSRecord
    """
    q = DNSRecord.question(name, "A")       
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1.0)
    sock.sendto(q.pack(), ("127.0.0.1", port))
    data, _ = sock.recvfrom(512)
    return DNSRecord.parse(data)


# ---------------------------------------------------------------------------#
# Tests                                                                      #
# ---------------------------------------------------------------------------#
def test_example_resolves() -> None:
    """
    ``example.com.`` must resolve to 93.184.216.34 with RCODE 0.
    """
    port = random.randint(40_000, 50_000)
    _start(port)

    resp = _query("example.com.", port)

    assert resp.header.rcode == 0                      # NOERROR
    assert resp.rr[0].rdata.toZone() == "93.184.216.34"


def test_nxdomain() -> None:
    """
    Any unknown name should return NXDOMAIN (RCODE 3).
    """
    port = random.randint(40_000, 50_000)
    _start(port)

    resp = _query("no.such.name.", port)

    assert resp.header.rcode == 3                      # NXDOMAIN