import requests
import os

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
    # 2. Get the latest 'up_to_date_as_of' date for all titles
    print("Fetching latest title dates...")
    titles_url = "https://www.ecfr.gov/api/versioner/v1/titles.json"
    response = requests.get(titles_url)
    response.raise_for_status()
    
    # Map title numbers to their latest updated date
    titles_data = response.json().get("titles", [])
    latest_dates = {str(t["number"]): t["up_to_date_as_of"] for t in titles_data}

    # Create a directory to store the XML files
    os.makedirs("ecfr_data", exist_ok=True)

    # 3. Fetch the XML for each target
    for target in TARGETS:
        title = target["title"]
        date = latest_dates.get(title)
        
        if not date:
            print(f"Could not find a valid date for Title {title}. Skipping...")
            continue
            
        # Base URL for the eCFR XML endpoint
        base_url = f"https://www.ecfr.gov/api/versioner/v1/full/{date}/title-{title}.xml"
        
        # Build query parameters based on the target dictionary (excluding 'title')
        params = {k: v for k, v in target.items() if k != "title"}
            
        print(f"Fetching Title {title}, Date {date}, Params {params}...")
        xml_response = requests.get(base_url, params=params)
        
        if xml_response.status_code == 200:
            # Create a clean, unique filename based on the parameters
            parts_str = "_".join(f"{k}-{v}" for k, v in params.items())
            filename = f"ecfr_data/title-{title}_{parts_str}.xml"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(xml_response.text)
            print(f"Successfully saved {filename}")
        else:
            print(f"Failed to fetch {target}: HTTP {xml_response.status_code}")

if __name__ == "__main__":
    main()
