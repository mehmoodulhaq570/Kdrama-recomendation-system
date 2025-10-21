# ========== Get the html of drama list =================

# import asyncio
# import random
# import re
# from playwright.async_api import async_playwright, Route, Playwright, expect
# from typing import Optional

# # List of common, modern User-Agents for rotation
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
# ]

# # --- Playwright Handler Functions ---

# async def block_images_and_fonts(route: Route):
#     """
#     Stops unnecessary resource requests (images and fonts) to save bandwidth
#     and significantly speed up page loading, preventing unnecessary timeouts.
#     """
#     if route.request.resource_type in ["image", "font", "media"]:
#         await route.abort()
#     else:
#         await route.continue_()


# async def fetch_rendered_html_playwright(url: str) -> Optional[str]:
#     """
#     Launches a robust Playwright browser (Chromium) to fetch the
#     fully rendered HTML content of a dynamic webpage.

#     Incorporates User-Agent rotation and a robust content waiting strategy.

#     Args:
#         url: The URL to fetch.

#     Returns:
#         The full HTML source code as a string, or None if an error occurs.
#     """
#     # Select a random User-Agent for this run
#     selected_user_agent = random.choice(USER_AGENTS)
#     print(f"Starting Playwright (Chromium) with User-Agent: {selected_user_agent[:40]}...")

#     try:
#         async with async_playwright() as p:
#             # Launch Chromium with headless=new for stability
#             browser = await p.chromium.launch(
#                 headless=True,
#                 args=[
#                     '--no-sandbox', 
#                     '--disable-gpu',
#                     '--window-size=1920,1080'
#                 ]
#             )
            
#             context = await browser.new_context(
#                 user_agent=selected_user_agent, # Rotated User-Agent applied here
#                 viewport={'width': 1920, 'height': 1080},
#                 ignore_https_errors=True 
#             )
            
#             page = await context.new_page()

#             # Enable network routing to block heavy resources
#             await page.route("**/*", block_images_and_fonts)

#             # 3. Navigate
#             print("Navigating to page (Image loading disabled)...")
#             # Overall navigation timeout set high
#             await page.goto(url, timeout=120000) 

#             # 4. Wait for Content using the most reliable method
#             # UPDATED SELECTOR: Targets the title link inside any drama box
#             content_selector = '.box h6.title a'
            
#             # CRITICAL FIX: Wait until the specific element's text is not empty.
#             locator = page.locator(content_selector).first
            
#             print(f"Waiting up to 60 seconds for the first drama title to appear...")
            
#             await expect(locator).to_have_text(
#                 re.compile(r'\S+'), # Regex to ensure the text is NOT empty (i.e., contains one or more non-whitespace characters)
#                 timeout=60000 # 60 seconds timeout
#             )

#             # Give a small buffer time for any final rendering
#             await asyncio.sleep(2)

#             # 5. Capture the final, rendered HTML source
#             print("Content loaded successfully. Capturing HTML source.")
#             content = await page.content()
            
#             await browser.close()
#             return content

#     except Exception as e:
#         print(f"\n--- PLAYWRIGHT ERROR ---")
#         print(f"Failed to fetch HTML. Error details: {e}")
#         print("------------------------")
#         return None

# # --- Main Execution Block ---

# def fetch_rendered_html(url: str) -> Optional[str]:
#     """Wrapper function to run the async Playwright function."""
#     return asyncio.run(fetch_rendered_html_playwright(url))

# OUTPUT_FILENAME = "mydramalist_popular.html"

# if __name__ == "__main__":
#     MYDRAMALIST_URL = "https://mydramalist.com/shows/popular"

#     # Fetch the HTML
#     html_source = fetch_rendered_html(MYDRAMALIST_URL)

#     # Process the result
#     if html_source:
#         print("\n--- CONTENT CAPTURED ---")
        
#         # Save the full HTML source to a file
#         try:
#             with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
#                 f.write(html_source)
#             print(f"Content successfully saved to {OUTPUT_FILENAME}")
#             print(f"Total HTML length: {len(html_source)} characters.")
#         except IOError as e:
#             print(f"Error saving file {OUTPUT_FILENAME}: {e}")
            
#     else:
#         print("\nFailed to capture HTML source.")


