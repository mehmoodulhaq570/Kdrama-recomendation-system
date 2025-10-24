# import json
# import re
# from bs4 import BeautifulSoup

# def extract_mydramalist_jsonld(html_path):
#     """Extracts structured data (JSON-LD) from MyDramaList HTML file."""
    
#     with open(html_path, 'r', encoding='utf-8') as f:
#         html = f.read()
    
#     soup = BeautifulSoup(html, 'html.parser')
    
#     # Find the main JSON-LD script containing @type=TVSeries
#     jsonld_tag = soup.find('script', type='application/ld+json', string=re.compile('TVSeries'))
#     if not jsonld_tag:
#         print("No TVSeries JSON-LD found")
#         return None
    
#     # Parse JSON safely
#     try:
#         data = json.loads(jsonld_tag.string)
#     except json.JSONDecodeError:
#         print("Invalid JSON format in script")
#         return None
    
#     # Extract main details
#     drama_info = {
#         'title': data.get('name'),
#         'url': data.get('url'),
#         'description': data.get('description'),
#         'image': data.get('image'),
#         'publisher': data.get('publisher', {}).get('name'),
#         'country': data.get('countryOfOrigin', {}).get('name'),
#         'genres': data.get('genre'),
#         'rating_value': data.get('aggregateRating', {}).get('ratingValue'),
#         'rating_count': data.get('aggregateRating', {}).get('ratingCount'),
#         'date_published': data.get('datePublished'),
#         'keywords': data.get('keywords'),
#         'actors': [
#             {
#                 'name': a.get('name'),
#                 'url': a.get('url'),
#                 'image': a.get('image')
#             }
#             for a in data.get('actor', [])
#         ],
#     }
    
#     return drama_info

# # Example usage
# info = extract_mydramalist_jsonld("The Heirs - MyDramaList.html")
# print(json.dumps(info, indent=2, ensure_ascii=False))


# import json
# import re
# from bs4 import BeautifulSoup

# def extract_mydramalist_data(html_path):
#     """Extracts complete drama data (including full description) from a MyDramaList HTML file."""
    
#     with open(html_path, 'r', encoding='utf-8') as f:
#         html = f.read()
    
#     soup = BeautifulSoup(html, 'html.parser')

#     # --------------------------------------------------------
#     # 1️⃣ Extract structured JSON-LD data
#     # --------------------------------------------------------
#     jsonld_tag = soup.find('script', type='application/ld+json', string=re.compile('TVSeries'))
#     data = {}
#     if jsonld_tag:
#         try:
#             data = json.loads(jsonld_tag.string)
#         except json.JSONDecodeError:
#             pass

#     drama_info = {
#         'title': data.get('name'),
#         'url': data.get('url'),
#         'description': data.get('description'),
#         'image': data.get('image'),
#         'publisher': data.get('publisher', {}).get('name'),
#         'country': data.get('countryOfOrigin', {}).get('name'),
#         'genres': data.get('genre'),
#         'rating_value': data.get('aggregateRating', {}).get('ratingValue'),
#         'rating_count': data.get('aggregateRating', {}).get('ratingCount'),
#         'date_published': data.get('datePublished'),
#         'keywords': data.get('keywords'),
#         'actors': [
#             {'name': a.get('name'), 'url': a.get('url'), 'image': a.get('image')}
#             for a in data.get('actor', [])
#         ],
#     }

#     # --------------------------------------------------------
#     # 2️⃣ Extract full description from HTML (if available)
#     # --------------------------------------------------------
#     desc_div = soup.find('div', class_=re.compile(r'(show-synopsis|show-synopsis__text|show-details-item__content)'))
#     if desc_div:
#         full_desc = desc_div.get_text(separator=' ', strip=True)
#         # Replace short description only if longer text found
#         if full_desc and len(full_desc) > len(str(drama_info.get('description', ''))):
#             drama_info['description'] = full_desc

#     return drama_info


# # Example usage
# info = extract_mydramalist_data("The Heirs - MyDramaList.html")
# print(json.dumps(info, indent=2, ensure_ascii=False))



# Save data into the json

# import json
# import re
# from bs4 import BeautifulSoup
# import os

# def extract_mydramalist_data(html_path):
#     """Extract detailed drama data (including alternate names and full description) from a MyDramaList HTML file."""
    
#     with open(html_path, 'r', encoding='utf-8') as f:
#         html = f.read()
    
#     soup = BeautifulSoup(html, 'html.parser')

