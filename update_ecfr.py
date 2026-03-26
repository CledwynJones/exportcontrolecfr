import requests
import os
from datetime import datetime, timezone

# 1. Define the specific CFR sections or parts you want to track.
# You can specify 'part', 'section', 'subpart', etc., according to the eCFR hierarchy.
TARGETS = [
    {"title": "15", "part": "744"}, # The Commerce Control 
    {"title": "22", "part": "121"}, # The US Munitions List
    {"title": "10", "part": "110"}, # NRC
    {"title": "10", "part": "810"}, # NNSA
   # {"title": "12", "part": "1005", "section": "1005.4"} # Example: CFPB specific section
]

def main():
    print("Fetching latest title dates...")
    titles_url = "https://www.ecfr.gov/api/versioner/v1/titles.json"
    response = requests.get(titles_url)
    response.raise_for_status()
    
    titles_data = response.json().get("titles", [])
    latest_dates = {str(t["number"]): t["up_to_date_as_of"] for t in titles_data}

    os.makedirs("ecfr_data", exist_ok=True)

    for target in TARGETS:
        title = target["title"]
        date = latest_dates.get(title)
        
        if not date:
            print(f"Could not find a valid date for Title {title}. Skipping...")
            continue
            
        base_url = f"https://www.ecfr.gov/api/versioner/v1/full/{date}/title-{title}.xml"
        params = {k: v for k, v in target.items() if k != "title"}
            
        print(f"Fetching Title {title}, Date {date}, Params {params}...")
        xml_response = requests.get(base_url, params=params)
        
        if xml_response.status_code == 200:
            parts_str = "_".join(f"{k}-{v}" for k, v in params.items())
            filename = f"ecfr_data/title-{title}_{parts_str}.xml"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(xml_response.text)
            print(f"Successfully saved {filename}")
        else:
            print(f"Failed to fetch {target}: HTTP {xml_response.status_code}")

    # NEW: Write the current time to last_run.txt
    run_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    with open("last_run.txt", "w", encoding="utf-8") as f:
        f.write(f"Script last executed successfully on: {run_time}\n")
    print("Updated last_run.txt")

if __name__ == "__main__":
    main()
