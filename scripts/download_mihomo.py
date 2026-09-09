from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
import urllib.request
from pathlib import Path


API_URL = "https://api.github.com/repos/MetaCubeX/mihomo/releases/latest"
ASSET_PATTERNS = (
    re.compile(r"^mihomo-linux-amd64-v1-.*\.gz$"),
    re.compile(r"^mihomo-linux-amd64-compatible-.*\.gz$"),
    re.compile(r"^mihomo-linux-amd64-.*\.gz$"),
)


def request(url: str) -> urllib.request.Request:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "cn-ipv4-auto-update",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(url, headers=headers)


def main() -> None:
    with urllib.request.urlopen(request(API_URL), timeout=60) as response:
        release = json.load(response)

    asset = None
    for pattern in ASSET_PATTERNS:
        asset = next((item for item in release["assets"] if pattern.match(item["name"])), None)
        if asset:
            break
    if not asset:
        raise RuntimeError("No compatible Linux AMD64 Mihomo release asset was found")

    with urllib.request.urlopen(request(asset["browser_download_url"]), timeout=180) as response:
        archive = response.read()

    digest = asset.get("digest")
    if digest and digest.startswith("sha256:"):
        actual = hashlib.sha256(archive).hexdigest()
        expected = digest.removeprefix("sha256:")
        if actual != expected:
            raise RuntimeError(f"Mihomo checksum mismatch: {actual} != {expected}")

    repo_root = Path(__file__).resolve().parents[1]
    tool_dir = repo_root / "_tools"
    tool_dir.mkdir(exist_ok=True)
    executable = tool_dir / "mihomo"
    executable.write_bytes(gzip.decompress(archive))
    executable.chmod(0o755)

    print(f"Downloaded {asset['name']} from {release['tag_name']}")


if __name__ == "__main__":
    main()