#     # --------------------------------------------------------
#     # 1️⃣ Extract structured JSON-LD data
#     # --------------------------------------------------------
#     jsonld_tag = soup.find('script', type='application/ld+json', string=re.compile('TVSeries'))
#     data = {}
#     if jsonld_tag:
#         try:
#             data = json.loads(jsonld_tag.string)
#         except json.JSONDecodeError:
#             pass

#     drama_info = {
#         'title': data.get('name'),
#         'alternate_names': data.get('alternateName'),
#         'url': data.get('url'),
#         'description': data.get('description'),
#         'image': data.get('image'),
#         'publisher': data.get('publisher', {}).get('name'),
#         'country': data.get('countryOfOrigin', {}).get('name'),
#         'genres': data.get('genre'),
#         'rating_value': data.get('aggregateRating', {}).get('ratingValue'),
#         'rating_count': data.get('aggregateRating', {}).get('ratingCount'),
#         'date_published': data.get('datePublished'),
#         'keywords': data.get('keywords'),
#         'actors': [
#             {
#                 'name': a.get('name'),
#                 'url': a.get('url'),
#                 'image': a.get('image')
#             }
#             for a in data.get('actor', [])
#         ],
#     }

#     # --------------------------------------------------------
#     # 2️⃣ Extract full description from HTML (if available)
#     # --------------------------------------------------------
#     desc_div = soup.find('div', class_=re.compile(r'(show-synopsis|show-synopsis__text|show-details-item__content)'))
#     if desc_div:
#         full_desc = desc_div.get_text(separator=' ', strip=True)
#         if full_desc and len(full_desc) > len(str(drama_info.get('description', ''))):
#             drama_info['description'] = full_desc

#     return drama_info


# # --------------------------------------------------------
# # 3️⃣ Process a single file or all HTMLs in a folder
# # --------------------------------------------------------
# def process_folder(input_path, output_path="output.json"):
#     all_dramas = []

#     if os.path.isdir(input_path):
#         files = [f for f in os.listdir(input_path) if f.lower().endswith(".html")]
#         for file in files:
#             full_path = os.path.join(input_path, file)
#             info = extract_mydramalist_data(full_path)
#             if info:
#                 all_dramas.append(info)
#     else:
#         # Single file mode
#         info = extract_mydramalist_data(input_path)
#         if info:
#             all_dramas.append(info)

#     # --------------------------------------------------------
#     # 4️⃣ Save results to JSON (UTF-8 encoded)
#     # --------------------------------------------------------
#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(all_dramas, f, indent=2, ensure_ascii=False)

#     print(f" Extracted {len(all_dramas)} dramas and saved to '{output_path}'")


# # Example usage:
# # For one HTML file:
# process_folder("The Heirs - MyDramaList.html")

# # For a folder containing multiple saved pages:
# # process_folder("path_to_your_html_folder")


# Script to fetch HTML pages and save them locally but no N/A handling or other error handling

# import asyncio
# import random
# import re
# import os
# import pandas as pd
# from playwright.async_api import async_playwright, Route, expect
# from typing import Optional

# # ===============================================
# #  User-Agent rotation (to avoid detection)
# # ===============================================
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
# ]

# # ===============================================
# #  Block unnecessary resources (faster scraping)
# # ===============================================
# async def block_images_and_fonts(route: Route):
#     if route.request.resource_type in ["image", "font", "media"]:
#         await route.abort()
#     else:
#         await route.continue_()

# # ===============================================
# #  Fetch HTML of a single page using Playwright
# # ===============================================
# async def fetch_rendered_html_playwright(url: str) -> Optional[str]:
#     selected_user_agent = random.choice(USER_AGENTS)
#     print(f"Fetching: {url}")

#     try:
#         async with async_playwright() as p:
#             browser = await p.chromium.launch(
#                 headless=True,
#                 args=["--no-sandbox", "--disable-gpu", "--window-size=1920,1080"],
#             )
#             context = await browser.new_context(
#                 user_agent=selected_user_agent,
#                 viewport={"width": 1920, "height": 1080},
#                 ignore_https_errors=True,
#             )
#             page = await context.new_page()
#             await page.route("**/*", block_images_and_fonts)

#             await page.goto(url, timeout=120000)

#             # Wait for the title or key element to ensure full render
#             await expect(page.locator("h1")).to_have_text(re.compile(r"\S+"), timeout=60000)

#             await asyncio.sleep(2)
#             html = await page.content()

