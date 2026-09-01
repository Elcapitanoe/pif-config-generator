# PIF Config Generator

Automated pipeline for tracking upstream Android build properties and generating validated Play Integrity Fix (PIF) JSON profiles.

## Architecture

```text
[Upstream Repositories]
├── Pixel-Props/build.prop (Stable)
└── Elcapitanoe/Build-Prop-BETA (Beta)
        │
        ▼ (Scheduled Polling / Workflow Dispatch)
[pif-gen check] ─── Compares tag with state/last_<channel>_tag.txt
        │
        ▼ (On New Release)
[pif-gen build] ─── Downloads ZIPs -> Extracts system.prop -> Parses Props
        │           Validates Schema via Pydantic (Extended/Legacy)
        │           Serializes to JSON (<filename>.json)
        ▼
[pif-gen publish] ─ Creates Git Release: v<TAG>-<channel>
                    Uploads JSON artifacts with dedup verification
```

## Schema Specification

The generator parses `system.prop` keys into strictly validated profile schemas.

### Extended Profile Schema (`OutputFormat.EXTENDED`)

| Field | Source Property Priority | Description |
| :--- | :--- | :--- |
| `ID` | `ro.system_ext.build.id` → `ro.build.id` | Android build identifier |
| `BRAND` | `ro.product.system_ext.brand` → `ro.product.brand` | Device brand name |
| `DEVICE` | `ro.product.system_ext.device` → `ro.product.device` | Hardware codename |
| `MANUFACTURER` | `ro.product.system_ext.manufacturer` → `ro.product.manufacturer` | Device OEM |
| `FINGERPRINT` | `ro.system_ext.build.fingerprint` → `ro.build.fingerprint` | Build fingerprint |
| `MODEL` | `ro.product.system_ext.model` → `ro.product.model` | Commercial marketing name |
| `PRODUCT` | `ro.product.system_ext.name` → `ro.product.name` | Product codename |
| `SECURITY_PATCH` | `ro.build.version.security_patch` or parsed from ID/FP | Patch level (`YYYY-MM-DD`) |
| `DEVICE_INITIAL_SDK_INT` | `ro.product.first_api_level` → SDK version | Minimum hardware launch SDK |
| `RELEASE` | `ro.system_ext.build.version.release` → `ro.build.version.release` | Android OS version |
| `TYPE` | `ro.system_ext.build.type` (Default: `user`) | Build type |
| `TAG` | `ro.system_ext.build.tags` (Default: `release-keys`) | Signing key tag |
| `DEBUG` | Computed boolean (`ro.debuggable == 1` or `type != user`) | Debug build flag |

## Installation

Requires Python >= 3.10.

```bash
git clone https://github.com/<owner>/pif-config-generator.git
cd pif-config-generator
pip install -e .
```

## CLI Reference

The package provides the `pif-gen` command line tool.

```bash
# Check monitored repositories against state files
pif-gen check --state-dir state

# Build single JSON from a local system.prop
pif-gen build --file path/to/system.prop --output-dir output

# Build batch from asset list (used by CI)
pif-gen build \
  --channel stable \
  --assets-json '[{"name": "Pixel_9_Pro_XL.zip", "url": "https://..."}]' \
  --output-dir output \
  --manifest output/manifest.txt

# Publish release assets
pif-gen publish \
  --repo "owner/pif-config-generator" \
  --tag "2026.08.15" \
  --channel stable \
  --manifest output/manifest.txt
```

## CI/CD Workflow Setup

The included GitHub Actions workflow (`.github/workflows/generate-pif.yml`) runs on a daily schedule (`0 2 * * *`) or manual dispatch.

### Required Permissions

Ensure the workflow has write permissions under repository settings:
- `contents: write` (for committing state trackers and publishing releases).

## Development & Testing

Run unit tests and schema assertions using `pytest`:

```bash
pytest tests/
```
