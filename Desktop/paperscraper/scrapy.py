import csv
import requests
from bs4 import BeautifulSoup
from collections import Counter
from urllib.parse import urljoin, urlparse

# Step 1: Read the original CSV file
input_csv = 'original_data.csv'
rows = []

with open(input_csv, 'r', encoding='utf-8') as csvfile:
    # Use comma as the delimiter
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        rows.append(row)

# Step 2: Define the function to get the most frequent link
def get_most_frequent_link(url):
    # Skip obvious fails like YouTube links
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc.lower()
    skip_domains = ['youtube.com', 'youtu.be']

    if any(domain in netloc for domain in skip_domains):
        return 'Skipped (YouTube link)'

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; MyScraper/1.0)'}
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
    except requests.HTTPError as e:
        print(f"HTTP error fetching {url}: {e}")
        return f'HTTP error: {e}'
    except requests.ConnectionError as e:
        print(f"Connection error fetching {url}: {e}")
        return f'Connection error: {e}'
    except requests.Timeout as e:
        print(f"Timeout error fetching {url}: {e}")
        return f'Timeout error: {e}'
    except requests.RequestException as e:
        print(f"General error fetching {url}: {e}")
        return f'Error: {e}'

    soup = BeautifulSoup(response.content, 'html.parser')
    base_url = response.url  # Handle redirects

    # Extract and normalize links
    links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag.get('href')
        # Skip empty or None hrefs
        if not href or href.strip() == '':
            continue
        # Resolve relative links
        full_url = urljoin(base_url, href)
        links.append(full_url)

    if not links:
        return 'No links found'

    link_counts = Counter(links)
    most_common_links = link_counts.most_common()
    highest_frequency = most_common_links[0][1]
    # Get all links with the highest frequency
    most_frequent_links = [link for link, count in most_common_links if count == highest_frequency]

    # Return the first most frequent link
    return most_frequent_links[0]

# Step 3: Process each row and add the most frequent link
for row in rows:
    url = row['url']
    print(f"Processing URL: {url}")
    most_frequent_link = get_most_frequent_link(url)
    row['most_frequent_link'] = most_frequent_link

# Step 4: Write the updated data to a new CSV file
output_csv = 'updated_data.csv'
fieldnames = list(rows[0].keys())

with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
