import os
import sys
import json
import time
import subprocess
import shutil
import urllib3
import requests

urllib3.disable_warnings()

TARGET_DIR = r"c:\Users\lucav\OneDrive - TDSYNNEX\Tecnologias e apresentações\ProjetoX\Seismc"
SCRATCH_DIR = r"C:\Users\lucav\.gemini\antigravity\brain\91f18d0a-f887-47f0-ab0c-5b2f471620dc\scratch"
PROFILE_DIR = os.path.join(SCRATCH_DIR, "seismic_profile")
MANIFEST_PATH = os.path.join(TARGET_DIR, "download_manifest.json")
INDEX_PATH = os.path.join(TARGET_DIR, "README_IBM_Quantum_Safe_Sales_Kit.md")

EMAIL = "luciano.cavalheiro@tdsynnex.com"
PASSWORD = "P@vec1000kdbenc"
TARGET_URL = "https://ibm.seismic.com/apps/doccenter/861ea1fd-99e0-44d7-9135-85412e5c28d1/doc/%252Fdd3359e5f7-a856-a91b-7688-41024b2ac637%252FdfNTY4NmVhOWItY2RkNS04ZWY3LTZkNzItZTQwZjczMWUyMjk1%252CPT0%253D%252CRGF0YSBQbGF0Zm9ybQ%253D%253D%252FdfNDRmODBlMzMtY2ViMC0zMDI1LTVhNDEtNzg2OTg4MWVmZDBl%252CPT0%253D%252CR3VhcmRpdW0gQ3J5cHRvZ3JhcGh5IE1hbmFnZW1lbnQ%253D%252FdfOTRiYmU4NTQtNWY4NC03Y2QyLWZjYWUtOGIxYmFmZjkyZThk%252CPT0%253D%252CU2FsZXMga2l0%252Flfa7bebc74-5dec-44f7-a078-d1a4a345c4d8//?searchId=&anchorId=c8bcdf6a-9e9d-44ee-b421-fb1080658df4"

SECTION_MAPPING = {
    "Client Presentations": "01_Client_Presentations",
    "Solution Brief & Deployment Model": "02_Solution_Briefs_and_Architecture",
    "Data Sheets & One-Pagers": "03_Data_Sheets_and_One_Pagers",
    "Whitepapers": "04_Whitepapers_and_Strategy",
    "Hands-On Lab Guide": "05_Hands_On_Lab_Guides",
    "Sales Enablement Decks": "06_Sales_Enablement_Decks",
    "Technical Enablement Decks": "07_Technical_Enablement_Decks",
    "New assets": "08_New_Assets_and_Battlecards",
    "Lab Guide Demo Videos": "09_Lab_Guide_Demo_Videos",
    "Feature Flashes and Marketing Demos": "10_Marketing_and_Feature_Demos",
    "Sales Enablement Replays": "11_Sales_Enablement_Replays",
    "Technical Enablement Replays": "12_Technical_Enablement_Replays",
    "Pricing & Packaging": "13_Pricing_and_Packaging",
    "General": "14_General_Resources"
}

def get_free_space_mb():
    total, used, free = shutil.disk_usage(TARGET_DIR)
    return free // (1024 * 1024)

def free_up_disk_space():
    print("Freeing up local disk space via OneDrive On-Demand (attrib +U -P)...")
    for root, dirs, files in os.walk(TARGET_DIR):
        for f in files:
            if f.endswith((".mp4", ".pptx", ".html")):
                filepath = os.path.join(root, f)
                try:
                    subprocess.run(["attrib", "+U", "-P", filepath], capture_output=True)
                except Exception:
                    pass

def sanitize_name(name):
    # Remove chars invalid in Windows filenames: \ / : * ? " < > |
    cleaned = "".join(c if c not in r'\/:*?"<>|' else '_' for c in name).strip()
    return cleaned

