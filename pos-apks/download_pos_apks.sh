#!/usr/bin/env bash
# Download every app in pos_apps.csv from APKPure's direct-download endpoint.
# Usage: ./download_pos_apks.sh [csv] [out_dir]
# Needs curl and unzip. Apps published as split APKs come back as .xapk bundles
# (install them with `adb install-multiple` after unzipping, or with the APKPure app).
set -u

CSV="${1:-$(dirname "$0")/pos_apps.csv}"
OUT="${2:-$(dirname "$0")/apks}"
UA="Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36"
mkdir -p "$OUT"
LOG="$OUT/download_log.csv"
echo "package,status,file,bytes,sha256" > "$LOG"

fetch() { # $1=package $2=APK|XAPK $3=dest
  curl -sSL --retry 3 --retry-delay 2 -m 600 -A "$UA" \
    -o "$3" -w '%{http_code}' "https://d.apkpure.com/b/$2/$1?version=latest"
}

tail -n +2 "$CSV" | cut -d, -f1 | while read -r pkg; do
  [ -z "$pkg" ] && continue
  if ls "$OUT/$pkg".*apk >/dev/null 2>&1; then echo "skip  $pkg (already downloaded)"; continue; fi
  tmp="$OUT/$pkg.part"
  status=failed; file=""
  for kind in APK XAPK; do
    code=$(fetch "$pkg" "$kind" "$tmp")
    if [ "$code" = 200 ] && unzip -l "$tmp" >/dev/null 2>&1; then
      if unzip -l "$tmp" | grep -q 'AndroidManifest.xml$'; then ext=apk; else ext=xapk; fi
      file="$OUT/$pkg.$ext"; mv "$tmp" "$file"; status=ok; break
    fi
  done
  rm -f "$tmp"
  if [ "$status" = ok ]; then
    bytes=$(wc -c < "$file"); sha=$(sha256sum "$file" | cut -d' ' -f1)
    echo "ok    $pkg -> $(basename "$file") ($bytes bytes)"
    echo "$pkg,ok,$(basename "$file"),$bytes,$sha" >> "$LOG"
  else
    echo "FAIL  $pkg (not available or blocked; try the apkpure_url in the CSV by hand)"
    echo "$pkg,failed,,," >> "$LOG"
  fi
  sleep 2  # be polite to the mirror
done
echo "Done. Results in $LOG"
