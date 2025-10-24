# # Save data into the csv file

# import json
# import re
# from bs4 import BeautifulSoup
# import os
# import csv
# from tqdm import tqdm  # progress bar

# def extract_mydramalist_data(html_path):
#     """Extract detailed drama data (including alternate names and full description) from a MyDramaList HTML file."""
#     try:
#         with open(html_path, 'r', encoding='utf-8') as f:
#             html = f.read()
#     except Exception as e:
#         print(f"Error reading {html_path}: {e}")
#         return None
    
#     soup = BeautifulSoup(html, 'html.parser')

#     # --------------------------------------------------------
#     # 1. Extract structured JSON-LD data
#     # --------------------------------------------------------
#     jsonld_tag = soup.find('script', type='application/ld+json', string=re.compile('TVSeries'))
#     data = {}
#     if jsonld_tag:
#         try:
#             data = json.loads(jsonld_tag.string)
#         except json.JSONDecodeError:
#             print(f"JSON parse error in file: {html_path}")

#     drama_info = {
#         'title': data.get('name'),
#         'alternate_names': ', '.join(data.get('alternateName', [])) if isinstance(data.get('alternateName'), list) else data.get('alternateName'),
#         'url': data.get('url'),
#         'description': data.get('description'),
#         'image': data.get('image'),
#         'publisher': data.get('publisher', {}).get('name'),
#         'country': data.get('countryOfOrigin', {}).get('name'),
#         'genres': ', '.join(data.get('genre', [])) if isinstance(data.get('genre'), list) else data.get('genre'),
#         'rating_value': data.get('aggregateRating', {}).get('ratingValue'),
#         'rating_count': data.get('aggregateRating', {}).get('ratingCount'),
#         'date_published': data.get('datePublished'),
#         'keywords': ', '.join(data.get('keywords', [])) if isinstance(data.get('keywords'), list) else data.get('keywords'),
#         'actors': ', '.join([a.get('name', '') for a in data.get('actor', [])]),
#     }

#     # --------------------------------------------------------
#     # 2. Extract full description from HTML (if available)
#     # --------------------------------------------------------
#     desc_div = soup.find('div', class_=re.compile(r'(show-synopsis|show-synopsis__text|show-details-item__content)'))
#     if desc_div:
#         full_desc = desc_div.get_text(separator=' ', strip=True)
#         if full_desc and len(full_desc) > len(str(drama_info.get('description', ''))):
#             drama_info['description'] = full_desc

#     return drama_info


# # --------------------------------------------------------
# # 3. Process a single file or all HTMLs in a folder
# # --------------------------------------------------------
# def process_folder(input_path, output_csv="output.csv"):
#     all_dramas = []

#     if os.path.isdir(input_path):
#         files = [f for f in os.listdir(input_path) if f.lower().endswith(".html")]
#         print(f"Found {len(files)} HTML files. Starting extraction...\n")
        
#         for file in tqdm(files, desc="Extracting dramas", unit="file"):
#             full_path = os.path.join(input_path, file)
#             try:
#                 info = extract_mydramalist_data(full_path)
#                 if info:
#                     all_dramas.append(info)
#             except Exception as e:
#                 print(f"Error processing {file}: {e}")
#                 continue
#     else:
#         # Single file mode
#         info = extract_mydramalist_data(input_path)
#         if info:
#             all_dramas.append(info)

#     # --------------------------------------------------------
#     # 4. Save results to CSV (UTF-8 encoded)
#     # --------------------------------------------------------
#     if all_dramas:
#         keys = list(all_dramas[0].keys())
#         with open(output_csv, "w", encoding="utf-8-sig", newline="") as f:
#             writer = csv.DictWriter(f, fieldnames=keys)
#             writer.writeheader()
#             writer.writerows(all_dramas)

#         print(f"\nExtracted {len(all_dramas)} dramas and saved to '{output_csv}'")
#     else:
#         print("\nNo dramas extracted.")


# # Example usage:
# # process_folder("DramaList_Scrapper/The Heirs - MyDramaList.html")
# process_folder(r"D:\Projects\Kdrama-recommendation\data_scrapper\dramas_html")