def load_auth_token():
    auth_file = os.path.join(SCRATCH_DIR, "latest_auth.txt")
    if os.path.exists(auth_file):
        with open(auth_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def refresh_auth_token():
    print("Refreshing auth token via headless Playwright...")
    from playwright.sync_api import sync_playwright
    captured_token = None
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            channel="msedge",
            headless=True
        )
        page = context.pages[0] if context.pages else context.new_page()
        
        def on_req(req):
            nonlocal captured_token
            auth = req.headers.get("authorization")
            if auth and "gateway-edge-prod-ibm-us-east-otter.seismic.com" in req.url:
                captured_token = auth
                
        page.on("request", on_req)
        page.goto(TARGET_URL, wait_until="networkidle")
        page.wait_for_timeout(3000)
        
        bp_btn = page.locator("text=IBM Business Partner")
        if bp_btn.count() > 0:
            bp_btn.first.click()
            page.wait_for_timeout(4000)
            user_input = page.locator("input[type='text']:not([type='hidden'])")
            if user_input.count() > 0 and user_input.first.is_visible():
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
                    
        page.wait_for_timeout(8000)
        context.close()
        
    if captured_token:
        with open(os.path.join(SCRATCH_DIR, "latest_auth.txt"), "w", encoding="utf-8") as f:
            f.write(captured_token)
        with open(os.path.join(SCRATCH_DIR, "captured_auth.json"), "w", encoding="utf-8") as f:
            json.dump({"auth": captured_token}, f)
        print("Successfully refreshed token!")
        return captured_token
    else:
        print("Warning: Failed to capture new token during refresh.")
        return load_auth_token()