#             await browser.close()
#             return html

#     except Exception as e:
#         print(f"Error fetching {url}: {e}")
#         return None

# # ===============================================
# #  Main Function — read CSV & save HTML files
# # ===============================================
# async def main():
#     CSV_FILE = r"D:\Projects\Kdrama-recommendation\data_scrapper\mydramalist_data.csv"          # Path to your CSV file
#     OUTPUT_DIR = "dramas_html"       # Output folder
#     os.makedirs(OUTPUT_DIR, exist_ok=True)

#     df = pd.read_csv(CSV_FILE)

#     if "Title_URL" not in df.columns:
#         raise ValueError("CSV must contain a 'Title_URL' column!")

#     urls = df["Title_URL"].dropna().unique().tolist()

#     for i, url in enumerate(urls, start=1):
#         drama_id = url.strip().split("/")[-1]  # e.g., '18452-goblin'
#         output_path = os.path.join(OUTPUT_DIR, f"{drama_id}.html")

#         if os.path.exists(output_path):
#             print(f"Already saved — skipping: {drama_id}")
#             continue

#         print(f"[{i}/{len(urls)}] Downloading: {url}")
#         html_source = await fetch_rendered_html_playwright(url)

#         if html_source:
#             try:
#                 with open(output_path, "w", encoding="utf-8") as f:
#                     f.write(html_source)
#                 print(f"Saved: {output_path} ({len(html_source)} chars)")
#             except Exception as e:
#                 print(f"Error saving {output_path}: {e}")
#         else:
#             print(f"Skipped {url} due to fetch error.")

#         # Random short sleep to avoid being blocked
#         sleep_time = random.uniform(3, 7)
#         print(f"Sleeping {sleep_time:.1f}s...\n")
#         await asyncio.sleep(sleep_time)

# # ===============================================
# #  Entry Point
# # ===============================================
# if __name__ == "__main__":
#     asyncio.run(main())


# Script to fetch HTML pages and save them locally but with N/A handling or other error handling and downloading single html at a time


# import asyncio
# import random
# import re
# import os
# import pandas as pd
# from playwright.async_api import async_playwright, Route, expect
# from typing import Optional

# # ===============================================
# #  User-Agent rotation (to avoid detection)
# # ===============================================
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
# ]

# # ===============================================
# #  Block unnecessary resources (faster scraping)
# # ===============================================
# async def block_images_and_fonts(route: Route):
#     if route.request.resource_type in ["image", "font", "media"]:
#         await route.abort()
#     else:
#         await route.continue_()

# # ===============================================
# #  Fetch HTML of a single page using Playwright
# # ===============================================
# async def fetch_rendered_html_playwright(url: str) -> Optional[str]:
#     selected_user_agent = random.choice(USER_AGENTS)
#     print(f"Fetching: {url}")

#     try:
#         async with async_playwright() as p:
#             browser = await p.chromium.launch(
#                 headless=True,
#                 args=["--no-sandbox", "--disable-gpu", "--window-size=1920,1080"],
#             )
#             context = await browser.new_context(
#                 user_agent=selected_user_agent,
#                 viewport={"width": 1920, "height": 1080},
#                 ignore_https_errors=True,
#             )
#             page = await context.new_page()
#             await page.route("**/*", block_images_and_fonts)

#             await page.goto(url, timeout=120000)

#             # Wait for a key element (like the main title) to confirm loading
#             await expect(page.locator("h1")).to_have_text(re.compile(r"\S+"), timeout=60000)

#             await asyncio.sleep(2)
#             html = await page.content()

#             await browser.close()
#             return html

#     except Exception as e:
#         print(f"Error fetching {url}: {e}")
#         return None

# # ===============================================
# #  Main Function — read CSV & save HTML files
# # ===============================================
# async def main():
#     CSV_FILE = r"D:\Projects\Kdrama-recommendation\data_scrapper\mydramalist_data.csv"          # Path to your CSV file
#     OUTPUT_DIR = "dramas_html"       # Output folder
#     os.makedirs(OUTPUT_DIR, exist_ok=True)

#     df = pd.read_csv(CSV_FILE)

#     if "Title_URL" not in df.columns:
#         raise ValueError("CSV must contain a 'Title_URL' column!")

#     urls = df["Title_URL"].dropna().astype(str).tolist()

#     for i, url in enumerate(urls, start=1):
#         url = url.strip()

