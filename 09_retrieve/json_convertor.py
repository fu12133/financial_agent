import json
import os
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests library not installed, cloud reading functionality will be unavailable. Please run: pip install requests")


def load_json_from_url(url: str, headers: Optional[Dict[str, str]] = None,
                       timeout: int = 30) -> Dict[str, Any]:
    """
    Load JSON data from URL (supports HTTP/HTTPS)
    :param url: URL address of JSON data
    :param headers: Optional HTTP request headers (e.g., authentication token)
    :param timeout: Request timeout in seconds
    :return: Parsed JSON dictionary
    """
    if not REQUESTS_AVAILABLE:
        logger.error("requests library not installed, cannot read JSON from URL")
        return {}

    try:
        logger.info(f"Reading JSON from URL: {url}")

        # Default request headers
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }

        # Merge custom headers
        if headers:
            default_headers.update(headers)

        response = requests.get(url, headers=default_headers, timeout=timeout)
        response.raise_for_status()  # Raise exception if status code is not 200

        # Detect encoding
        response.encoding = response.apparent_encoding

        data = response.json()
        logger.info(f"✅ Successfully read JSON from URL, data size: {len(response.text)} characters")
        return data

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ HTTP request failed: {e}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parsing failed: {e}")
        return {}
    except Exception as e:
        logger.error(f"❌ Unknown error occurred while reading URL: {e}")
        return {}


def load_json_from_cloud_storage(storage_type: str, **kwargs) -> Dict[str, Any]:
    """
    Load JSON from cloud storage service (extension point, can be implemented as needed)
    :param storage_type: Cloud storage type ('aliyun_oss', 'aws_s3', 'azure_blob', etc.)
    :param kwargs: Cloud storage specific parameters
    :return: Parsed JSON dictionary
    """
    logger.warning(f"Cloud storage type '{storage_type}' not yet implemented, please use load_json_from_url")
    return {}