def main():
    token = load_auth_token()
    if not token:
        token = refresh_auth_token()
        
    # Load all documents
    with open(os.path.join(SCRATCH_DIR, "all_kit_documents.json"), "r", encoding="utf-8") as f:
        all_docs = json.load(f)
        
    # Load appdatas to map items to sections
    cid_to_section = {}
    try:
        with open(os.path.join(SCRATCH_DIR, "appdatas.json"), "r", encoding="utf-8") as f:
            app_data = json.load(f)
        article = app_data['initApp']['/doccenter']['articleMetadata']['articleStructure']['Article']
        for w in article.get('Widgets', []):
            wdata = w.get('Data', {})
            title = wdata.get('title') or wdata.get('heading')
            if title:
                for it in wdata.get('items', []):
                    cid = it.get('contentId')
                    if cid and cid not in cid_to_section:
                        cid_to_section[cid] = title
    except Exception as e:
        print("Could not map sections from appdatas:", e)
        
    # Heuristics for general items
    for cid, doc in all_docs.items():
        name = doc.get("Name", "")
        if cid not in cid_to_section:
            if any(k in name.lower() for k in ["pricing", "packaging", "parts", "quoting"]):
                cid_to_section[cid] = "Pricing & Packaging"
            elif any(k in name.lower() for k in ["battlecard", "competitive", "objection"]):
                cid_to_section[cid] = "New assets"
            elif any(k in name.lower() for k in ["brief", "solution brief", "white paper", "whitepaper"]):
                cid_to_section[cid] = "Whitepapers"
            elif any(k in name.lower() for k in ["deep dive", "install"]):
                cid_to_section[cid] = "Technical Enablement Decks" if doc.get("Format") == "PPTX" else "Technical Enablement Replays"
            elif any(k in name.lower() for k in ["vault", "seller", "presentation"]):
                cid_to_section[cid] = "Sales Enablement Decks"
            else:
                cid_to_section[cid] = "General"

    # Filter to downloadable static content
    downloadable = [d for d in all_docs.values() if d.get("ObjectType") == "StaticContent"]
    
    # Sort files: first non-MP4 (small files: PPTX, PDF, HTML, DOCX, XLSX), then MP4s by size ascending
    non_mp4 = [d for d in downloadable if d.get("Format") != "MP4"]
    mp4_files = [d for d in downloadable if d.get("Format") == "MP4"]
    mp4_files.sort(key=lambda x: x.get("Size", 0))
    ordered_files = non_mp4 + mp4_files
    
    print(f"Total downloadable files: {len(downloadable)}")
    print(f"  Non-video files: {len(non_mp4)}")
    print(f"  Video files (MP4): {len(mp4_files)}")
    print(f"Initial free disk space: {get_free_space_mb()} MB\n")
    
    # Load manifest if exists
    manifest = {}
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            manifest = {}
            
    success_count = 0
    fail_count = 0
    
    for idx, doc in enumerate(ordered_files, 1):
        cid = doc.get("Id")
        name = doc.get("Name")
        fmt = doc.get("Format", "bin")
        size = doc.get("Size", 0)
        section_name = cid_to_section.get(cid, "General")
        folder_name = SECTION_MAPPING.get(section_name, "14_General_Resources")
        
        folder_path = os.path.join(TARGET_DIR, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        filename = f"{sanitize_name(name)}.{fmt.lower()}"
        out_path = os.path.join(folder_path, filename)
        
        # Check if already downloaded and verified
        if os.path.exists(out_path):
            existing_size = os.path.getsize(out_path)
            if existing_size > 0:
                print(f"[{idx}/{len(ordered_files)}] ALREADY DOWNLOADED: [{fmt}] {name} ({existing_size} bytes)")
                manifest[cid] = {
                    "id": cid,
                    "name": name,
                    "format": fmt,
                    "size": existing_size,
                    "section": section_name,
                    "path": out_path,
                    "status": "Verified"
                }
                success_count += 1
                continue
                
        # Check disk space before downloading
        free_mb = get_free_space_mb()
        file_mb = size // (1024 * 1024)
        if free_mb < (file_mb + 250):
            print(f"Low disk space ({free_mb} MB free, need {file_mb} MB). Running OneDrive hydration cleanup...")
            free_up_disk_space()
            time.sleep(2)
            free_mb = get_free_space_mb()
            print(f"Disk space after cleanup: {free_mb} MB free")
            
        print(f"\n[{idx}/{len(ordered_files)}] Downloading [{fmt}] ({file_mb} MB): {name}")
        
        # Download request
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
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "teamsiteid": "1",
            "profileversionid": "861ea1fd-99e0-44d7-9135-85412e5c28d1"
        }
        
        caugs_url = "https://gateway-edge-prod-ibm-us-east-otter.seismic.com/caugs/v1/download"
        download_url = None
        
        for attempt in range(2):
            try:
                resp = requests.post(caugs_url, headers=headers, json=payload, verify=False, timeout=20)
                if resp.status_code == 401:
                    print("Received 401 Unauthorized. Refreshing token...")
                    token = refresh_auth_token()
                    headers["Authorization"] = token
                    continue
                elif resp.status_code == 200:
                    cdata = resp.json()
                    status = cdata.get("Status")
                    if status == "Complete":
                        download_url = cdata.get("Url")
                        break
                    elif status == "InProgress":
                        job_id = cdata.get("Id")
                        poll_url = f"{caugs_url}/{job_id}"
                        for p in range(15):
                            time.sleep(2)
                            poll_resp = requests.get(poll_url, headers=headers, verify=False, timeout=15)
                            if poll_resp.status_code == 200:
                                pdata = poll_resp.json()
                                if pdata.get("Status") == "Complete":
                                    download_url = pdata.get("Url")
                                    break
                        if download_url:
                            break
                    else:
                        print(f"Unexpected status: {status} ({cdata.get('ErrorReason')})")
                        break
                else:
                    print(f"CAUGS returned HTTP {resp.status_code}: {resp.text}")
                    break
            except Exception as e:
                print(f"Attempt {attempt+1} error: {e}")
                time.sleep(2)
                
        if not download_url:
            print(f"FAILED to obtain download URL for: {name}")
            manifest[cid] = {
                "id": cid,
                "name": name,
                "format": fmt,
                "size": size,
                "section": section_name,
                "status": "Failed_URL"
            }
            fail_count += 1
            continue
            
        # Fetch file bytes
        try:
            temp_out = out_path + ".part"
            dl_resp = requests.get(download_url, headers={"Authorization": token}, verify=False, stream=True, timeout=60)
            if dl_resp.status_code == 200:
                with open(temp_out, "wb") as fp:
                    for chunk in dl_resp.iter_content(chunk_size=65536):
                        if chunk:
                            fp.write(chunk)
                if os.path.exists(temp_out):
                    if os.path.exists(out_path):
                        os.remove(out_path)
                    os.rename(temp_out, out_path)
                    actual_sz = os.path.getsize(out_path)
                    print(f"SUCCESS: Saved to {out_path} ({actual_sz} bytes)")
                    
                    # If it's a large MP4, unpin it immediately so OneDrive syncs it to cloud and frees local disk
                    if fmt == "MP4" and actual_sz > 50 * 1024 * 1024:
                        subprocess.run(["attrib", "+U", "-P", out_path], capture_output=True)
                        
                    manifest[cid] = {
                        "id": cid,
                        "name": name,
                        "format": fmt,
                        "size": actual_sz,
                        "section": section_name,
                        "path": out_path,
                        "status": "Verified"
                    }
                    success_count += 1
            else:
                print(f"Failed to fetch file binary: HTTP {dl_resp.status_code}")
                manifest[cid] = {
                    "id": cid,
                    "name": name,
                    "format": fmt,
                    "size": size,
                    "section": section_name,
                    "status": f"Failed_HTTP_{dl_resp.status_code}"
                }
                fail_count += 1
        except Exception as e:
            print(f"Exception downloading file: {e}")
            fail_count += 1
            
        # Save manifest periodically
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    # Clean up any leftover test files in root of TARGET_DIR if present
    for f in os.listdir(TARGET_DIR):
        fpath = os.path.join(TARGET_DIR, f)
        if os.path.isfile(fpath) and not f.startswith(("README", "download_manifest")) and not f.endswith(".py"):
            try:
                os.remove(fpath)
            except Exception:
                pass
                
    # Generate README index in TARGET_DIR
    generate_markdown_index(manifest, INDEX_PATH)
    
    print("\n==========================================")
    print("DOWNLOAD TASK COMPLETE!")
    print(f"Total processed: {len(ordered_files)}")
    print(f"Successfully downloaded & verified: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Destination: {TARGET_DIR}")
    print(f"Index created: {INDEX_PATH}")
    print("==========================================")

