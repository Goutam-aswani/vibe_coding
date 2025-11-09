from main import scrape_dice_jobs
from bs4 import BeautifulSoup
import requests
import re

# Make a direct request to see the HTML structure
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

url = "https://www.dice.com/jobs?q=gen+ai&filters.workplaceTypes=Remote&page=1"
response = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(response.content, 'lxml')

# Find first job link
job_link = soup.find('a', href=re.compile(r'/job-detail/'))
if job_link:
    parent = job_link.find_parent(['div', 'article'])
    if parent:
        # Find ALL company profile links  
        company_links = parent.find_all('a', href=re.compile(r'/company-profile/'))
        print(f"Found {len(company_links)} company links")
        
        for i, clink in enumerate(company_links, 1):
            print(f"\n--- Company Link {i} ---")
            text = clink.get_text(strip=True)
            print(f"Text: '{text}' (length: {len(text)})")
            print(f"Text repr: {repr(text)}")
            print(f"Has children: {len(list(clink.children))}")
            print(f"Children: {[child.name for child in clink.children if hasattr(child, 'name')]}")
            if text:
                print(f"'logo' in text.lower(): {'logo' in text.lower()}")
