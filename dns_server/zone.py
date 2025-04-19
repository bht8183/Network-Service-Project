"""
dns_server.zone
===============

A tiny, zone-file parser for this assignment.

* Accepts one text file that contains A records only.
* Ignores TTL, class, blank lines, comments, and everything else.
* Returns a plain ``dict`` mapping fully-qualified names to IPv4 strings.

Example zone file::

    example.com.     300   IN   A   93.184.216.34
    rit.edu.         300   IN   A   129.21.1.16
"""

from pathlib import Path
import re
from typing import Dict

# ---------------------------------------------------------------------------#
# Regular expression to capture NAME ... A IP lines                        #
# ---------------------------------------------------------------------------#
# Groups:
#   1 → domain name 
#   2 → IPv4 address
_A_RECORD = re.compile(  # this was a paint to figure out. I used AI for this sorry.
    r""" ^\s*                          # leading whitespace
          ([A-Za-z0-9.-]+) \s+         # domain name (group 1)
          \d+ \s+ IN \s+ A \s+         # TTL, class, type (ignored)
          ([\d.]+)                     # IPv4 address (group 2)
      """,
    re.VERBOSE,
)


# ---------------------------------------------------------------------------#
# Public API                                                                 #
# ---------------------------------------------------------------------------#
def load_zone(path: str | Path) -> Dict[str, str]:
    """
    Parse minimal zone file and return.

    Parameters
    ----------
    path : str | Path to zone file.

    Returns
    -------
    dict[str, str]
        Mapping from lower-cased FQDN to dotted-quad IP.
    """
    records: Dict[str, str] = {}
    text = Path(path).read_text(encoding="utf‑8")

    for line in text.splitlines():
        match = _A_RECORD.match(line)
        if not match:
            continue                                   # skip junk

        name, ip = match.groups()
        records[name.lower()] = ip                     # normalise to lower‑case

    return records