# ========== extract details from the html file =================

# from bs4 import BeautifulSoup
# import re
# import os

# def extract_drama_data_from_file(file_path):
#     """
#     Reads HTML content from a file path and extracts various drama details:
#     Title, Ranking, Rating, Media Info, Description, Title URL, and Image URL.
#     """
    
#     # 1. Read the HTML content from the local file
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             html_content = f.read()
#     except FileNotFoundError:
#         print(f"Error: The file '{file_path}' was not found. Please check the path and try again.")
#         return
#     except Exception as e:
#         print(f"An error occurred while reading the file: {e}")
#         return

#     # 2. Parse the HTML
#     soup = BeautifulSoup(html_content, 'html.parser')

#     # 3. Find all drama list items. The container is 'div.box'
#     drama_items = soup.find_all('div', class_='box')

#     extracted_data = []
#     BASE_URL = "https://mydramalist.com" # Base URL to prepend to the relative links

#     # 4. Loop through each item and extract the data
#     for item in drama_items:
#         try:
#             # Extract Title (from the <a> tag inside h6.title)
#             title_link_tag = item.find('h6', class_='title').find('a') if item.find('h6', class_='title') else None
#             title = title_link_tag.text.strip() if title_link_tag else 'N/A'
            
#             # === NEW EXTRACTION LOGIC: Title URL (href) ===
#             # Extract relative href and prepend BASE_URL
#             relative_href = title_link_tag.get('href') if title_link_tag and title_link_tag.get('href') else ''
#             title_url = BASE_URL + relative_href if relative_href else 'N/A'
            
#             # === NEW EXTRACTION LOGIC: Image URL ===
#             # The <img> tag is inside the first <a> tag within the item
#             image_tag = item.find('a', class_='block').find('img') if item.find('a', class_='block') else None
            
#             # Prioritize 'data-src' if it exists (for lazy loading), otherwise use 'src'
#             image_url = image_tag.get('data-src') or image_tag.get('src') if image_tag else 'N/A'

#             # Extract Ranking (from the <span> tag inside div.ranking)
#             ranking_tag = item.find('div', class_='ranking')
#             ranking = ranking_tag.find('span').text.strip() if ranking_tag and ranking_tag.find('span') else 'N/A'
            
#             # Extract Media Type/Year/Episodes
#             media_info_tag = item.find('span', class_='text-muted')
#             media_info = media_info_tag.text.strip() if media_info_tag else 'N/A'
            
#             # Extract Rating (from the <span> tag with class 'score')
#             rating_tag = item.find('span', class_='score')
#             rating = rating_tag.text.strip() if rating_tag else 'N/A'

#             # Extract Description: Find the last <p> tag within the 'content' div
#             content_column = item.find('div', class_='content')
#             description_paragraphs = content_column.find_all('p') if content_column else []
            
#             # The last <p> tag usually holds the description
#             description = description_paragraphs[-1].text.strip() if description_paragraphs else 'N/A'
            
#             # Clean up the description: remove the ellipsis if it's the last character
#             if description.endswith('…'):
#                 description = description[:-1].strip()

#             extracted_data.append({
#                 'Ranking': ranking,
#                 'Title': title,
#                 'Media_Info': media_info, 
#                 'Rating': rating,
#                 'Description': description,
#                 'Title_URL': title_url, # Added
#                 'Image_URL': image_url  # Added
#             })
#         except Exception as e:
#             drama_id = item.get('id', 'Unknown ID')
#             print(f"Error processing drama {drama_id}. Skipping entry. Error: {e}")
#             continue

#     # 5. Print the results
#     if extracted_data:
#         print("\n--- Extracted Drama Information ---")
#         for data in extracted_data:
#             print(f"Ranking: {data['Ranking']}")
#             print(f"Title: {data['Title']}")
#             print(f"Media Info: {data['Media_Info']}")
#             print(f"Rating: {data['Rating']}")
#             print(f"Description: {data['Description']}")
#             print(f"Title URL: {data['Title_URL']}")
#             print(f"Image URL: {data['Image_URL']}\n")
#     else:
#         print("\nNo complete drama items were found using the class 'box'.")

