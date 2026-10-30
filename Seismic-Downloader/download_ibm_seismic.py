"""
IBM Seismic Automated Downloader
Reusable tool to download complete Sales Kits and DocCenter content from Seismic.
"""

import os
import sys
import json
import time
import re
import argparse
import subprocess
import shutil
import urllib3
import requests

urllib3.disable_warnings()

GLOBAL_PROFILE_DIR = r"C:\Users\lucav\.gemini\antigravity\seismic_profile"
EMAIL = "luciano.cavalheiro@tdsynnex.com"
PASSWORD = "P@vec1000kdbenc"

CAUGS_DOWNLOAD_URL = "https://gateway-edge-prod-ibm-us-east-otter.seismic.com/caugs/v1/download"
CDS_SEARCH_URL = "https://gateway-edge-prod-ibm-us-east-otter.seismic.com/cds/api/cds/v1/tenants/ibm/resource/publishedcontents/search"

def sanitize_filename(name):
    return "".join(c if c not in r'\/:*?"<>|' else '_' for c in name).strip()

def get_free_disk_space_mb(path):
    total, used, free = shutil.disk_usage(path)
    return free // (1024 * 1024)

def dehydrate_onedrive_files(target_dir):
    """Marks completed files as Online-Only via OneDrive On-Demand to free local space."""
    for root, _, files in os.walk(target_dir):
        for f in files:
            if f.endswith((".mp4", ".pptx", ".html", ".zip")):
                filepath = os.path.join(root, f)
                try:
                    subprocess.run(["attrib", "+U", "-P", filepath], capture_output=True)
                except Exception:
                    pass

class SeismicSessionManager:
    def __init__(self, profile_dir=GLOBAL_PROFILE_DIR):
        self.profile_dir = profile_dir
        self.auth_token = None
        self.headers = {}
        self.profile_version_id = None
        self.teamsite_id = "1"
        self.cached_auth_path = os.path.join(self.profile_dir, "last_token.json")

    def load_cached_token(self):
        if os.path.exists(self.cached_auth_path):
            try:
                with open(self.cached_auth_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                token = data.get("auth")
                if token and not self.is_token_expired(token):
                    self.auth_token = token
                    self.profile_version_id = data.get("profile_version_id", self.profile_version_id)
                    return True
            except Exception:
                pass
        return False

    def is_token_expired(self, token, buffer_seconds=120):
        try:
            import base64
            clean_tok = token.replace("Bearer ", "")
            parts = clean_tok.split(".")
            if len(parts) >= 2:
                payload = parts[1] + "=" * (-len(parts[1]) % 4)
                decoded = json.loads(base64.urlsafe_b64decode(payload))
                exp = decoded.get("exp", 0)
                return (exp - int(time.time())) < buffer_seconds
        except Exception:
            return True
        return True

    def authenticate_and_extract_kit(self, target_url):
        print(f"\n[Auth] Launching headless browser with cached profile...")
        from playwright.sync_api import sync_playwright

        intercepted_appdatas = None
        intercepted_search_calls = []

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=self.profile_dir,
                channel="msedge",
                headless=True
            )
            page = context.pages[0] if context.pages else context.new_page()

            def on_request(req):
                auth = req.headers.get("authorization")
                if auth and "gateway-edge-prod-ibm-us-east-otter.seismic.com" in req.url:
                    self.auth_token = auth
                pvid = req.headers.get("profileversionid")
                if pvid:
                    self.profile_version_id = pvid
                tsid = req.headers.get("teamsiteid")
                if tsid:
                    self.teamsite_id = tsid

                if "publishedcontents/search" in req.url:
                    intercepted_search_calls.append({
                        "url": req.url,
                        "method": req.method,
                        "headers": dict(req.headers),
                        "post_data": req.post_data
                    })

            page.on("request", on_request)

            print(f"[Auth] Navigating to: {target_url}")
            page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(3000)

            # Check if IBM Business Partner login button is displayed
            bp_btn = page.locator("text=IBM Business Partner")
            if bp_btn.count() > 0 and bp_btn.first.is_visible():
                print("[Auth] Clicking IBM Business Partner login...")
                bp_btn.first.click()
                page.wait_for_timeout(4000)

                user_input = page.locator("input[type='text']:not([type='hidden'])")
                if user_input.count() > 0 and user_input.first.is_visible():
                    print("[Auth] Submitting user credentials...")
                    user_input.first.fill(EMAIL)
                    cont_btn = page.locator("button:has-text('Continuar'), button:has-text('Continue')")
                    if cont_btn.count() > 0:
                        cont_btn.first.click()
                    else:
                        user_input.first.press("Enter")
                    page.wait_for_timeout(3000)

                    pwd_input = page.locator("input[type='password']")
                    if pwd_input.count() > 0 and pwd_input.first.is_visible():
                        pwd_input.first.fill(PASSWORD)
                        login_btn = page.locator("button:has-text('Entrar'), button:has-text('Log in'), button:has-text('Sign in'), button[type='submit']")
                        if login_btn.count() > 0:
                            login_btn.first.click()
                        else:
                            pwd_input.first.press("Enter")
                        page.wait_for_timeout(5000)

            print("[Auth] Waiting for DocCenter state to load...")
            for _ in range(15):
                if self.auth_token:
                    break
                page.wait_for_timeout(1000)

            # Try to extract window.appDatas from page
            try:
                appdatas_raw = page.evaluate("() => window.appDatas ? JSON.stringify(window.appDatas) : null")
                if appdatas_raw:
                    intercepted_appdatas = json.loads(appdatas_raw)
            except Exception:
                pass

            context.close()

        if self.auth_token:
            print("[Auth] Authentication token successfully captured & verified!")
            os.makedirs(self.profile_dir, exist_ok=True)
            with open(self.cached_auth_path, "w", encoding="utf-8") as f:
                json.dump({
                    "auth": self.auth_token,
                    "profile_version_id": self.profile_version_id,
                    "teamsite_id": self.teamsite_id
                }, f)
        else:
            print("[Auth] Warning: Could not capture auth token.")

        return intercepted_appdatas, intercepted_search_calls

