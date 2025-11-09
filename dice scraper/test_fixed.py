import requests
import json

# Test the scraper function directly
from main import scrape_dice_jobs

print("Testing the updated scraper...")
print("-" * 50)

result = scrape_dice_jobs(
    search_query="gen ai",
    workplace_type="Remote",
    page=1
)

# Convert to dict
result_dict = result.model_dump()

# Print first 3 jobs to check
print(f"Total jobs found: {result_dict['total_jobs']}")
print("\nFirst 3 jobs:")
print("=" * 50)

for i, job in enumerate(result_dict['jobs'][:3], 1):
    print(f"\nJob {i}:")
    print(f"  Title: {job['title'] or 'MISSING'}")
    print(f"  Company: {job['company'] or 'MISSING'}")
    print(f"  Location: {job['location']}")
    print(f"  Posted: {job['posted_date']}")
    print(f"  Salary: {job['salary']}")
    print(f"  Type: {job['job_type']}")
    print(f"  Description: {job['description'][:100] if job['description'] else 'MISSING'}...")
    print(f"  URL: {job['job_url']}")

# Save to file
with open('test_fixed_result.json', 'w', encoding='utf-8') as f:
    json.dump(result_dict, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 50)
print("Full results saved to: test_fixed_result.json")
