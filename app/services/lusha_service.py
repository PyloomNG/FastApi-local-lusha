import time
import requests
from app.config import settings
from app.models.lusha_models import LushaResult


class LushaService:
    def __init__(self):
        self.api_key = settings.LUSHA_API_KEY
        self.endpoint = settings.LUSHA_ENDPOINT
        self.max_retries = settings.LUSHA_MAX_RETRIES
        self.delay = settings.LUSHA_DELAY_BETWEEN_REQUESTS

    def enrich_person(
        self,
        linkedin_url: str,
        reveal_emails: bool = True,
        reveal_phones: bool = True,
        partial_profile: bool = True
    ) -> LushaResult:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Using endpoint: {self.endpoint}")
        logger.info(f"API key: {self.api_key[:10]}...")

        headers = {
            "api_key": self.api_key,
            "Content-Type": "application/json"
        }

        params = {
            "linkedinUrl": linkedin_url,
            "revealEmails": str(reveal_emails).lower(),
            "revealPhones": str(reveal_phones).lower(),
            "partialProfile": str(partial_profile).lower()
        }

        logger.info(f"Request params: {params}")

        for attempt in range(1, self.max_retries + 1):
            logger.info(f"Attempt {attempt}: calling {self.endpoint}")
            response = requests.get(self.endpoint, headers=headers, params=params)
            logger.info(f"Response status: {response.status_code}")

            if response.status_code == 429:
                wait = 10 * attempt
                print(f"   Rate limit (attempt {attempt}/{self.max_retries}). Waiting {wait}s...")
                time.sleep(wait)
                continue

            if response.status_code != 200:
                raise Exception(f"Lusha error: {response.status_code} - {response.text}")

            break
        else:
            raise Exception("Rate limit exceeded after 3 retries.")

        data = response.json()

        # Lusha API response structure: contact.data contains the person
        contact = data.get("contact") or {}

        # Check for errors in response - still return result with linkedin_url
        error = contact.get("error") if contact else None
        if error:
            logger.warning(f"Lusha error: {error.get('name')} - {error.get('code')}")
            return LushaResult(linkedin_url=linkedin_url)

        person = (contact.get("data") or {}) if contact else {}

        # If no person data, return result with linkedin_url
        if not person:
            return LushaResult(linkedin_url=linkedin_url)

        # Extract email from emailAddresses array
        email = None
        email_addresses = person.get("emailAddresses", [])
        if email_addresses:
            email = email_addresses[0].get("email") if isinstance(email_addresses[0], dict) else None

        # Extract phone from phoneNumbers array
        phone = None
        phone_numbers = person.get("phoneNumbers", [])
        if phone_numbers:
            phone = phone_numbers[0].get("number") if isinstance(phone_numbers[0], dict) else None

        # Extract company info
        company_info = person.get("company", {})
        company_name = company_info.get("name") if company_info else None
        company_domains = company_info.get("domains", {}) if company_info else {}
        company_domain = company_domains.get("homepage") if company_domains else None

        # Extract job title
        job_title_info = person.get("jobTitle", {})
        job_title = job_title_info.get("title") if job_title_info else None

        # Extract location
        location_info = person.get("location", {})
        location = location_info.get("city") if location_info else None
        country = location_info.get("country") if location_info else None

        return LushaResult(
            linkedin_url=linkedin_url,
            person_id=person.get("personId"),
            first_name=person.get("firstName"),
            last_name=person.get("lastName"),
            full_name=person.get("fullName"),
            email=email,
            phone=phone,
            company_name=company_name,
            company_domain=company_domain,
            job_title=job_title,
            location=location,
            country=country,
            linkedin_url_response=person.get("socialLinks", {}).get("linkedin")
        )

    def enrich_list(self, urls: list[str]) -> list[LushaResult]:
        results = []

        for i, url in enumerate(urls):
            print(f"Processing {i + 1}/{len(urls)}: {url}")
            try:
                result = self.enrich_person(url)
                results.append(result)
            except Exception as e:
                print(f"Error enriching {url}: {e}")
                results.append(LushaResult(linkedin_url=url))

            if i < len(urls) - 1:
                time.sleep(self.delay)

        return results


lusha_service = LushaService()
