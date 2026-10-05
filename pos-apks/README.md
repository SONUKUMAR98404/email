# POS Android apps on APKPure

`pos_apps.csv` lists 74 point-of-sale Android apps that have APKPure pages: package name, app name, category and APKPure URL. They were found with web searches over apkpure.com in October 2026.

| Category | Count |
|---|---|
| Retail POS (incl. offline and Spanish-language) | 20 |
| Indonesian "kasir" POS | 15 |
| Restaurant / F&B POS | 12 |
| Retail + restaurant POS | 6 |
| mPOS / card payment / SoftPOS | 10 |
| Odoo ERP POS clients | 5 |
| Pharmacy POS | 3 |
| POS companions (scanner, reporting, CRM) | 3 |

Some vendor apps are hardware-locked or need a merchant account to get past login: Toast, Lightspeed, Shopify, Clover-style terminals and most mPOS apps. The offline ones run without an account: Loyverse, Tunder, Simply POS, Oh My POS, POS App Offline and the Zobaze apps.

## Downloading the APKs

```bash
./download_pos_apks.sh            # reads pos_apps.csv, writes to ./apks/
```

The script requests `https://d.apkpure.com/b/APK/<package>?version=latest`. If that fails it tries the XAPK variant. It checks that each file is a valid zip and saves it as `<package>.apk`, or `<package>.xapk` for split-APK bundles. Results go to `apks/download_log.csv` with the size and SHA-256 of each file. If you run it again, it skips files that are already downloaded.

If APKPure blocks a package or doesn't have it, the log marks it `failed`. Open its `apkpure_url` from the CSV and download it by hand.

## Downloading with apkeep (what was used in practice)

From servers that get APKPure's Cloudflare challenge, the script above fails. EFF's [apkeep](https://github.com/EFForg/apkeep) uses APKPure's app API instead:

```bash
cargo install apkeep
tail -n +2 pos_apps.csv | cut -d, -f1 > packages.txt
apkeep -c packages.txt -d apk-pure -o 'acknowledge_dangers=true' -r 3 -s 1000 apks/
```

Hosts needed: `api.pureapk.com`, `download.pureapk.com`, `data.winudf.com`.

APKPure is an unofficial mirror that has been caught serving repackaged apps with malware. Install these only on an emulator or a dedicated test device.

## Verifying downloads

```bash
pip install androguard
python3 verify_apks.py apks/     # writes apks/inventory.csv
```

For each file this records the package, version, SDK levels, size, SHA-256, signature schemes and the SHA-256 of the signing certificate. Compare that certificate digest against the same app from Google Play to spot re-signed (modified) builds.

## Download results (2026-10-05)

71 of 74 apps downloaded (2.2 GB: 34 single APKs, 37 XAPK split bundles). All 71 parse as valid APKs whose package name matches the list; see `apk_inventory.csv` for versions, checksums and signing-certificate digests.

APKPure's API returned no versions for three apps, so they could not be downloaded: `com.shopify.pos` (Shopify POS), `com.nowpos.pos` (PayVoo POS) and `com.smartpesa.weepay` (WeePay mPOS).