def generate_markdown_index(manifest, out_path):
    sections = {}
    for item in manifest.values():
        sec = item.get("section", "General")
        if sec not in sections:
            sections[sec] = []
        sections[sec].append(item)
        
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# IBM Quantum Safe Sales Kit - Catálogo Completo de Ativos\n\n")
        f.write(f"**Data do Download:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total de Ativos Disponibilizados:** {len(manifest)}\n\n")
        f.write("Todos os arquivos foram baixados diretamente do portal Seismic (IBM Sales Kit) e organizados por seção temática.\n\n")
        
        for sec, items in sorted(sections.items()):
            f.write(f"## {sec} ({len(items)} itens)\n\n")
            f.write("| Formato | Nome do Documento / Vídeo | Tamanho | Status |\n")
            f.write("| :--- | :--- | :--- | :--- |\n")
            for it in sorted(items, key=lambda x: x.get("name", "")):
                fmt = it.get("format", "")
                name = it.get("name", "")
                sz = it.get("size", 0)
                if sz > 1024 * 1024:
                    sz_str = f"{round(sz / (1024*1024), 1)} MB"
                elif sz > 1024:
                    sz_str = f"{round(sz / 1024, 1)} KB"
                else:
                    sz_str = f"{sz} B"
                status = it.get("status", "")
                icon = "✅" if status == "Verified" else "❌"
                f.write(f"| `{fmt}` | **{name}** | {sz_str} | {icon} {status} |\n")
            f.write("\n")

if __name__ == "__main__":
    main()