#         # Skip empty or invalid URLs
#         if not url or url.lower() in ["n/a", "none", "null"]:
#             print(f"[{i}] Skipping invalid URL: {url}")
#             continue

#         # Clean and extract a safe filename from the URL
#         if not url.startswith("https://mydramalist.com/"):
#             print(f"[{i}] Skipping non-MyDramaList URL: {url}")
#             continue

#         drama_id = url.split("/")[-1].strip()
#         if not drama_id:
#             print(f"[{i}] Skipping invalid drama ID from URL: {url}")
#             continue

#         output_path = os.path.join(OUTPUT_DIR, f"{drama_id}.html")

#         # Skip if file already exists
#         if os.path.exists(output_path):
#             print(f"[{i}] Already saved — skipping: {drama_id}")
#             continue

#         print(f"\n[{i}] Downloading: {url}")
#         html_source = await fetch_rendered_html_playwright(url)

#         # Skip if page could not be fetched
#         if not html_source:
#             print(f"[{i}] Failed to fetch page — skipping: {url}")
#             continue

#         try:
#             with open(output_path, "w", encoding="utf-8") as f:
#                 f.write(html_source)
#             print(f"[{i}] Saved: {output_path} ({len(html_source)} chars)")
#         except Exception as e:
#             print(f"[{i}] Error saving {output_path}: {e}")

#         # Random delay to reduce detection risk
#         sleep_time = random.uniform(3, 7)
#         print(f"Sleeping {sleep_time:.1f}s...\n")
#         await asyncio.sleep(sleep_time)

# # ===============================================
# #  Entry Point
# # ===============================================
# if __name__ == "__main__":
#     asyncio.run(main())


# Works parallel downloads with error handling and N/A handling

# import asyncio
# import random
# import os
# import pandas as pd
# from playwright.async_api import async_playwright, Route

# # ===============================================
# #  User-Agent rotation (to avoid detection)
# # ===============================================
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
# ]

# # ===============================================
# #  Block unnecessary resources (faster scraping)
# # ===============================================
# async def block_images_and_fonts(route: Route):
#     if route.request.resource_type in ["image", "font", "media"]:
#         await route.abort()
#     else:
#         await route.continue_()

# # ===============================================
# #  Download a single page safely (with retry)
# # ===============================================
# async def download_page(i, url, browser, output_dir, semaphore):
#     url = url.strip()

#     if not url or url.lower() in ["n/a", "none", "null"]:
#         print(f"[{i}] Skipping invalid URL: {url}")
#         return

#     if not url.startswith("https://mydramalist.com/"):
#         print(f"[{i}] Skipping non-MyDramaList URL: {url}")
#         return

#     drama_id = url.split("/")[-1].strip()
#     if not drama_id:
#         print(f"[{i}] Skipping invalid drama ID from URL: {url}")
#         return

#     output_path = os.path.join(output_dir, f"{drama_id}.html")
#     if os.path.exists(output_path):
#         print(f"[{i}] Already saved — skipping: {drama_id}")
#         return

#     async with semaphore:
#         selected_user_agent = random.choice(USER_AGENTS)
#         success = False

#         for attempt in range(2):  # retry twice if needed
#             context = await browser.new_context(
#                 viewport={"width": 1920, "height": 1080},
#                 ignore_https_errors=True,
#                 user_agent=selected_user_agent,
#             )

#             try:
#                 page = await context.new_page()
#                 await page.route("**/*", block_images_and_fonts)

#                 print(f"[{i}] ({attempt+1}/2) Downloading: {url}")
#                 await page.goto(url, timeout=45000, wait_until="domcontentloaded")
#                 await page.wait_for_selector("h1", timeout=10000)

#                 html_source = await page.content()

#                 with open(output_path, "w", encoding="utf-8") as f:
#                     f.write(html_source)
#                 print(f"[{i}] Saved: {output_path} ({len(html_source)} chars)")

#                 success = True
#                 await page.close()
#                 break

#             except Exception as e:
#                 print(f"[{i}] Attempt {attempt+1} failed for {url}: {e}")
#                 await asyncio.sleep(random.uniform(2, 4))

#             finally:
#                 await context.close()

#         if not success:
#             print(f"[{i}] Failed to fetch page: {url}")

#         await asyncio.sleep(random.uniform(1, 2))