# # ----------------------------------------------------------------------------------
# # YOU MUST PROVIDE THE PATH TO YOUR HTML FILE HERE
# # ----------------------------------------------------------------------------------

# # Example usage:
# html_file_path = "D:\\Projects\\Kdrama-recommendation\\data_scrapper\\mydramalist_popular.html"
# # Call the function with the path
# extract_drama_data_from_file(html_file_path)


# # ============ Directly extract from the drama list page =============
# import asyncio
# import random
# import re
# import os
# import pandas as pd
# from playwright.async_api import async_playwright, Route, expect
# from bs4 import BeautifulSoup
# from typing import Optional

# # ======================================================
# # USER-AGENTS for rotation
# # ======================================================
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
# ]


# # ======================================================
# # PLAYWRIGHT: BLOCK UNNECESSARY REQUESTS
# # ======================================================
# async def block_images_and_fonts(route: Route):
#     """Blocks heavy resources like images, fonts, and videos."""
#     if route.request.resource_type in ["image", "font", "media"]:
#         await route.abort()
#     else:
#         await route.continue_()


# # ======================================================
# # FETCH RENDERED HTML (HEADLESS)
# # ======================================================
# async def fetch_rendered_html_playwright(url: str) -> Optional[str]:
#     selected_user_agent = random.choice(USER_AGENTS)
#     print(f"Starting Playwright with User-Agent: {selected_user_agent[:40]}...")

#     try:
#         async with async_playwright() as p:
#             browser = await p.chromium.launch(
#                 headless=True,
#                 args=['--no-sandbox', '--disable-gpu', '--window-size=1920,1080']
#             )

#             context = await browser.new_context(
#                 user_agent=selected_user_agent,
#                 viewport={'width': 1920, 'height': 1080},
#                 ignore_https_errors=True
#             )

#             page = await context.new_page()
#             await page.route("**/*", block_images_and_fonts)

#             print("Navigating to page...")
#             await page.goto(url, timeout=180000)

#             content_selector = '.box h6.title a'
#             locator = page.locator(content_selector).first
#             print("Waiting up to 60s for drama titles to load...")

#             await expect(locator).to_have_text(re.compile(r'\S+'), timeout=60000)
#             await asyncio.sleep(2)

#             print("Page loaded. Capturing HTML...")
#             content = await page.content()

#             await browser.close()
#             return content

#     except Exception as e:
#         print(f"\nPlaywright Error: {e}")
#         return None


# def fetch_rendered_html(url: str) -> Optional[str]:
#     """Synchronous wrapper."""
#     return asyncio.run(fetch_rendered_html_playwright(url))


# # ======================================================
# # BEAUTIFULSOUP: PARSE DRAMA DATA
# # ======================================================
# def extract_drama_data_from_html(html_content: str):
#     """Extracts drama details from the fetched HTML."""
#     soup = BeautifulSoup(html_content, 'html.parser')
#     drama_items = soup.find_all('div', class_='box')

#     extracted_data = []
#     BASE_URL = "https://mydramalist.com"

#     for item in drama_items:
#         try:
#             # Title & URL
#             title_tag = item.find('h6', class_='title')
#             title_link_tag = title_tag.find('a') if title_tag else None
#             title = title_link_tag.text.strip() if title_link_tag else 'N/A'
#             href = title_link_tag.get('href', '') if title_link_tag else ''
#             title_url = BASE_URL + href if href else 'N/A'

#             # Image
#             image_tag = item.find('a', class_='block')
#             img = image_tag.find('img') if image_tag else None
#             image_url = img.get('data-src') or img.get('src') if img else 'N/A'

#             # Ranking
#             rank_tag = item.find('div', class_='ranking')
#             ranking = rank_tag.find('span').text.strip() if rank_tag and rank_tag.find('span') else 'N/A'

#             # Media Info (Year / Episodes)
#             media_info_tag = item.find('span', class_='text-muted')
#             media_info = media_info_tag.text.strip() if media_info_tag else 'N/A'

#             # Rating
#             rating_tag = item.find('span', class_='score')
#             rating = rating_tag.text.strip() if rating_tag else 'N/A'