# import json
# import re
# from bs4 import BeautifulSoup
# import os
# import csv
# from tqdm import tqdm
# from concurrent.futures import ThreadPoolExecutor, as_completed

# # Precompile regex patterns
# TVSERIES_RE = re.compile('TVSeries')
# DESC_CLASS_RE = re.compile(r'(show-synopsis|show-synopsis__text|show-details-item__content)')


# def extract_mydramalist_data(html_path):
#     """Extract detailed drama data (including alternate names and full description) from a MyDramaList HTML file."""
#     try:
#         with open(html_path, 'r', encoding='utf-8') as f:
#             html = f.read()
#     except Exception as e:
#         print(f"Error reading {html_path}: {e}")
#         return None

#     # Use lxml parser for speed
#     soup = BeautifulSoup(html, 'lxml')

#     # 1. Extract JSON-LD data
#     jsonld_tag = soup.find('script', type='application/ld+json', string=TVSERIES_RE)
#     data = {}
#     if jsonld_tag:
#         try:
#             data = json.loads(jsonld_tag.string)
#         except json.JSONDecodeError:
#             return None

#     # 2. Extract key info
#     drama_info = {
#         'title': data.get('name'),
#         'alternate_names': ', '.join(data.get('alternateName', [])) if isinstance(data.get('alternateName'), list)
#         else data.get('alternateName'),
#         'url': data.get('url'),
#         'description': data.get('description'),
#         'image': data.get('image'),
#         'publisher': (data.get('publisher') or {}).get('name'),
#         'country': (data.get('countryOfOrigin') or {}).get('name'),
#         'genres': ', '.join(data.get('genre', [])) if isinstance(data.get('genre'), list) else data.get('genre'),
#         'rating_value': (data.get('aggregateRating') or {}).get('ratingValue'),
#         'rating_count': (data.get('aggregateRating') or {}).get('ratingCount'),
#         'date_published': data.get('datePublished'),
#         'keywords': ', '.join(data.get('keywords', [])) if isinstance(data.get('keywords'), list) else data.get('keywords'),
#         'actors': ', '.join(a.get('name', '') for a in data.get('actor', [])),
#     }

#     # 3. Extract longer description if present
#     desc_div = soup.find('div', class_=DESC_CLASS_RE)
#     if desc_div:
#         full_desc = desc_div.get_text(separator=' ', strip=True)
#         if full_desc and len(full_desc) > len(str(drama_info.get('description') or '')):
#             drama_info['description'] = full_desc

#     return drama_info


# def process_folder(input_path, output_csv="output.csv", max_workers=8):
#     """Process all HTML files in a folder using multithreading."""
#     all_dramas = []

#     # Collect file list
#     files = []
#     if os.path.isdir(input_path):
#         files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.lower().endswith(".html")]
#         print(f"Found {len(files)} HTML files. Starting extraction...\n")
#     else:
#         files = [input_path]

#     if not files:
#         print("No HTML files found.")
#         return

#     # Multithreaded extraction
#     with ThreadPoolExecutor(max_workers=max_workers) as executor:
#         futures = {executor.submit(extract_mydramalist_data, f): f for f in files}
#         for future in tqdm(as_completed(futures), total=len(futures), desc="Extracting dramas", unit="file"):
#             result = future.result()
#             if result:
#                 all_dramas.append(result)

#     # Save results
#     if all_dramas:
#         keys = list(all_dramas[0].keys())
#         with open(output_csv, "w", encoding="utf-8-sig", newline="") as f:
#             writer = csv.DictWriter(f, fieldnames=keys)
#             writer.writeheader()
#             writer.writerows(all_dramas)
#         print(f"\n✅ Extracted {len(all_dramas)} dramas and saved to '{output_csv}'")
#     else:
#         print("\n⚠️ No dramas extracted.")


# # Example usage:
# process_folder(
#     r"D:\Projects\Kdrama-recommendation\data_scrapper\dramas_html",
#     output_csv="output_fast.csv",
#     max_workers=8  # Adjust based on CPU cores
# )

# code is 10x faster using lxml and multithreading
import json
import os
import csv
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from lxml import html

