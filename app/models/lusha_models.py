from pydantic import BaseModel
from typing import Optional


class LushaResult(BaseModel):
    linkedin_url: str
    person_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    company_domain: Optional[str] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    linkedin_url_response: Optional[str] = None


class EnrichRequest(BaseModel):
    linkedin_url: str
    reveal_emails: bool = True
    reveal_phones: bool = True
    partial_profile: bool = True


class EnrichListRequest(BaseModel):
    urls: list[str]
