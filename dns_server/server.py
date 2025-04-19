"""
Minimal authoritative DNS server.

* Listens on UDP (default : 0.0.0.0:53)
* Answers **A** queries for names that appear in `example.zone`
  (or falls back to a built-in dict if the file is missing).
* No recursion, no TCP fallback, no zone transfers - kept intentionally
  simple for an academic assignment.

Run with:
    python -m dns_server.server --port 5353
"""
import logging
import socket
from pathlib import Path
from typing import Optional

from dnslib import DNSRecord, DNSHeader, RR, A, QTYPE  # pip install dnslib

# ---------------------------------------------------------------------------#
# Load zone data                                                             #
# ---------------------------------------------------------------------------#

from .zone import load_zone  # relative import

DEFAULT_ZONE: dict[str, str] = {
    "example.com.": "93.184.216.34",
    "rit.edu.":      "129.21.1.16",
}

# Overlay records from example.zone
_zone_file = Path(__file__).with_suffix(".zone")  # dns_server/server.zone
ZONE: dict[str, str] = DEFAULT_ZONE.copy()
if _zone_file.exists():
    try:
        ZONE.update(load_zone(_zone_file))
    except Exception as exc:                      
        logging.warning("Failed to load %s (%s); using defaults", _zone_file, exc)

# ---------------------------------------------------------------------------#
# Helper functions                                                           #
# ---------------------------------------------------------------------------#
def resolve(qname: str) -> Optional[RR]:
    """
    Look up *qname* in **ZONE**.

    Parameters
    ----------
    qname : str
        Domain name ending with a dot.

    Returns
    -------
    dnslib.RR | None
        An ``A`` Resource Record or ``None`` if the name is unknown.
    """
    ip = ZONE.get(qname.lower())
    if ip:
        return RR(qname, QTYPE.A, rdata=A(ip), ttl=300)
    return None

# ---------------------------------------------------------------------------#
# Core server loop                                                           #
# ---------------------------------------------------------------------------#
def serve(host: str = "0.0.0.0", port: int = 53) -> None:
    """
    Start an authoritative UDP DNS server.

    Parameters
    ----------
    host : str
        Interface to bind.
    port : int
        UDP port to bind.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    logging.info("DNS server listening on %s:%d", host, port)

    try:
        while True:
            data, addr = sock.recvfrom(512)        # 512 B = RFC 1035 max size
            request = DNSRecord.parse(data)        # decode wire format
            qname = str(request.q.qname)
            logging.debug("Query %s from %s", qname, addr)

            # Build skeleton reply header
            reply = DNSRecord(
                DNSHeader(
                    id=request.header.id,          # echo client ID
                    qr=1,                          # QR = response
                    aa=1,                          # Authoritative Answer
                    ra=0,                          # Recursion (none rn)
                ),
                q=request.q,
            )

            answer = resolve(qname)
            if answer:
                reply.add_answer(answer)
            else:                                  # NXDOMAIN
                reply.header.rcode = 3             # RCODE 3 = NXDOMAIN

            sock.sendto(reply.pack(), addr)        # encode & send
    except KeyboardInterrupt:                      # Graceful shutdown
        logging.info("Shutting down DNS server")


# ---------------------------------------------------------------------------#
# entry‑point                                                               #
# ---------------------------------------------------------------------------#
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Minimal authoritative DNS server")
    parser.add_argument("--host", default="0.0.0.0", help="interface to bind (default: all)")
    parser.add_argument("--port", type=int, default=53, help="UDP port (use 5353 for non‑root)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    serve(host=args.host, port=args.port)