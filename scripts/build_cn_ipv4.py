from __future__ import annotations

import ipaddress
import time
import urllib.request
from pathlib import Path


SOURCES = (
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo-lite/geoip/cn.list",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geoip/cn.list",
)


def download_text(url: str) -> str:
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "cn-ipv4-auto-update"})
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read().decode("utf-8-sig")
        except Exception as error:
            last_error = error
            if attempt < 2:
                time.sleep(2**attempt)
    raise RuntimeError(f"Unable to download {url}") from last_error


def main() -> None:
    networks: set[ipaddress.IPv4Network] = set()
    source_counts: list[int] = []

    for url in SOURCES:
        count = 0
        for raw_line in download_text(url).splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            network = ipaddress.ip_network(line, strict=False)
            if network.version != 4:
                continue
            networks.add(network)
            count += 1
        source_counts.append(count)

    if not networks:
        raise RuntimeError("No IPv4 networks were produced")

    merged = list(ipaddress.collapse_addresses(networks))
    repo_root = Path(__file__).resolve().parents[1]
    output = repo_root / "cn-ipv4-merged.list"
    output.write_text("\n".join(map(str, merged)) + "\n", encoding="utf-8", newline="\n")

    print(f"Source IPv4 rules: {source_counts}")
    print(f"Exact unique CIDRs: {len(networks)}")
    print(f"Collapsed CIDRs: {len(merged)}")
    print(f"Covered IPv4 addresses: {sum(network.num_addresses for network in merged)}")


if __name__ == "__main__":
    main()