def load_apple_analysis_json(file_path: str, is_url: bool = False,
                             headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Load Apple company analysis JSON file (supports local file or cloud URL)
    :param file_path: JSON file path or URL address
    :param is_url: Whether it's a URL address (default False, i.e., local file)
    :param headers: If URL, optional HTTP request headers
    :return: Parsed JSON dictionary
    """
    if is_url:
        return load_json_from_url(file_path, headers)

    # Local file reading (original logic)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"✅ Successfully read JSON from local file: {file_path}")
        return data
    except FileNotFoundError:
        logger.error(f"❌ File not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        logger.error("❌ JSON format parsing failed")
        return {}


def parse_llm_raw_response(raw_response: str) -> Dict[str, Any]:
    """
    Parse raw_response JSON string directly into JSON object

    :param raw_response: LLM returned raw response string (JSON format)
    :return: Parsed dictionary
    """
    if not raw_response or not isinstance(raw_response, str):
        return {}

    try:
        # Parse JSON string directly
        parsed = json.loads(raw_response)
        return parsed
    except json.JSONDecodeError:
        # If parsing failed, try to extract JSON fragment
        try:
            start_idx = raw_response.find('{')
            end_idx = raw_response.rfind('}')

            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = raw_response[start_idx:end_idx + 1]
                return json.loads(json_str)
        except:
            pass

        return {}


def extract_core_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract core metrics from JSON
    :param data: Parsed JSON dictionary
    :return: Core metrics dictionary
    """
    if not data:
        return {}

    # Basic information
    basic_info = {
        "Stock Ticker": data.get("ticker"),
        "Company Name": data.get("company_name"),
        "Analysis Period (Days)": data.get("analysis_period_days"),
        "Analysis Start Date": data.get("start_date"),
        "Analysis End Date": data.get("end_date"),
        "TOP News Count": data.get("total_news")
    }

    # News type statistics
    event_types = data.get("news_overview", {}).get("event_types", {})
    # News sentiment statistics
    sentiments = data.get("news_overview", {}).get("sentiments", {})

    # LLM analysis core scores
    llm_scores = {}
    llm_analysis = data.get("llm_analysis", {})

    if llm_analysis and "raw_response" in llm_analysis:
        # Parse raw_response string directly
        parsed_llm = parse_llm_raw_response(llm_analysis["raw_response"])

        if parsed_llm:
            llm_scores = {
                "Financial Impact Score": parsed_llm.get("financial_impact", {}).get("score"),
                "Operational Impact Score": parsed_llm.get("operational_impact", {}).get("score"),
                "Market Impact Score": parsed_llm.get("market_impact", {}).get("score"),
                "Regulatory Impact Score": parsed_llm.get("regulatory_impact", {}).get("score"),
                "Strategic Impact Score": parsed_llm.get("strategic_impact", {}).get("score")
            }

    # Integrate all core metrics
    core_metrics = {
        "Basic Information": basic_info,
        "News Type Distribution": event_types,
        "News Sentiment Distribution": sentiments,
        "LLM Analysis Scores": llm_scores
    }

    return core_metrics


def extract_full_llm_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract complete LLM analysis result
    
    Supports two formats:
    1. With raw_response string (needs parsing)
    2. Already parsed dictionary structure

    :param data: Raw data dictionary
    :return: Parsed complete LLM analysis result
    """
    if not data:
        return {}

    llm_analysis = data.get("llm_analysis", {})
    
    if not llm_analysis:
        return {}
    
    # Case 1: If llm_analysis contains raw_response string, parse it
    if isinstance(llm_analysis, dict) and "raw_response" in llm_analysis:
        logger.info("📝 Found raw_response, parsing it...")
        return parse_llm_raw_response(llm_analysis["raw_response"])
    
    # Case 2: If llm_analysis is already a parsed dictionary with analysis structure
    if isinstance(llm_analysis, dict) and ("storyline" in llm_analysis or "financial_impact" in llm_analysis):
        logger.info("✅ LLM analysis already parsed, using directly")
        return llm_analysis
    
    # Case 3: If llm_analysis itself is the parsed result
    if isinstance(llm_analysis, dict):
        logger.info("✅ Using llm_analysis as-is")
        return llm_analysis

    return {}


def analyze_news_sentiment(sentiments: Dict[str, int]) -> str:
    """
    Simple news sentiment analysis
    :param sentiments: Sentiment statistics dictionary
    :return: Sentiment analysis conclusion
    """
    total = sum(sentiments.values())
    if total == 0:
        return "No sentiment data"

    positive_ratio = (sentiments.get("positive", 0) / total) * 100
    negative_ratio = (sentiments.get("negative", 0) / total) * 100
    neutral_ratio = (sentiments.get("neutral", 0) / total) * 100

    conclusion = f"Sentiment distribution: Positive {positive_ratio:.1f}% | Negative {negative_ratio:.1f}% | Neutral {neutral_ratio:.1f}%; "
    if positive_ratio > negative_ratio + 10:
        conclusion += "Overall sentiment is positive"
    elif negative_ratio > positive_ratio + 10:
        conclusion += "Overall sentiment is negative"
    else:
        conclusion += "Overall sentiment is primarily neutral"

    return conclusion


def main():
    # ==================== Example 1: Read from local file ====================
    print("=" * 60)
    print("Example 1: Reading JSON from local file")
    print("=" * 60)

    local_json_path = "apple_company_analysis.json"
    if os.path.exists(local_json_path):
        raw_data = load_apple_analysis_json(local_json_path, is_url=False)
        if raw_data:
            _print_analysis_result(raw_data)
    else:
        print(f"⚠️  Local file {local_json_path} does not exist, skipping this example")

    # ==================== Example 2: Read from cloud URL ====================
    print("\n" + "=" * 60)
    print("Example 2: Reading JSON from cloud URL")
    print("=" * 60)

    # Replace with your cloud JSON URL
    cloud_json_url = "https://example.com/apple_company_analysis.json"

    # If authentication is needed, add request headers
    # headers = {
    #     'Authorization': 'Bearer YOUR_TOKEN',
    #     'X-API-Key': 'YOUR_API_KEY'
    # }

    print(f"📡 Attempting to read from cloud: {cloud_json_url}")
    print("💡 Tip: Please replace cloud_json_url with actual cloud JSON address")

    # Uncomment the following code to actually test
    # raw_data = load_apple_analysis_json(cloud_json_url, is_url=True)
    # if raw_data:
    #     _print_analysis_result(raw_data)
    # else:
    #     print("❌ Failed to read data from cloud (possibly invalid example URL)")


def _print_analysis_result(raw_data: Dict[str, Any]):
    """Helper function to print analysis results"""
    # Extract core metrics
    core_metrics = extract_core_metrics(raw_data)
    print("\n=== Core Metrics Extraction Result ===")
    print(json.dumps(core_metrics, ensure_ascii=False, indent=2))

    # Analyze news sentiment
    sentiment_analysis = analyze_news_sentiment(core_metrics["News Sentiment Distribution"])
    print("\n=== News Sentiment Analysis ===")
    print(sentiment_analysis)

    # Extract latest headlines
    recent_headlines = raw_data.get("news_overview", {}).get("recent_headlines", [])
    print("\n=== Latest Headline News (Top 5) ===")
    for idx, headline in enumerate(recent_headlines[:5], 1):
        print(f"{idx}. Title: {headline['headline']} | Time: {headline['time']} | Sentiment: {headline['sentiment']}")

if __name__ == "__main__":
    main()