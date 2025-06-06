# Minimal Authoritative DNS Server

> **Author:** Brian Tokumoto bht8183@g.rit.edu

A lightweight DNS server written in Python.  
It answers **A‑record** queries for names defined in a simple zone file (or in the built‑in defaults).  
No recursion, no TCP fallback implemented.

---

1  Quick Start

# 1. install deps
pip install -r requirements.txt

# 2. launch the server on an unprivileged port
python -m dns_server.server --port 5353


2  Command‑Line Examples

Purpose	Command:
Start server: python -m dns_server.server
Start server on port 8053:	python -m dns_server.server --port 8053
Query with dig:	dig '@127.0.0.1' -p 8053 example.com A
Run automated tests:	pytest -q

3  Zone Files
A sample file dns_server/server.zone is read automatically if it exists.

Format: one A record per line — nothing else is parsed.

example.com. 300 IN A 93.184.216.34
rit.edu.     300 IN A 129.21.1.16