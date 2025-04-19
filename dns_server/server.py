from dnslib import DNSRecord, DNSHeader, RR, A, QTYPE   # pip install dnslib
import socket, logging

# tests/conftest.py
import sys, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(root))


ZONE = {                   # hard‑coded zone
    "example.com.": "93.184.216.34",
    "rit.edu.":      "129.21.1.16",
}

def resolve(qname: str):
    ip = ZONE.get(qname.lower())
    if ip:
        return RR(qname, QTYPE.A, rdata=A(ip), ttl=300)

def serve(host="0.0.0.0", port=53):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    logging.info("DNS server listening on %s:%d", host, port)

    while True:
        
        data, addr = sock.recvfrom(512)
        request = DNSRecord.parse(data)
        qname = str(request.q.qname)
        logging.debug("Query %s from %s", qname, addr)

        reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=0), q=request.q)
        answer = resolve(qname)
        if answer:
            reply.add_answer(answer)
        else:                       # NXDOMAIN
            reply.header.rcode = 3

        sock.sendto(reply.pack(), addr)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    serve()