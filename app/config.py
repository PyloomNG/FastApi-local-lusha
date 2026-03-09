import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Lusha API
    LUSHA_API_KEY: str = os.getenv("LUSHA_API_KEY", "")
    LUSHA_ENDPOINT: str = os.getenv("LUSHA_ENDPOINT", "https://api.lusha.com/v2/person")
    LUSHA_MAX_RETRIES: int = int(os.getenv("LUSHA_MAX_RETRIES", "3"))
    LUSHA_DELAY_BETWEEN_REQUESTS: int = int(os.getenv("LUSHA_DELAY_BETWEEN_REQUESTS", "2"))

    # App
    APP_NAME: str = "Lusha Enrich API"
    APP_VERSION: str = "1.0.0"

    # Bulk paths
    BASE_DIR: Path = Path(__file__).parent.parent
    INPUT_EXCEL: Path = BASE_DIR / "data" / "input.xlsx"
    OUTPUT_EXCEL: Path = BASE_DIR / "data" / "enriched_output.xlsx"


settings = Settings()
