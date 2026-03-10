import time
from typing import Union
import pandas as pd
import numpy as np
import requests
from app.config import settings


class BulkService:
    def __init__(self):
        self.api_key = settings.LUSHA_API_KEY
        self.endpoint = settings.LUSHA_ENDPOINT
        self.max_retries = settings.LUSHA_MAX_RETRIES
        self.delay = settings.LUSHA_DELAY_BETWEEN_REQUESTS

    def _clean_linkedin_url(self, url: str) -> str:
        """Extract base LinkedIn URL without extra parameters"""
        if "?" in url:
            url = url.split("?")[0]
        # Remove trailing slash
        if url.endswith("/"):
            url = url[:-1]
        return url

    def _enrich_single(self, linkedin_url: str) -> dict:
        """Enrich a single LinkedIn URL"""
        clean_url = self._clean_linkedin_url(linkedin_url)
        print(f"   Clean URL: {clean_url}")

        headers = {
            "api_key": self.api_key,
            "Content-Type": "application/json"
        }

        params = {
            "linkedinUrl": clean_url,
            "revealEmails": "true",
            "revealPhones": "true",
            "partialProfile": "true"
        }

        for attempt in range(1, self.max_retries + 1):
            response = requests.get(self.endpoint, headers=headers, params=params)

            if response.status_code == 429:
                wait = 10 * attempt
                print(f"   Rate limit (attempt {attempt}/{self.max_retries}). Waiting {wait}s...")
                time.sleep(wait)
                continue

            if response.status_code != 200:
                print(f"   Error: {response.status_code} - {response.text}")
                return self._empty_result(linkedin_url=linkedin_url)

            break
        else:
            return self._empty_result(linkedin_url=linkedin_url)

        try:
            data = response.json()
            # If response is not a dict, return empty result
            if not isinstance(data, dict):
                print(f"   Invalid response format")
                return self._empty_result(linkedin_url=clean_url)

            # Lusha API response structure: contact.data contains the person
            contact = data.get("contact") or {}

            # Check for errors in response - still return result with linkedin_url
            error = contact.get("error") if isinstance(contact, dict) else None
            if error:
                print(f"   Lusha error: {error.get('name')} - {error.get('code')}")
                # Return result with linkedin_url but empty fields
                return self._empty_result(linkedin_url=clean_url)

            # If contact is not a dict or has no data, return empty
            if not isinstance(contact, dict):
                print(f"   No contact data")
                return self._empty_result(linkedin_url=clean_url)

            person = (contact.get("data") or {}) if isinstance(contact, dict) else {}

            # If no person data, return result with linkedin_url
            if not person or not isinstance(person, dict):
                print(f"   No person data found in response")
                return self._empty_result(linkedin_url=clean_url)

            # Extract email from emailAddresses array
            email = None
            email_addresses = person.get("emailAddresses") or []
            if email_addresses and isinstance(email_addresses, list):
                email = email_addresses[0].get("email") if isinstance(email_addresses[0], dict) else None

            # Extract phone from phoneNumbers array
            phone = None
            phone_numbers = person.get("phoneNumbers") or []
            if phone_numbers and isinstance(phone_numbers, list):
                phone = phone_numbers[0].get("number") if isinstance(phone_numbers[0], dict) else None

            # Extract company info
            company_info = person.get("company") or {}
            company_name = company_info.get("name") if isinstance(company_info, dict) else None
            company_domains = company_info.get("domains") or {} if isinstance(company_info, dict) else {}
            company_domain = company_domains.get("homepage") if isinstance(company_domains, dict) else None

            # Extract job title
            job_title_info = person.get("jobTitle") or {}
            job_title = job_title_info.get("title") if isinstance(job_title_info, dict) else None

            # Extract location
            location_info = person.get("location") or {}
            location = location_info.get("city") if isinstance(location_info, dict) else None
            country = location_info.get("country") if isinstance(location_info, dict) else None

            # Extract social links
            social_links = person.get("socialLinks") or {}
            linkedin_url_response = social_links.get("linkedin") if isinstance(social_links, dict) else None

            return {
                "first_name": person.get("firstName"),
                "last_name": person.get("lastName"),
                "full_name": person.get("fullName"),
                "job_title": job_title,
                "location": location,
                "linkedin_url": linkedin_url_response,
                "email": email,
                "phone": phone,
                "company_name": company_name,
                "company_domain": company_domain,
                "country": country,
            }
        except Exception as e:
            print(f"   Parse error: {e}")
            return self._empty_result(linkedin_url=clean_url)

    def _empty_result(self, linkedin_url: str = None) -> dict:
        return {
            "first_name": None,
            "last_name": None,
            "full_name": None,
            "job_title": None,
            "location": None,
            "linkedin_url": linkedin_url,
            "email": None,
            "phone": None,
            "company_name": None,
            "company_domain": None,
            "country": None,
        }

    def enrich_excel(self, return_json: bool = False) -> Union[str, list[dict]]:
        """Process local Excel and save enriched version or return JSON"""
        input_path = settings.INPUT_EXCEL

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        df = pd.read_excel(input_path)

        # Ensure columns exist
        if "Email" not in df.columns:
            df["Email"] = None
        if "Phone" not in df.columns:
            df["Phone"] = None
        if "First Name" not in df.columns:
            df["First Name"] = None
        if "Last Name" not in df.columns:
            df["Last Name"] = None
        if "Company" not in df.columns:
            df["Company"] = None
        if "Job Title" not in df.columns:
            df["Job Title"] = None
        if "Location" not in df.columns:
            df["Location"] = None
        if "Country" not in df.columns:
            df["Country"] = None

        total = len(df)
        print(f"\nStarting enrichment of {total} records...")

        for i, row in df.iterrows():
            profile_url = row.get("profileUrl")

            if pd.isna(profile_url) or not profile_url:
                print(f"  [{i+1}/{total}] No URL, skipping...")
                continue

            print(f"  [{i+1}/{total}] Enriching: {profile_url}")

            try:
                result = self._enrich_single(profile_url)

                df.at[i, "Email"] = result.get("email")
                df.at[i, "Phone"] = result.get("phone")
                df.at[i, "First Name"] = result.get("first_name")
                df.at[i, "Last Name"] = result.get("last_name")
                df.at[i, "Company"] = result.get("company_name")
                df.at[i, "Job Title"] = result.get("job_title")
                df.at[i, "Location"] = result.get("location")
                df.at[i, "Country"] = result.get("country")
            except Exception as e:
                print(f"  [{i+1}/{total}] Error processing: {e}")
                # Continue with next record

            # Wait between requests
            if i < total - 1:
                print(f"    Waiting {}s...".format(self.delay))
                time.sleep(self.delay)

        if return_json:
            df_clean = df.replace({np.nan: None})
            return df_clean.to_dict(orient="records")

        output_path = settings.OUTPUT_EXCEL
        df.to_excel(output_path, index=False)

        print(f"Enrichment completed! Output: {output_path}")
        return str(output_path)


bulk_service = BulkService()