#             # Description
#             content_col = item.find('div', class_='content')
#             paragraphs = content_col.find_all('p') if content_col else []
#             description = paragraphs[-1].text.strip() if paragraphs else 'N/A'
#             if description.endswith('…'):
#                 description = description[:-1].strip()

#             extracted_data.append({
#                 "Ranking": ranking,
#                 "Title": title,
#                 "Media_Info": media_info,
#                 "Rating": rating,
#                 "Description": description,
#                 "Title_URL": title_url,
#                 "Image_URL": image_url
#             })

#         except Exception as e:
#             print(f"Error parsing one item: {e}")
#             continue

#     return extracted_data


# # ======================================================
# # MAIN EXECUTION
# # ======================================================
# if __name__ == "__main__":
#     MYDRAMALIST_URL = "https://mydramalist.com/shows/popular"
#     OUTPUT_HTML = "mydramalist_popular.html"
#     OUTPUT_CSV = "mydramalist_popular.csv"

#     print("Fetching HTML using Playwright...")
#     html_source = fetch_rendered_html(MYDRAMALIST_URL)

#     if not html_source:
#         print("Failed to fetch HTML.")
#         exit()

#     # Save raw HTML
#     with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
#         f.write(html_source)
#     print(f"Saved raw HTML -> {OUTPUT_HTML}")

#     # Extract data
#     dramas = extract_drama_data_from_html(html_source)

#     if dramas:
#         print(f"\nExtracted {len(dramas)} dramas:")
#         for d in dramas[:5]:  # Preview first 5
#             print(f"- {d['Title']} ({d['Rating']})")

#         # Save to CSV
#         df = pd.DataFrame(dramas)
#         df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
#         print(f"Drama data saved to {OUTPUT_CSV}")
#     else:
#         print("No drama data extracted.")



import asyncio
import random
import re
import os
from playwright.async_api import async_playwright, Route, expect
from typing import Optional

# ===============================================
#  User-Agent rotation (to avoid detection)
# ===============================================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
]

# ===============================================
#  Helper to block unnecessary resources
# ===============================================
async def block_images_and_fonts(route: Route):
    if route.request.resource_type in ["image", "font", "media"]:
        await route.abort()
    else:
        await route.continue_()

# ===============================================
#  Main Playwright HTML Fetch Function
# ===============================================
async def fetch_rendered_html_playwright(url: str) -> Optional[str]:
    selected_user_agent = random.choice(USER_AGENTS)
    print(f"Fetching: {url} (UA: {selected_user_agent[:40]}...)")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-gpu", "--window-size=1920,1080"],
            )
            context = await browser.new_context(
                user_agent=selected_user_agent,
                viewport={"width": 1920, "height": 1080},
                ignore_https_errors=True,
            )
            page = await context.new_page()
            await page.route("**/*", block_images_and_fonts)

            await page.goto(url, timeout=120000)

            # Wait for at least one drama title to appear
            content_selector = ".box h6.title a"
            locator = page.locator(content_selector).first
            await expect(locator).to_have_text(re.compile(r"\S+"), timeout=60000)

            await asyncio.sleep(2)
            html = await page.content()
            await browser.close()
            return html

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

# ===============================================
#  Main Async Runner
# ===============================================
async def main():
    BASE_URL = "https://mydramalist.com/shows/popular?page={}"
    OUTPUT_DIR = "html_pages"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for page_num in range(1, 251):
        url = BASE_URL.format(page_num)
        output_path = os.path.join(OUTPUT_DIR, f"page_{page_num}.html")

        # Skip if already exists
        if os.path.exists(output_path):
            print(f"Page {page_num} already exists — skipping.")
            continue

        print(f"\nStarting page {page_num}")
        html_source = await fetch_rendered_html_playwright(url)

        if html_source:
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(html_source)
                print(f"Saved: {output_path} ({len(html_source)} chars)")
            except Exception as e:
                print(f"Error saving page {page_num}: {e}")
        else:
            print(f"Skipped page {page_num} due to fetch error.")

        # Sleep to avoid rate-limiting
        sleep_time = random.uniform(3, 6)
        print(f"Sleeping {sleep_time:.1f}s...\n")
        await asyncio.sleep(sleep_time)

# ===============================================
#  Entry Point
# ===============================================
if __name__ == "__main__":
    asyncio.run(main())
