"""
Job scraper module for foundit.in using their API
"""
import requests
import logging
from typing import List, Dict, Any
from datetime import datetime
from models import Job, Company, Location, Salary, Experience, Skill

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FounditScraper:
    """Scraper for foundit.in job listings using their API"""
    
    BASE_URL = "https://www.foundit.in/home/api/searchResultsPage"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.foundit.in/search/'
        })
    
    def scrape_jobs(
        self, 
        job_roles: List[str], 
        experience_range: str = "0~0",
        country: str = "India",
        limit_per_role: int = 100
    ) -> tuple[List[Job], Dict[str, int]]:
        """
        Scrape jobs for multiple job roles
        
        Args:
            job_roles: List of job role queries (e.g., ['gen ai engineer', 'data scientist'])
            experience_range: Experience range in format 'min~max'
            country: Country to search in
            limit_per_role: Maximum jobs to fetch per role
            
        Returns:
            Tuple of (list of Job objects, dict of jobs count per role)
        """
        all_jobs = []
        jobs_per_role = {}
        seen_job_ids = set()  # To avoid duplicates across different roles
        
        for role in job_roles:
            logger.info(f"Scraping jobs for role: {role}")
            
            try:
                jobs = self._scrape_single_role(
                    role, 
                    experience_range, 
                    country, 
                    limit_per_role
                )
                
                # Filter out duplicates
                unique_jobs = []
                for job in jobs:
                    if job.job_id not in seen_job_ids:
                        seen_job_ids.add(job.job_id)
                        unique_jobs.append(job)
                
                jobs_per_role[role] = len(unique_jobs)
                all_jobs.extend(unique_jobs)
                
                logger.info(f"Found {len(unique_jobs)} unique jobs for '{role}'")
                
            except Exception as e:
                logger.error(f"Error scraping role '{role}': {e}")
                jobs_per_role[role] = 0
        
        return all_jobs, jobs_per_role
    
    def _scrape_single_role(
        self, 
        query: str, 
        experience_range: str,
        country: str,
        limit: int
    ) -> List[Job]:
        """
        Scrape jobs for a single role
        
        Args:
            query: Job role search query
            experience_range: Experience range
            country: Country to search
            limit: Maximum jobs to fetch
            
        Returns:
            List of Job objects
        """
        jobs = []
        start = 0
        batch_size = 20  # API seems to work well with 20 per request
        
        while len(jobs) < limit:
            params = {
                'start': start,
                'limit': batch_size,
                'query': query,
                'experienceRanges': experience_range,
                'countries': country,
                'variantName': 'DEFAULT'
            }
            
            try:
                response = self.session.get(
                    self.BASE_URL, 
                    params=params, 
                    timeout=30
                )
                
                if response.status_code != 200:
                    logger.error(f"API returned status {response.status_code}")
                    break
                
                data = response.json()
                
                # Jobs are in data['data'] array
                job_listings = data.get('data', [])
                
                if not job_listings:
                    logger.info(f"No more jobs found for '{query}' at start={start}")
                    break
                
                # Parse each job
                for job_data in job_listings:
                    try:
                        job = self._parse_job(job_data)
                        jobs.append(job)
                    except Exception as e:
                        logger.warning(f"Failed to parse job {job_data.get('id', 'unknown')}: {e}")
                        continue
                
                # Move to next batch
                start += batch_size
                
                # If we got fewer than batch_size, we've reached the end
                if len(job_listings) < batch_size:
                    break
                    
            except Exception as e:
                logger.error(f"Error fetching jobs: {e}")
                break
        
        return jobs[:limit]  # Return only up to limit
    
    def _parse_job(self, data: Dict[str, Any]) -> Job:
        """
        Parse raw job data from API into Job model
        
        Args:
            data: Raw job data from API
            
        Returns:
            Job object
        """
        # Parse company
        company_data = data.get('company', {})
        company = Company(
            name=company_data.get('name', 'Unknown'),
            company_id=company_data.get('companyId', 0),
            logo_url=company_data.get('logo')
        )
        
        # Parse locations
        locations = []
        for loc_data in data.get('locations', []):
            location = Location(
                city=loc_data.get('city'),
                state=loc_data.get('state'),
                country=loc_data.get('country', 'India'),
                lat_lon=loc_data.get('latLon')
            )
            locations.append(location)
        
        # Parse salary
        min_sal = data.get('minimumSalary', {})
        max_sal = data.get('maximumSalary', {})
        min_amount = min_sal.get('absoluteValue', 0)
        max_amount = max_sal.get('absoluteValue', 0)
        
        salary = Salary(
            currency=min_sal.get('currency', 'INR'),
            minimum=min_amount,
            maximum=max_amount,
            is_disclosed=(min_amount > 0 or max_amount > 0)
        )
        
        # Parse experience
        min_exp = data.get('minimumExperience', {})
        max_exp = data.get('maximumExperience', {})
        
        experience = Experience(
            minimum_years=min_exp.get('years', 0),
            maximum_years=max_exp.get('years', 0)
        )
        
        # Parse skills
        skills = []
        for skill_data in data.get('skills', []):
            skill = Skill(
                name=skill_data.get('text', ''),
                skill_id=skill_data.get('id')
            )
            skills.append(skill)
        
        # Parse IT skills
        it_skills = []
        for skill_data in data.get('itSkills', []):
            skill = Skill(
                name=skill_data.get('text', ''),
                skill_id=skill_data.get('id')
            )
            it_skills.append(skill)
        
        # Parse posted date (Unix timestamp in milliseconds)
        posted_timestamp = data.get('postedAt', 0)
        posted_date = datetime.fromtimestamp(posted_timestamp / 1000) if posted_timestamp else datetime.now()
        
        # Create Job object
        job = Job(
            job_id=str(data.get('id', data.get('jobId', 'unknown'))),
            title=data.get('title', 'Unknown Title'),
            company=company,
            locations=locations,
            description=data.get('description', ''),
            experience=experience,
            salary=salary,
            skills=skills,
            it_skills=it_skills,
            apply_url=data.get('redirectUrl', ''),
            posted_date=posted_date,
            job_types=data.get('jobTypes', []),
            employment_types=data.get('employmentTypes', []),
            industries=data.get('industries', []),
            functions=data.get('functions', [])
        )
        
        return job
