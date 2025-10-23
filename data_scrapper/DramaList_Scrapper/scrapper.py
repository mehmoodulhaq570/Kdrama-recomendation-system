# Save data into the csv file

import json
import re
from bs4 import BeautifulSoup
import os
import csv
from tqdm import tqdm  # progress bar

def extract_mydramalist_data(html_path):
    """Extract detailed drama data (including alternate names and full description) from a MyDramaList HTML file."""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
    except Exception as e:
        print(f"Error reading {html_path}: {e}")
        return None
    
    soup = BeautifulSoup(html, 'html.parser')

    # --------------------------------------------------------
    # 1. Extract structured JSON-LD data
    # --------------------------------------------------------
    jsonld_tag = soup.find('script', type='application/ld+json', string=re.compile('TVSeries'))
    data = {}
    if jsonld_tag:
        try:
            data = json.loads(jsonld_tag.string)
        except json.JSONDecodeError:
            print(f"JSON parse error in file: {html_path}")

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
    # 2. Extract full description from HTML (if available)
    # --------------------------------------------------------
    desc_div = soup.find('div', class_=re.compile(r'(show-synopsis|show-synopsis__text|show-details-item__content)'))
    if desc_div:
        full_desc = desc_div.get_text(separator=' ', strip=True)
        if full_desc and len(full_desc) > len(str(drama_info.get('description', ''))):
            drama_info['description'] = full_desc

    return drama_info


# --------------------------------------------------------
# 3. Process a single file or all HTMLs in a folder
# --------------------------------------------------------
def process_folder(input_path, output_csv="output.csv"):
    all_dramas = []

    if os.path.isdir(input_path):
        files = [f for f in os.listdir(input_path) if f.lower().endswith(".html")]
        print(f"Found {len(files)} HTML files. Starting extraction...\n")
        
        for file in tqdm(files, desc="Extracting dramas", unit="file"):
            full_path = os.path.join(input_path, file)
            try:
                info = extract_mydramalist_data(full_path)
                if info:
                    all_dramas.append(info)
            except Exception as e:
                print(f"Error processing {file}: {e}")
                continue
    else:
        # Single file mode
        info = extract_mydramalist_data(input_path)
        if info:
            all_dramas.append(info)

    # --------------------------------------------------------
    # 4. Save results to CSV (UTF-8 encoded)
    # --------------------------------------------------------
    if all_dramas:
        keys = list(all_dramas[0].keys())
        with open(output_csv, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_dramas)

        print(f"\nExtracted {len(all_dramas)} dramas and saved to '{output_csv}'")
    else:
        print("\nNo dramas extracted.")


# Example usage:
# process_folder("DramaList_Scrapper/The Heirs - MyDramaList.html")
process_folder(r"D:\Projects\Kdrama-recommendation\data_scrapper\dramas_html")