# # ===============================================
# #  Main function — parallel downloads
# # ===============================================
# async def main():
#     CSV_FILE = r"D:\Projects\Kdrama-recommendation\data_scrapper\mydramalist_data.csv"
#     OUTPUT_DIR = "dramas_html"
#     os.makedirs(OUTPUT_DIR, exist_ok=True)

#     df = pd.read_csv(CSV_FILE)
#     if "Title_URL" not in df.columns:
#         raise ValueError("CSV must contain a 'Title_URL' column!")

#     urls = df["Title_URL"].dropna().astype(str).tolist()
#     semaphore = asyncio.Semaphore(5)  # adjust concurrency

#     async with async_playwright() as p:
#         browser = await p.chromium.launch(
#             headless=True,
#             args=["--no-sandbox", "--disable-gpu", "--window-size=1920,1080"]
#         )

#         tasks = [
#             download_page(i, url, browser, OUTPUT_DIR, semaphore)
#             for i, url in enumerate(urls, start=1)
#         ]
#         await asyncio.gather(*tasks)

#         await browser.close()

# # ===============================================
# #  Entry point
# # ===============================================
# if __name__ == "__main__":
#     asyncio.run(main())


# More robust parallel downloading logic
# concurrent file limit to 5, does not exhasust browser or out of memory problem also retry mechanism too

import asyncio
import random
import os
import pandas as pd
import re
from playwright.async_api import async_playwright, Route, TimeoutError

# -------------------------------------------
# User-Agent rotation
# -------------------------------------------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
]

# -------------------------------------------
# Block unnecessary resources
# -------------------------------------------
async def block_images_and_fonts(route: Route):
    if route.request.resource_type in ["image", "font", "media", "stylesheet"]:
        await route.abort()
    else:
        await route.continue_()

# -------------------------------------------
# Remove emojis safely
# -------------------------------------------
def remove_emojis(text):
    return re.sub(r'[\U00010000-\U0010ffff]', '', text)

# -------------------------------------------
# Download single page
# -------------------------------------------
async def download_page(i, url, context, output_dir, semaphore):
    url = url.strip()
    if not url or url.lower() in ["n/a", "none", "null"] or not url.startswith("https://mydramalist.com/"):
        print(f"[{i}] Skipping invalid URL: {url}")
        return

    drama_id = url.split("/")[-1].strip()
    if not drama_id:
        print(f"[{i}] Skipping invalid drama ID: {url}")
        return

    output_path = os.path.join(output_dir, f"{drama_id}.html")
    if os.path.exists(output_path):
        print(f"[{i}] Already saved — skipping: {drama_id}")
        return

    async with semaphore:
        success = False
        for attempt in range(2):
            try:
                page = await context.new_page()
                await page.route("**/*", block_images_and_fonts)

                print(f"[{i}] ({attempt+1}/2) Downloading: {url}")
                await page.goto(url, timeout=60000, wait_until="domcontentloaded")
                await page.wait_for_selector("h1", timeout=10000)

                await asyncio.sleep(random.uniform(1, 2.5))  # let JS finish
                html_source = await page.content()
                html_source = remove_emojis(html_source)

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(html_source)
                print(f"[{i}] Saved: {output_path} ({len(html_source)} chars)")

                success = True
                await page.close()
                break

            except TimeoutError:
                print(f"[{i}] Timeout for {url}, retrying...")
            except Exception as e:
                print(f"[{i}] Attempt {attempt+1} failed for {url}: {e}")
            finally:
                try:
                    await page.close()
                except:
                    pass
                await asyncio.sleep(random.uniform(1, 3))

        if not success:
            print(f"[{i}] Failed to fetch page: {url}")

# -------------------------------------------
# Main
# -------------------------------------------
async def main():
    CSV_FILE = r"D:\Projects\Kdrama-recommendation\data_scrapper\mydramalist_data.csv"
    OUTPUT_DIR = "dramas_html"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.read_csv(CSV_FILE)
    if "Title_URL" not in df.columns:
        raise ValueError("CSV must contain a 'Title_URL' column!")

    urls = df["Title_URL"].dropna().astype(str).tolist()
    semaphore = asyncio.Semaphore(5)  # safe concurrency level

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--window-size=1920,1080"]
        )

        # Reuse one context across all downloads
        selected_user_agent = random.choice(USER_AGENTS)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True,
            user_agent=selected_user_agent,
        )

        tasks = [
            asyncio.create_task(download_page(i, url, context, OUTPUT_DIR, semaphore))
            for i, url in enumerate(urls, start=1)
        ]
        await asyncio.gather(*tasks)

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