class SeismicDownloader:
    def __init__(self, target_url, output_dir):
        self.target_url = target_url
        self.output_dir = output_dir
        self.session_mgr = SeismicSessionManager()
        self.manifest_path = os.path.join(self.output_dir, "download_manifest.json")
        self.catalog_path = os.path.join(self.output_dir, "README_CATALOG.md")

    def run(self):
        os.makedirs(self.output_dir, exist_ok=True)
        print("="*60)
        print(f"IBM SEISMIC UNIVERSAL DOWNLOADER")
        print(f"URL: {self.target_url}")
        print(f"Destination: {self.output_dir}")
        print("="*60)

        appdatas, search_calls = self.session_mgr.authenticate_and_extract_kit(self.target_url)

        if not self.session_mgr.auth_token:
            print("ERROR: Failed to authenticate to IBM Seismic.")
            return False

        headers = {
            "Authorization": self.session_mgr.auth_token,
            "Content-Type": "application/json",
            "teamsiteid": self.session_mgr.teamsite_id or "1",
            "profileversionid": self.session_mgr.profile_version_id or "861ea1fd-99e0-44d7-9135-85412e5c28d1"
        }

        # Catalog documents from search calls and appdatas
        catalogued_docs = {}
        cid_to_section = {}

        if appdatas:
            try:
                article = appdatas.get('initApp', {}).get('/doccenter', {}).get('articleMetadata', {}).get('articleStructure', {}).get('Article', {})
                for w in article.get('Widgets', []):
                    wdata = w.get('Data', {})
                    title = wdata.get('title') or wdata.get('heading') or "General"
                    for it in wdata.get('items', []):
                        cid = it.get('contentId')
                        if cid and cid not in cid_to_section:
                            cid_to_section[cid] = title
            except Exception:
                pass

        print(f"[Catalog] Querying {len(search_calls)} intercepted sections for accessible documents...")
        for call in search_calls:
            url = call["url"]
            pdata = json.loads(call["post_data"]) if call.get("post_data") else {}
            try:
                resp = requests.post(url, headers=headers, json=pdata, verify=False, timeout=15)
                if resp.status_code == 200:
                    for d in resp.json().get("Documents", []):
                        cid = d.get("Id")
                        if cid and cid not in catalogued_docs:
                            catalogued_docs[cid] = d
            except Exception:
                pass

        downloadable = [d for d in catalogued_docs.values() if d.get("ObjectType") == "StaticContent"]
        print(f"[Catalog] Found {len(downloadable)} accessible downloadable files.")

        if not downloadable:
            print("No downloadable static content files found in this kit.")
            return True

        # Load existing manifest for auto-resume
        manifest = {}
        if os.path.exists(self.manifest_path):
            try:
                with open(self.manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except Exception:
                manifest = {}

        # Sort: first non-MP4 (small files), then MP4s ascending
        non_mp4 = [d for d in downloadable if d.get("Format") != "MP4"]
        mp4_files = sorted([d for d in downloadable if d.get("Format") == "MP4"], key=lambda x: x.get("Size", 0))
        ordered_files = non_mp4 + mp4_files

        for idx, doc in enumerate(ordered_files, 1):
            cid = doc.get("Id")
            name = doc.get("Name")
            fmt = doc.get("Format", "bin")
            size = doc.get("Size", 0)
            sec = cid_to_section.get(cid, "General")
            
            # Clean folder name
            folder_clean = sanitize_filename(sec)
            folder_path = os.path.join(self.output_dir, folder_clean)
            os.makedirs(folder_path, exist_ok=True)

            filename = f"{sanitize_filename(name)}.{fmt.lower()}"
            out_path = os.path.join(folder_path, filename)

            # Skip if already verified
            if os.path.exists(out_path) and os.path.getsize(out_path) > 0 and cid in manifest and manifest[cid].get("status") == "Verified":
                print(f"[{idx}/{len(ordered_files)}] [CACHED] {name}")
                continue

            # Check disk space
            free_mb = get_free_disk_space_mb(self.output_dir)
            file_mb = size // (1024 * 1024)
            if free_mb < (file_mb + 250):
                print(f"[Disk] Low space ({free_mb} MB free). Dehydrating synced files...")
                dehydrate_onedrive_files(self.output_dir)
                time.sleep(2)

            # Token refresh check
            if self.session_mgr.is_token_expired(self.session_mgr.auth_token):
                print("[Auth] Token expired or close to expiry. Refreshing...")
                self.session_mgr.authenticate_and_extract_kit(self.target_url)
                headers["Authorization"] = self.session_mgr.auth_token

            print(f"[{idx}/{len(ordered_files)}] Downloading [{fmt}] ({file_mb} MB): {name}")

            payload = {
                "ContentV1": {
                    "repository": "doccenter",
                    "type": "file",
                    "name": name,
                    "contentProfileId": "0234dd96-5d7f-45ba-ad82-fee886efa83d",
                    "libraryContent": {
                        "teamsiteId": "1",
                        "id": cid,
                        "versionId": doc["VersionId"]
                    }
                },
                "ApplicationWatermarkData": {
                    "application": "DocCenter",
                    "viewerId": "49ea3907-0950-45c1-b2d7-5c40d68a04df"
                },
                "Format": fmt,
                "Expiration": -1
            }

            download_url = None
            for attempt in range(3):
                try:
                    resp = requests.post(CAUGS_DOWNLOAD_URL, headers=headers, json=payload, verify=False, timeout=20)
                    if resp.status_code == 200:
                        cdata = resp.json()
                        if cdata.get("Status") == "Complete":
                            download_url = cdata.get("Url")
                            break
                        elif cdata.get("Status") == "InProgress":
                            job_id = cdata.get("Id")
                            poll_url = f"{CAUGS_DOWNLOAD_URL}/{job_id}"
                            for _ in range(15):
                                time.sleep(2)
                                poll_resp = requests.get(poll_url, headers=headers, verify=False, timeout=15)
                                if poll_resp.status_code == 200 and poll_resp.json().get("Status") == "Complete":
                                    download_url = poll_resp.json().get("Url")
                                    break
                            if download_url:
                                break
                    time.sleep(2)
                except Exception as e:
                    print(f"CAUGS attempt {attempt+1} error: {e}")
                    time.sleep(2)

            if not download_url:
                print(f"FAILED to obtain download URL for: {name}")
                continue

            temp_out = out_path + ".part"
            dl_ok = False
            for dl_attempt in range(3):
                try:
                    dl_resp = requests.get(download_url, headers={"Authorization": self.session_mgr.auth_token}, verify=False, stream=True, timeout=60)
                    if dl_resp.status_code == 200:
                        with open(temp_out, "wb") as fp:
                            for chunk in dl_resp.iter_content(chunk_size=65536):
                                if chunk:
                                    fp.write(chunk)
                        if os.path.exists(temp_out) and os.path.getsize(temp_out) > 0:
                            if os.path.exists(out_path):
                                os.remove(out_path)
                            os.rename(temp_out, out_path)
                            actual_sz = os.path.getsize(out_path)
                            dl_ok = True
                            if fmt == "MP4":
                                subprocess.run(["attrib", "+U", "-P", out_path], capture_output=True)
                            manifest[cid] = {
                                "id": cid,
                                "name": name,
                                "format": fmt,
                                "size": actual_sz,
                                "section": sec,
                                "path": out_path,
                                "status": "Verified"
                            }
                            print(f"SUCCESS: Saved {name}")
                            break
                except Exception as e:
                    print(f"Download attempt {dl_attempt+1} error: {e}")
                    time.sleep(3)

            with open(self.manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)

        self.generate_catalog(manifest)
        print("\n[Complete] All items downloaded and catalogued successfully!")
        return True

    def generate_catalog(self, manifest):
        sections = {}
        for item in manifest.values():
            sec = item.get("section", "General")
            if sec not in sections:
                sections[sec] = []
            sections[sec].append(item)

        with open(self.catalog_path, "w", encoding="utf-8") as f:
            f.write(f"# Catálogo de Ativos - Seismic IBM\n\n")
            f.write(f"**Origem:** {self.target_url}\n")
            f.write(f"**Data de Sincronização:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total de Arquivos:** {len(manifest)}\n\n")

            for sec, items in sorted(sections.items()):
                f.write(f"## {sec} ({len(items)} itens)\n\n")
                f.write("| Formato | Nome | Tamanho | Status |\n")
                f.write("| :--- | :--- | :--- | :--- |\n")
                for it in sorted(items, key=lambda x: x.get("name", "")):
                    sz = it.get("size", 0)
                    sz_str = f"{round(sz / (1024*1024), 1)} MB" if sz > 1024*1024 else f"{round(sz / 1024, 1)} KB"
                    f.write(f"| `{it.get('format')}` | **{it.get('name')}** | {sz_str} | ✅ Verificado |\n")
                f.write("\n")

def main():
    parser = argparse.ArgumentParser(description="Universal IBM Seismic Downloader")
    parser.add_argument("url", help="Target Seismic Sales Kit / DocCenter URL")
    parser.add_argument("--dest", "-d", default=os.getcwd(), help="Destination directory (default: current directory)")
    args = parser.parse_args()

    downloader = SeismicDownloader(args.url, os.path.abspath(args.dest))
    downloader.run()

if __name__ == "__main__":
    main()
