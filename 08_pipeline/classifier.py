"""
Four-Layer News Classifier
1. Event Pre-classification (Event Storyline)
2. Industry & Entity Classification (Regulatory & Industry Impact)
3. Sentiment Polarity Coarse Classification (Market & Sentiment Impact)
4. Business Impact Scope Classification (Business Impact)
"""
import sys
import os
import logging
import importlib
from typing import Dict, List, Tuple

# Add project root directory to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Use importlib to import config
_config_module = importlib.import_module('05_config.settings')
Config = _config_module.Config

logger = logging.getLogger(__name__)


class AdvancedNewsClassifier:
    """Four-layer classification system"""

    # ========== Layer 1: Event Pre-classification ==========
    EVENT_CATEGORIES = {
        "earnings_performance": {
            "keywords": [
                "earnings", "revenue", "profit", "quarterly", "beat", "miss",
                "net income", "eps", "guidance", "forecast", "outlook",
                "fiscal year", "annual report", "financial results"
            ],
            "description": "Earnings and performance related"
        },
        "policy_regulation": {
            "keywords": [
                "fed", "interest rate", "regulation", "policy", "government",
                "sec", "fda", "antitrust", "tariff", "trade policy",
                "monetary policy", "fiscal policy", "legislation", "compliance"
            ],
            "description": "Policy changes and regulatory actions"
        },
        "product_launch": {
            "keywords": [
                "launch", "release", "new product", "unveil", "announce",
                "innovation", "upgrade", "version", "feature", "technology",
                "patent", "breakthrough", "debut", "rollout"
            ],
            "description": "Product launches and technological breakthroughs"
        },
        "regulatory_lawsuit": {
            "keywords": [
                "lawsuit", "litigation", "investigation", "fine", "penalty",
                "settlement", "violation", "fraud", "scandal", "probe",
                "enforcement", "sanction", "legal action", "court"
            ],
            "description": "Regulatory lawsuits and compliance risks"
        },
        "merger_acquisition": {
            "keywords": [
                "merger", "acquisition", "acquire", "buyout", "deal",
                "takeover", "consolidation", "joint venture", "partnership",
                "stake", "divestiture", "spin-off", "integration"
            ],
            "description": "Mergers, acquisitions, and strategic partnerships"
        },
        "management_change": {
            "keywords": [
                "ceo", "cfo", "cto", "executive", "resign", "appoint",
                "leadership", "board", "director", "succession",
                "promotion", "departure", "hire", "replacement"
            ],
            "description": "Management changes and organizational restructuring"
        },
        "market_movement": {
            "keywords": [
                "surge", "plunge", "rally", "crash", "volatility",
                "stock price", "trading", "market cap", "valuation",
                "ipo", "listing", "delisting", "buyback", "dividend"
            ],
            "description": "Market movements and capital operations"
        },
        "supply_chain": {
            "keywords": [
                "supply chain", "supplier", "vendor", "logistics",
                "shortage", "disruption", "inventory", "procurement",
                "manufacturing", "production", "capacity", "bottleneck"
            ],
            "description": "Supply chain and production operations"
        }
    }

    # ========== Layer 2: Industry & Entity Classification ==========
    INDUSTRY_CATEGORIES = {
        "technology": {
            "keywords": [
                "software", "hardware", "semiconductor", "chip", "ai",
                "cloud computing", "cybersecurity", "internet", "social media",
                "e-commerce", "digital", "tech company", "silicon valley"
            ],
            "tickers": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "AMD", "INTC"],
            "description": "Technology sector"
        },
        "finance": {
            "keywords": [
                "bank", "insurance", "investment", "asset management",
                "brokerage", "fintech", "cryptocurrency", "blockchain",
                "lending", "credit", "mortgage", "wall street"
            ],
            "tickers": ["JPM", "BAC", "GS", "MS", "WFC", "C"],
            "description": "Financial sector"
        },
        "healthcare_pharma": {
            "keywords": [
                "pharmaceutical", "biotech", "drug", "clinical trial",
                "fda approval", "medical device", "healthcare", "hospital",
                "vaccine", "therapy", "treatment", "diagnosis"
            ],
            "tickers": ["JNJ", "PFE", "MRNA", "ABBV", "TMO"],
            "description": "Healthcare and pharmaceuticals"
        },
        "consumer_retail": {
            "keywords": [
                "retail", "consumer goods", "e-commerce", "shopping",
                "brand", "luxury", "apparel", "food beverage",
                "restaurant", "hospitality", "travel", "tourism"
            ],
            "tickers": ["AMZN", "WMT", "NKE", "SBUX", "MCD"],
            "description": "Consumer retail"
        },
        "energy_utilities": {
            "keywords": [
                "oil", "gas", "renewable energy", "solar", "wind",
                "electric utility", "power grid", "energy storage",
                "fossil fuel", "carbon", "emission"
            ],
            "tickers": ["XOM", "CVX", "NEE", "TSLA"],
            "description": "Energy and utilities"
        },
        "automotive_manufacturing": {
            "keywords": [
                "automotive", "electric vehicle", "ev", "autonomous driving",
                "manufacturing", "industrial", "aerospace", "defense",
                "machinery", "robotics", "automation"
            ],
            "tickers": ["TSLA", "F", "GM", "BA", "CAT"],
            "description": "Automotive and manufacturing"
        },
        "real_estate": {
            "keywords": [
                "real estate", "property", "housing", "commercial real estate",
                "reit", "construction", "development", "mortgage rate"
            ],
            "tickers": ["AMT", "PLD", "CCI"],
            "description": "Real estate"
        },
        "telecommunications": {
            "keywords": [
                "telecom", "5g", "network", "wireless", "broadband",
                "carrier", "spectrum", "infrastructure"
            ],
            "tickers": ["T", "VZ", "TMUS"],
            "description": "Telecommunications"
        }
    }

    # ========== Layer 3: Sentiment Polarity Coarse Classification ==========
    SENTIMENT_INDICATORS = {
        "positive": {
            "strong": [
                "surge", "soar", "skyrocket", "record high", "breakthrough",
                "beat expectations", "exceed", "outperform", "upgrade",
                "bullish", "optimistic", "strong growth", "profit jump"
            ],
            "moderate": [
                "rise", "gain", "increase", "growth", "improve",
                "positive", "favorable", "benefit", "opportunity",
                "expand", "accelerate", "momentum"
            ]
        },
        "negative": {
            "strong": [
                "plunge", "crash", "collapse", "plummet", "sharp decline",
                "miss expectations", "underperform", "downgrade",
                "bearish", "pessimistic", "loss", "bankruptcy"
            ],
            "moderate": [
                "fall", "drop", "decline", "decrease", "weaken",
                "negative", "unfavorable", "risk", "challenge",
                "slowdown", "contraction", "pressure"
            ]
        },
        "neutral": {
            "indicators": [
                "maintain", "stable", "unchanged", "flat", "steady",
                "announce", "report", "state", "confirm", "update"
            ]
        }
    }

    # ========== Layer 4: Business Impact Scope Classification ==========
    BUSINESS_IMPACT_CATEGORIES = {
        "revenue_impact": {
            "keywords": [
                "revenue", "sales", "top line", "income", "cash flow",
                "pricing", "demand", "order", "booking", "customer acquisition"
            ],
            "description": "Revenue impact (income side)"
        },
        "cost_impact": {
            "keywords": [
                "cost", "expense", "margin", "profitability", "overhead",
                "labor cost", "material cost", "operating expense",
                "inflation", "price increase", "efficiency"
            ],
            "description": "Cost impact (expenditure side)"
        },
        "supply_chain_impact": {
            "keywords": [
                "supply chain", "supplier", "vendor", "logistics",
                "shortage", "disruption", "lead time", "inventory",
                "procurement", "sourcing", "dependency"
            ],
            "description": "Supply chain impact"
        },
        "demand_impact": {
            "keywords": [
                "demand", "consumer sentiment", "market demand",
                "adoption", "preference", "trend", "behavior",
                "spending", "consumption", "buyer"
            ],
            "description": "Demand-side impact"
        },
        "channel_impact": {
            "keywords": [
                "distribution", "channel", "retail partner", "online sales",
                "marketplace", "platform", "delivery", "fulfillment",
                "wholesale", "direct-to-consumer"
            ],
            "description": "Channel impact"
        },
        "competitive_impact": {
            "keywords": [
                "competition", "market share", "competitor", "rival",
                "competitive advantage", "differentiation", "positioning",
                "barrier to entry", "moat"
            ],
            "description": "Competitive landscape impact"
        },
        "regulatory_impact": {
            "keywords": [
                "regulation", "compliance", "policy change", "legal",
                "restriction", "approval", "license", "permit",
                "government intervention", "lobbying"
            ],
            "description": "Regulatory policy impact"
        },
        "technology_impact": {
            "keywords": [
                "technology", "innovation", "digital transformation",
                "automation", "ai adoption", "modernization",
                "technical debt", "infrastructure upgrade"
            ],
            "description": "Technological change impact"
        }
    }

    @classmethod
    def classify_event(cls, headline: str, summary: str) -> Tuple[str, float]:
        """Layer 1: Event pre-classification"""
        text = f"{headline} {summary}".lower()

        scores = {}
        for event_type, config in cls.EVENT_CATEGORIES.items():
            keyword_matches = sum(1 for kw in config["keywords"] if kw in text)
            if keyword_matches > 0:
                confidence = keyword_matches / len(config["keywords"])
                scores[event_type] = min(confidence * 2, 1.0)

        if scores:
            best_event = max(scores, key=scores.get)
            return best_event, round(scores[best_event], 3)

        return "other", 0.0

    @classmethod
    def classify_industry(cls, headline: str, summary: str, ticker: str = "") -> Tuple[str, str, float]:
        """Layer 2: Industry & entity classification"""
        text = f"{ticker} {headline} {summary}".lower()
        ticker_upper = ticker.upper() if ticker else ""

        scores = {}
        matched_ticker = ticker_upper

        for industry, config in cls.INDUSTRY_CATEGORIES.items():
            keyword_score = sum(1 for kw in config["keywords"] if kw in text)

            ticker_match = 0
            if ticker_upper in config.get("tickers", []):
                ticker_match = 3

            total_score = keyword_score + ticker_match

            if total_score > 0:
                confidence = total_score / (len(config["keywords"]) + 3)
                scores[industry] = min(confidence, 1.0)

                if ticker_match > 0:
                    matched_ticker = ticker_upper

        if scores:
            best_industry = max(scores, key=scores.get)
            return best_industry, matched_ticker, round(scores[best_industry], 3)

        return "general", ticker_upper, 0.0

    @classmethod
    def classify_sentiment_coarse(cls, headline: str, summary: str) -> Tuple[str, str, float]:
        """Layer 3: Sentiment polarity coarse classification"""
        text = f"{headline} {summary}".lower()

        pos_strong = sum(1 for word in cls.SENTIMENT_INDICATORS["positive"]["strong"] if word in text)
        pos_moderate = sum(1 for word in cls.SENTIMENT_INDICATORS["positive"]["moderate"] if word in text)
        neg_strong = sum(1 for word in cls.SENTIMENT_INDICATORS["negative"]["strong"] if word in text)
        neg_moderate = sum(1 for word in cls.SENTIMENT_INDICATORS["negative"]["moderate"] if word in text)
        neutral_count = sum(1 for word in cls.SENTIMENT_INDICATORS["neutral"]["indicators"] if word in text)

        pos_score = pos_strong * 2 + pos_moderate
        neg_score = neg_strong * 2 + neg_moderate

        total = pos_score + neg_score + neutral_count

        if total == 0:
            return "neutral", "none", 0.5

        if pos_score > neg_score:
            polarity = "positive"
            intensity = "strong" if pos_strong > 0 else "moderate"
            confidence = pos_score / total
        elif neg_score > pos_score:
            polarity = "negative"
            intensity = "strong" if neg_strong > 0 else "moderate"
            confidence = neg_score / total
        else:
            polarity = "neutral"
            intensity = "none"
            confidence = neutral_count / total if neutral_count > 0 else 0.5

        return polarity, intensity, round(min(confidence, 1.0), 3)

    @classmethod
    def classify_business_impact(cls, headline: str, summary: str) -> List[Tuple[str, float]]:
        """Layer 4: Business impact scope classification (supports multi-label)"""
        text = f"{headline} {summary}".lower()

        impacts = []
        for impact_type, config in cls.BUSINESS_IMPACT_CATEGORIES.items():
            keyword_matches = sum(1 for kw in config["keywords"] if kw in text)
            if keyword_matches > 0:
                confidence = keyword_matches / len(config["keywords"])
                impacts.append((impact_type, round(min(confidence * 2, 1.0), 3)))

        impacts.sort(key=lambda x: x[1], reverse=True)
        return impacts

    @classmethod
    def full_classification(cls, news_item: Dict) -> Dict:
        """Execute complete four-layer classification"""
        headline = news_item.get("headline", "")
        summary = news_item.get("summary", "") or ""
        ticker = news_item.get("symbol", "") or news_item.get("related", "") or news_item.get("ticker", "")

        event_type, event_confidence = cls.classify_event(headline, summary)
        industry, main_entity, industry_confidence = cls.classify_industry(headline, summary, ticker)
        sentiment_polarity, sentiment_intensity, sentiment_confidence = cls.classify_sentiment_coarse(headline, summary)
        business_impacts = cls.classify_business_impact(headline, summary)

        enriched_news = news_item.copy()
        enriched_news.update({
            "event_type": event_type,
            "event_confidence": event_confidence,
            "event_description": cls.EVENT_CATEGORIES.get(event_type, {}).get("description", ""),

            "industry": industry,
            "main_entity": main_entity,
            "industry_confidence": industry_confidence,
            "industry_description": cls.INDUSTRY_CATEGORIES.get(industry, {}).get("description", ""),

            "sentiment_polarity": sentiment_polarity,
            "sentiment_intensity": sentiment_intensity,
            "sentiment_confidence": sentiment_confidence,

            "business_impacts": [imp[0] for imp in business_impacts[:3]],
            "business_impact_scores": {imp[0]: imp[1] for imp in business_impacts[:3]},
            "primary_impact": business_impacts[0][0] if business_impacts else "unknown",

            "tags": [
                event_type,
                industry,
                sentiment_polarity,
                sentiment_intensity
            ] + [imp[0] for imp in business_impacts[:2]]
        })

        return enriched_news

    @classmethod
    def get_classification_summary(cls, enriched_news: Dict) -> str:
        """Generate human-readable classification summary"""
        summary_parts = [
            f"📋 Event Type: {enriched_news.get('event_type')} ({enriched_news.get('event_description')})",
            f"🏭 Industry: {enriched_news.get('industry')} ({enriched_news.get('industry_description')})",
            f"📊 Sentiment: {enriched_news.get('sentiment_polarity')} ({enriched_news.get('sentiment_intensity')})",
            f"💼 Primary Impact: {enriched_news.get('primary_impact')}"
        ]

        if enriched_news.get('business_impacts'):
            impacts_str = ", ".join(enriched_news['business_impacts'])
            summary_parts.append(f"🎯 Impact Scope: {impacts_str}")

        return "\n".join(summary_parts)