import socket, random, threading, time
from dnslib import DNSRecord
from dns_server.server import serve

def _start(port):
    t = threading.Thread(target=serve,
                         kwargs={"host": "127.0.0.1", "port": port},
                         daemon=True)
    t.start()
    time.sleep(0.05)
    return t

def _query(name, port):
    q = DNSRecord.question(name, "A")      # ← fixed
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)
    sock.sendto(q.pack(), ("127.0.0.1", port))
    data, _ = sock.recvfrom(512)
    return DNSRecord.parse(data)

def test_example_resolves():
    port = random.randint(40000, 50000)
    _start(port)
    resp = _query("example.com.", port)
    assert resp.header.rcode == 0
    assert resp.rr[0].rdata.toZone() == "93.184.216.34"

def test_nxdomain():
    port = random.randint(40000, 50000)
    _start(port)
    resp = _query("no.such.name.", port)
    assert resp.header.rcode == 3