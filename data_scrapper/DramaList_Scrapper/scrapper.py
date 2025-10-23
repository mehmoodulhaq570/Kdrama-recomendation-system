# Save data into the csv file

import json
import re
from bs4 import BeautifulSoup
import os
import csv

def extract_mydramalist_data(html_path):
    """Extract detailed drama data (including alternate names and full description) from a MyDramaList HTML file."""
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')

    # --------------------------------------------------------
    # 1️⃣ Extract structured JSON-LD data
    # --------------------------------------------------------
    jsonld_tag = soup.find('script', type='application/ld+json', string=re.compile('TVSeries'))
    data = {}
    if jsonld_tag:
        try:
            data = json.loads(jsonld_tag.string)
        except json.JSONDecodeError:
            pass

    drama_info = {
        'title': data.get('name'),
        'alternate_names': ', '.join(data.get('alternateName', [])) if isinstance(data.get('alternateName'), list) else data.get('alternateName'),
        'url': data.get('url'),
        'description': data.get('description'),
        'image': data.get('image'),
        'publisher': data.get('publisher', {}).get('name'),
        'country': data.get('countryOfOrigin', {}).get('name'),
        'genres': ', '.join(data.get('genre', [])) if isinstance(data.get('genre'), list) else data.get('genre'),
        'rating_value': data.get('aggregateRating', {}).get('ratingValue'),
        'rating_count': data.get('aggregateRating', {}).get('ratingCount'),
        'date_published': data.get('datePublished'),
        'keywords': ', '.join(data.get('keywords', [])) if isinstance(data.get('keywords'), list) else data.get('keywords'),
        'actors': ', '.join([a.get('name', '') for a in data.get('actor', [])]),
    }

    # --------------------------------------------------------
    # 2️⃣ Extract full description from HTML (if available)
    # --------------------------------------------------------
    desc_div = soup.find('div', class_=re.compile(r'(show-synopsis|show-synopsis__text|show-details-item__content)'))
    if desc_div:
        full_desc = desc_div.get_text(separator=' ', strip=True)
        if full_desc and len(full_desc) > len(str(drama_info.get('description', ''))):
            drama_info['description'] = full_desc

    return drama_info


# --------------------------------------------------------
# 3️⃣ Process a single file or all HTMLs in a folder
# --------------------------------------------------------
def process_folder(input_path, output_csv="output.csv"):
    all_dramas = []

    if os.path.isdir(input_path):
        files = [f for f in os.listdir(input_path) if f.lower().endswith(".html")]
        for file in files:
            full_path = os.path.join(input_path, file)
            info = extract_mydramalist_data(full_path)
            if info:
                all_dramas.append(info)
    else:
        # Single file mode
        info = extract_mydramalist_data(input_path)
        if info:
            all_dramas.append(info)

    # --------------------------------------------------------
    # 4️⃣ Save results to CSV (UTF-8 encoded)
    # --------------------------------------------------------
    if all_dramas:
        keys = list(all_dramas[0].keys())
        with open(output_csv, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_dramas)

        print(f" Extracted {len(all_dramas)} dramas and saved to '{output_csv}'")
    else:
        print(" No dramas found.")


# Example usage:
# For one HTML file:
process_folder("DramaList_Scrapper/The Heirs - MyDramaList.html")

# For a folder containing multiple saved pages:
# process_folder("path_to_your_html_folder")
