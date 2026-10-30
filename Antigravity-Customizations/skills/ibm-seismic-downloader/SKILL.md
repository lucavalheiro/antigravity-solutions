---
name: ibm-seismic-downloader
description: Automated downloader and synchronizer for any IBM Seismic Sales Kit, DocCenter, and partner enablement materials using cached Business Partner credentials.
---

# IBM Seismic Downloader Skill

Use this skill whenever the user asks to download or synchronize documents, presentations, videos, sheets, and collateral from any **IBM Seismic** link (DocCenter / Sales Kit).

## Capabilities & Architecture
1. **Persistent Authentication & SSO:**
   - Permanent browser profile stored at `C:\Users\lucav\.gemini\antigravity\seismic_profile`.
   - Automatically handles SSO through `https://auth-ibm.seismic.com` and `login.ibm.com` for IBM Business Partners (`luciano.cavalheiro@tdsynnex.com`).
   - Reuses cached cookies and sessions without re-prompting for MFA/OTP.
2. **Reverse-Engineered Seismic CAUGS API:**
   - Extracts full article widget metadata from `window.appDatas`.
   - Queries `https://gateway-edge-prod-ibm-us-east-otter.seismic.com/cds/api/cds/v1/tenants/ibm/resource/publishedcontents/search` to retrieve all accessible documents and `versionId`s.
   - Generates signed download URLs via `POST https://gateway-edge-prod-ibm-us-east-otter.seismic.com/caugs/v1/download` using `ContentV1` format.
   - Downloads files directly with `Authorization: Bearer <token>` from `blobstorageservice-ibm-edge.seismic.com`.
3. **Storage & OneDrive Integration:**
   - Automatically categorizes downloaded files into clean thematic subfolders.
   - Protects local disk space by marking large downloaded videos as Online-Only via OneDrive On-Demand (`attrib +U -P`).
   - Supports resume capability (skips already verified files).

## How to Run for Any IBM Solution

Run the modular CLI script located at `c:\Users\lucav\OneDrive - TDSYNNEX\Tecnologias e apresentações\ProjetoX\Seismc\download_ibm_seismic.py`:

```bash
python "c:\Users\lucav\OneDrive - TDSYNNEX\Tecnologias e apresentações\ProjetoX\Seismc\download_ibm_seismic.py" "<SEISMIC_SALES_KIT_OR_DOCCENTER_URL>" --dest "<OUTPUT_DIR>"
```

### Parameters:
- `<URL>`: Any IBM Seismic link (Sales Kit, DocCenter profile version, or folder URL).
- `--dest` / `-d`: The target folder where files will be saved and organized (defaults to current working directory).

### Output Artifacts:
- Categorized folders with all PPTX, PDF, HTML, MP4, DOCX, and XLSX files.
- `download_manifest.json`: Structured JSON catalog with IDs, names, versions, sizes, and verification status.
- `README_CATALOG.md`: Formatted markdown index table of all assets.