# Precompile regex
TVSERIES_RE = re.compile('TVSeries')
DESC_CLASS_RE = re.compile(r'(show-synopsis|show-synopsis__text|show-details-item__content)')

def extract_mydramalist_data(file_path):
    """Ultra-fast extractor using lxml (no BeautifulSoup)."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    except Exception:
        return None

    try:
        doc = html.fromstring(text)
    except Exception:
        return None

    # Extract JSON-LD data
    jsonld = None
    for elem in doc.xpath("//script[@type='application/ld+json']"):
        content = elem.text or ""
        if "TVSeries" in content:
            jsonld = content
            break

    data = {}
    if jsonld:
        try:
            data = json.loads(jsonld)
        except Exception:
            return None

    aggr = data.get('aggregateRating', {}) or {}
    drama_info = {
        'title': data.get('name'),
        'alternate_names': ', '.join(data['alternateName']) if isinstance(data.get('alternateName'), list)
        else data.get('alternateName'),
        'url': data.get('url'),
        'description': data.get('description'),
        'image': data.get('image'),
        'publisher': (data.get('publisher') or {}).get('name'),
        'country': (data.get('countryOfOrigin') or {}).get('name'),
        'genres': ', '.join(data['genre']) if isinstance(data.get('genre'), list) else data.get('genre'),
        'rating_value': aggr.get('ratingValue'),
        'rating_count': aggr.get('ratingCount'),
        'date_published': data.get('datePublished'),
        'keywords': ', '.join(data['keywords']) if isinstance(data.get('keywords'), list) else data.get('keywords'),
        'actors': ', '.join(a.get('name', '') for a in data.get('actor', [])),
    }

    # Extract longer description if available
    desc_nodes = doc.xpath("//div[contains(@class,'show-synopsis') or "
                           "contains(@class,'show-synopsis__text') or "
                           "contains(@class,'show-details-item__content')]")
    if desc_nodes:
        full_desc = " ".join(desc_nodes[0].itertext()).strip()
        if full_desc and len(full_desc) > len(str(drama_info.get('description') or '')):
            drama_info['description'] = full_desc

    return drama_info


def process_folder(input_path, output_csv="output_fast.csv", max_workers=None, skip_existing=True):
    """Process all HTML files using multithreading and lxml for maximum speed."""
    if not os.path.exists(input_path):
        print(f"Path not found: {input_path}")
        return

    # Collect HTML files
    if os.path.isdir(input_path):
        files = [os.path.join(input_path, f) for f in os.listdir(input_path)
                 if f.lower().endswith(".html")]
    else:
        files = [input_path]

    if not files:
        print("No HTML files found.")
        return

    print(f"Found {len(files)} HTML files. Starting extraction...")

    # Skip already processed titles
    processed_titles = set()
    if skip_existing and os.path.exists(output_csv):
        with open(output_csv, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                processed_titles.add(row["title"])

    new_files = []
    for f in files:
        name = os.path.basename(f).replace(".html", "").strip()
        if name not in processed_titles:
            new_files.append(f)

    print(f"Processing {len(new_files)} new files...")

    # Use all CPU threads by default
    if max_workers is None:
        import multiprocessing
        max_workers = min(16, multiprocessing.cpu_count() * 2)

    all_dramas = []

    # Parallel execution
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(extract_mydramalist_data, f): f for f in new_files}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Extracting", unit="file"):
            result = future.result()
            if result:
                all_dramas.append(result)

    # Save to CSV
    if all_dramas:
        write_mode = "a" if skip_existing and os.path.exists(output_csv) else "w"
        keys = list(all_dramas[0].keys())
        with open(output_csv, write_mode, encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            if write_mode == "w":
                writer.writeheader()
            writer.writerows(all_dramas)

        print(f"Extracted {len(all_dramas)} dramas and saved to '{output_csv}'")
    else:
        print("No new dramas extracted.")


# Example usage
process_folder(
    r"D:\Projects\Kdrama-recommendation\data_scrapper\dramas_html",
    output_csv= r"D:\Projects\Kdrama-recommendation\data_scrapper\DramaList_Scrapper\output_ultrafast.csv",
    max_workers=None,
    skip_existing=True
)
