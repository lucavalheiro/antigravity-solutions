import os
import sys
import json
import time
import subprocess
import requests
import urllib3

urllib3.disable_warnings()

TARGET_DIR = r"c:\Users\lucav\OneDrive - TDSYNNEX\Tecnologias e apresentações\ProjetoX\Seismc"
SCRATCH_DIR = r"C:\Users\lucav\.gemini\antigravity\brain\91f18d0a-f887-47f0-ab0c-5b2f471620dc\scratch"
MANIFEST_PATH = os.path.join(TARGET_DIR, "download_manifest.json")
INDEX_PATH = os.path.join(TARGET_DIR, "README_IBM_Quantum_Safe_Sales_Kit.md")

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

def sanitize_name(name):
    return "".join(c if c not in r'\/:*?"<>|' else '_' for c in name).strip()

def load_auth_token():
    auth_file = os.path.join(SCRATCH_DIR, "latest_auth.txt")
    with open(auth_file, "r", encoding="utf-8") as f:
        return f.read().strip()

def main():
    token = load_auth_token()
    print("Loaded fresh token.")
    
    with open(os.path.join(SCRATCH_DIR, "all_kit_documents.json"), "r", encoding="utf-8") as f:
        all_docs = json.load(f)
        
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    # Appdatas to map sections
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
    except Exception:
        pass

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

    downloadable = [d for d in all_docs.values() if d.get("ObjectType") == "StaticContent"]
    remaining = [d for d in downloadable if d.get("Id") not in manifest or manifest[d.get("Id")].get("status") != "Verified"]
    
    print(f"Total downloadable: {len(downloadable)}")
    print(f"Already verified in manifest: {len(manifest)}")
    print(f"Remaining to download: {len(remaining)}")
    
    caugs_url = "https://gateway-edge-prod-ibm-us-east-otter.seismic.com/caugs/v1/download"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "teamsiteid": "1",
        "profileversionid": "861ea1fd-99e0-44d7-9135-85412e5c28d1"
    }
    
    for idx, doc in enumerate(remaining, 1):
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
        
        print(f"\n[{idx}/{len(remaining)}] Downloading [{fmt}] ({size // 1024} KB): {name}")
        
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
                resp = requests.post(caugs_url, headers=headers, json=payload, verify=False, timeout=20)
                if resp.status_code == 200:
                    cdata = resp.json()
                    status = cdata.get("Status")
                    if status == "Complete":
                        download_url = cdata.get("Url")
                        break
                    elif status == "InProgress":
                        job_id = cdata.get("Id")
                        poll_url = f"{caugs_url}/{job_id}"
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
                time.sleep(3)
                
        if not download_url:
            print(f"FAILED to get download URL for: {name}")
            continue
            
        temp_out = out_path + ".part"
        download_ok = False
        for dl_attempt in range(3):
            try:
                dl_resp = requests.get(download_url, headers={"Authorization": token}, verify=False, stream=True, timeout=60)
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
                        print(f"SUCCESS: Saved {out_path} ({actual_sz} bytes)")
                        download_ok = True
                        
                        if fmt == "MP4":
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
                        break
                else:
                    print(f"Download HTTP {dl_resp.status_code}, retrying...")
                    time.sleep(2)
            except Exception as e:
                print(f"Download attempt {dl_attempt+1} error: {e}")
                time.sleep(3)
                
        if not download_ok:
            print(f"FAILED to download file bytes for: {name}")
            
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    # Re-generate markdown index
    from download_all_assets import generate_markdown_index
    generate_markdown_index(manifest, INDEX_PATH)
    
    print("\n==========================================")
    print("ALL REMAINING ASSETS PROCESSED!")
    print(f"Final manifest verified count: {sum(1 for x in manifest.values() if x.get('status') == 'Verified')} / {len(downloadable)}")
    print("==========================================")

if __name__ == "__main__":
    main()
