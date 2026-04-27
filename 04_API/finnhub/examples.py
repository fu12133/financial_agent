import finnhub
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Setup client
finnhub_client = finnhub.Client(api_key=os.environ["FINNHUB_API_KEY"])

# 基础免费 04_API test
print("\n=== Company Profile ===")
print(finnhub_client.company_profile2(symbol="AAPL"))

print("\n=== Company News ===")
print(finnhub_client.company_news("AAPL", _from="2026-01-01", to="2026-04-20"))

print("\n=== General News ===")
print(finnhub_client.general_news("forex", min_id=0))
