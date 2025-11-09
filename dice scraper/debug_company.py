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
    print("Job link found!")
    print(f"Link text: '{job_link.get_text(strip=True)}'")
    print(f"Link href: {job_link.get('href', '')}")
    
    parent = job_link.find_parent(['div', 'article'])
    if parent:
        print("\nParent found!")
        
        # Find company link
        company_link = parent.find('a', href=re.compile(r'/company-profile/'))
        if company_link:
            print(f"\nCompany link found!")
            print(f"Company link text: '{company_link.get_text(strip=True)}'")
            print(f"Company link href: {company_link.get('href', '')}")
            print(f"Has 'logo' in text: {'logo' in company_link.get_text(strip=True).lower()}")
            
            # Extract company name from URL
            company_url = company_link.get('href', '')
            company_match = re.search(r'companyname=([^&]+)', company_url)
            if company_match:
                from urllib.parse import unquote
                company_from_url = unquote(company_match.group(1))
                print(f"Company from URL: {company_from_url}")
