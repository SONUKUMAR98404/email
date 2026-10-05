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
