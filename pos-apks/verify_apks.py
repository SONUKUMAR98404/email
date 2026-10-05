#!/usr/bin/env python3
"""Inventory downloaded POS APK/XAPK files.

For each file in the download directory, records the package name and version
from the manifest, size, SHA-256, and the SHA-256 of the signing certificate.
Compare the certificate digest against a copy of the same app from Google Play
to spot repackaged builds.

Usage: python3 verify_apks.py [apk_dir] [out_csv]
"""
import csv
import hashlib
import io
import json
import logging
import sys
import zipfile
from pathlib import Path

from androguard.core.apk import APK

logging.disable(logging.CRITICAL)
try:  # androguard 4 logs through loguru
    from loguru import logger
    logger.remove()
except ImportError:
    pass


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def base_apk_bytes(path):
    """Return the bytes of the base APK (the file itself, or the one inside an XAPK)."""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if "AndroidManifest.xml" in names:
            return Path(path).read_bytes(), 1
        apks = [n for n in names if n.endswith(".apk")]
        pkg = None
        if "manifest.json" in names:
            pkg = json.loads(z.read("manifest.json")).get("package_name")
        base = next((n for n in apks if pkg and n == f"{pkg}.apk"), None)
        base = base or next((n for n in apks if n == "base.apk"), None)
        base = base or max(apks, key=lambda n: z.getinfo(n).file_size)
        return z.read(base), len(apks)


def cert_digests(apk):
    certs = apk.get_certificates_der_v3() or apk.get_certificates_der_v2() or [
        c.dump() for c in apk.get_certificates_v1()
    ]
    return ";".join(hashlib.sha256(c).hexdigest() for c in certs)


def main():
    apk_dir = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "apks")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else apk_dir / "inventory.csv")
    rows = []
    for path in sorted(apk_dir.glob("*.*apk")):
        row = {"file": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        try:
            data, n_apks = base_apk_bytes(path)
            apk = APK(io.BytesIO(data).read(), raw=True)
            row.update(
                package=apk.get_package(),
                version_name=apk.get_androidversion_name(),
                version_code=apk.get_androidversion_code(),
                min_sdk=apk.get_min_sdk_version(),
                target_sdk=apk.get_target_sdk_version(),
                split_apks=n_apks,
                signed_v1=apk.is_signed_v1(),
                signed_v2=apk.is_signed_v2(),
                signed_v3=apk.is_signed_v3(),
                cert_sha256=cert_digests(apk),
                status="ok",
            )
        except Exception as e:  # corrupt or unparsable file
            row["status"] = f"error: {e}"
        rows.append(row)
        print(f"{row.get('status'):<6} {path.name} {row.get('version_name', '')}")
    fields = ["file", "package", "version_name", "version_code", "min_sdk", "target_sdk",
              "split_apks", "bytes", "sha256", "signed_v1", "signed_v2", "signed_v3",
              "cert_sha256", "status"]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} files -> {out}")


if __name__ == "__main__":
    main()
