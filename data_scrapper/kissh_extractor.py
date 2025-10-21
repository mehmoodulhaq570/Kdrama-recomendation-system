import requests
from bs4 import BeautifulSoup
from typing import List, Dict


def extract_all_drama_info_from_kisskh(url: str) -> List[Dict]:
    """
    Fetches the content from the KissKH explore URL, finds all drama cards,
    and extracts the picture link, drama name, and episode count for each.

    Args:
        url: The URL of the KissKH Explore page.

    Returns:
        A list of dictionaries, where each dictionary contains the
        extracted information for one drama.
    """
    extracted_data = []

    try:
        # 1. Fetch the HTML content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        print(f"Fetching data from: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Raise an exception for bad status codes

        # 2. Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # --- Extraction Logic for KissKH structure ---
        # Based on typical web structure for such sites, we target the containers
        # that hold individual drama items. This often involves a 'col' or 'item' class.

        # Searching for elements that likely represent individual drama cards
        # (This class is a common element on KissKH explore pages)
        drama_cards = soup.find_all('div', class_='movie-card')

        if not drama_cards:
            print("Error: Could not find any drama cards with class 'movie-card'.")
            return [{"error": "No drama cards found. The website structure may have changed."}]

        print(f"Found {len(drama_cards)} drama items.")

        # 3. Iterate through each card and extract data
        for card in drama_cards:
            # --- Picture Link (Image Source) ---
            # The image is usually within an <img> tag inside the card.
            img_tag = card.find('img')
            picture_link = img_tag.get('src', 'Not Found') if img_tag else "Not Found"

            # --- Drama Name (Title) ---
            # The title is often inside an <a> tag with class 'title' or similar.
            title_tag = card.find('a', class_='title')
            drama_name = title_tag.text.strip() if title_tag else "Not Found"

            # --- Episode Count ---
            # The episode count is often a small badge or span (e.g., class 'ep').
            # On KissKH, this is often found in a span with class 'quality-text'.
            ep_tag = card.find('span', class_='quality-text')
            episode_number = ep_tag.text.strip() if ep_tag else "Not Found"

            # Store the extracted data
            extracted_data.append({
                "picture_link": picture_link,
                "drama_name": drama_name,
                "episode_number": episode_number
            })

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the URL: {e}")
        return [{"error": f"An error occurred while fetching the URL: {e}"}]
    except Exception as e:
        print(f"An error occurred during parsing: {e}")
        return [{"error": f"An error occurred during parsing: {e}"}]

    return extracted_data


# --- Example Usage ---

# The URL provided by the user
target_url = "https://kisskh.co/Explore?status=2&country=2&sub=1&type=1&order=1"

# Run the extraction function
results = extract_all_drama_info_from_kisskh(target_url)

# Display the results
print("\n" + "=" * 50)
print("Extracted Drama Information (First 5 Results):")
print("=" * 50)

# Print only the first 5 results for brevity
for i, drama in enumerate(results[:5]):
    print(f"\n--- Drama {i + 1} ---")
    print(f"Drama Name:   {drama.get('drama_name', 'N/A')}")
    print(f"Episode:      {drama.get('episode_number', 'N/A')}")
    print(f"Picture Link: {drama.get('picture_link', 'N/A')}")

if len(results) > 5:
    print(f"\n... and {len(results) - 5} more dramas.")

if results and "error" in results[0]:
    print("\nExtraction failed. Please check the error message above.")