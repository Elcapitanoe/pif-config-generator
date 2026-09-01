# PIF Config Generator

Automated pipeline for tracking Android build properties and compiling validated Play Integrity Fix (PIF) JSON profiles.

```
Upstream Repositories
  ├── Pixel-Props/build.prop (Stable)
  └── Elcapitanoe/Build-Prop-BETA (Beta)
            │
            ▼
  [ pif-gen check ] ─── Poll tags vs local state/
            │
            ▼ (On tag update)
  [ pif-gen build ] ─── Download ZIPs ──> Extract system.prop ──> Parse & Validate
            │
            ▼
  [ pif-gen publish ] ─ Deploy unified release bundle (vYYYY.MM.DD)
```

---

## Schema Reference

Properties are resolved across partition namespaces (`system_ext` > `system` > `product` > `vendor`) and validated against Pydantic schemas.

### Extended Profile Schema

| Key | Property Resolution Order | Description |
|:---|:---|:---|
| `ID` | `ro.system_ext.build.id` → `ro.system.build.id` → `ro.build.id` → `ro.vendor.build.id` | Android build identifier |
| `BRAND` | `ro.product.system_ext.brand` → `ro.product.system.brand` → `ro.product.brand` | Device brand (`google`) |
| `DEVICE` | `ro.product.system_ext.device` → `ro.product.system.device` → `ro.product.device` | Hardware board codename |
| `MANUFACTURER` | `ro.product.system_ext.manufacturer` → `ro.product.manufacturer` | Hardware manufacturer |
| `MODEL` | `ro.product.system_ext.model` → `ro.product.system.model` → `ro.product.model` | Commercial model name |
| `PRODUCT` | `ro.product.system_ext.name` → `ro.product.system.name` → `ro.product.name` | Product codename |
| `FINGERPRINT` | `ro.system_ext.build.fingerprint` → `ro.build.fingerprint` → `ro.vendor.build.fingerprint` | Build fingerprint |
| `SECURITY_PATCH` | `ro.build.version.security_patch` → parsed date pattern | Patch date (`YYYY-MM-DD`) |
| `DEVICE_INITIAL_SDK_INT` | `ro.product.first_api_level` → `ro.board.first_api_level` → `ro.system.build.version.sdk` | Factory launch SDK |
| `RELEASE` | `ro.system_ext.build.version.release` → `ro.build.version.release` | Android OS version |
| `TYPE` | `ro.system_ext.build.type` → `ro.build.type` | Build type (`user`) |
| `TAG` | `ro.system_ext.build.tags` → `ro.build.tags` | Signing key tag (`release-keys`) |
| `DEBUG` | Evaluated (`ro.debuggable == 1` or `TYPE != user`) | Debug build flag (`false`) |

### Generated Output Example

```json
{
  "ID": "CP41.260814.003.B1",
  "BRAND": "google",
  "DEVICE": "komodo",
  "MANUFACTURER": "Google",
  "FINGERPRINT": "google/komodo_beta/komodo:17/CP41.260814.003.B1/16166531:user/release-keys",
  "MODEL": "Pixel 9 Pro XL",
  "PRODUCT": "komodo_beta",
  "SECURITY_PATCH": "2026-08-14",
  "DEVICE_INITIAL_SDK_INT": "34",
  "TYPE": "user",
  "TAG": "release-keys",
  "RELEASE": "17",
  "DEBUG": false,
  "spoofBuild": "1",
  "spoofProps": "0",
  "spoofProvider": "0",
  "spoofSignature": "0",
  "spoofVendingSdk": "0",
  "verboseLogs": "0"
}
```

---

## Installation

```bash
git clone https://github.com/Elcapitanoe/pif-config-generator.git
cd pif-config-generator
pip install -e .
```

---

## CLI Reference

`pif-gen` provides commands for checking, extracting, building, and publishing profiles.

### 1. Check Upstream

Compares remote releases against local state files (`state/last_<channel>_tag.txt`):

```bash
pif-gen check --state-dir state
```

### 2. Build Single File

Generates a JSON profile from a local `system.prop`:

```bash
pif-gen build --file path/to/system.prop --output-dir output
```

### 3. Build Batch (CI Mode)

Extracts and validates profiles from an asset URL list:

```bash
pif-gen build \
  --channel beta \
  --assets-json '[{"name": "Komodo_beta.zip", "url": "https://..."}]' \
  --output-dir output \
  --manifest output/manifest.txt
```

### 4. Publish Release

Deploys consolidated artifacts to GitHub Releases:

```bash
export GITHUB_TOKEN="ghp_xxx"
pif-gen publish \
  --repo "Elcapitanoe/pif-config-generator" \
  --manifest output/manifest.txt
```

---

## Testing

```bash
python3 -m unittest discover tests
```

---
