"""
Test LLM Intent Recognizer
"""
import sys
import os

# Add project root directory to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import importlib
llm_intent_module = importlib.import_module('06_intent.llm_intent_recognizer')
LLMIntentRecognizer = llm_intent_module.LLMIntentRecognizer


def test_llm_intent_recognition():
    """Test LLM Intent Recognition functionality"""
    print("="*70)
    print("🧪 Testing LLM Intent Recognizer")
    print("="*70)
    
    # Initialize recognizer
    recognizer = LLMIntentRecognizer()
    
    # Test cases
    test_cases = [
        # ========== Scenario 1: Complete queries (should successfully recognize and extract stock tickers) ==========
        {
            "name": "Company Analysis - Complete Query",
            "query": "Analyze Apple Inc.",
            "expected_intent": "company_analysis",
            "should_have_ticker": True,
            "expected_ticker": "AAPL"
        },
        {
            "name": "Company Analysis - With Stock Ticker",
            "query": "How is AAPL's financial situation",
            "expected_intent": "company_analysis",
            "should_have_ticker": True,
            "expected_ticker": "AAPL"
        },
        {
            "name": "News Query - Complete Query",
            "query": "Latest news about Tesla",
            "expected_intent": "news_query",
            "should_have_ticker": True,
            "expected_ticker": "TSLA"
        },
        {
            "name": "Industry Analysis - Complete Query",
            "query": "How is the technology industry outlook",
            "expected_intent": "industry_analysis",
            "should_have_ticker": False
        },
        
        # ========== Scenario 2: Vague queries (should return clarification hints) ==========
        {
            "name": "Company Analysis - Vague Query",
            "query": "Analyze",
            "expected_intent": "company_analysis",
            "should_have_hint": True,
            "expected_hint_keywords": ["company name", "stock ticker"]
        },
        {
            "name": "News Query - Vague Query",
            "query": "Check news",
            "expected_intent": "news_query",
            "should_have_hint": True,
            "expected_hint_keywords": ["news", "company"]
        },
        {
            "name": "Industry Analysis - Vague Query",
            "query": "Analyze industry",
            "expected_intent": "industry_analysis",
            "should_have_hint": True,
            "expected_hint_keywords": ["industry"]
        },
        
        # ========== Scenario 3: Unknown intents (should return fallback message) ==========
        {
            "name": "Unknown Intent - Weather Query",
            "query": "How is the weather today",
            "expected_intent": "unknown",
            "should_have_fallback": True
        },
        {
            "name": "Unknown Intent - Greeting",
            "query": "Hello",
            "expected_intent": "unknown",
            "should_have_fallback": True
        },
        {
            "name": "Unknown Intent - Other Function",
            "query": "Help me write code",
            "expected_intent": "unknown",
            "should_have_fallback": True
        }
    ]
    
    # Execute tests
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        name = test_case["name"]
        query = test_case["query"]
        expected_intent = test_case["expected_intent"]
        
        print(f"\n[{i}/{len(test_cases)}] {name}")
        print(f"   Query: {query}")
        print(f"   Expected intent: {expected_intent}")
        
        try:
            result = recognizer.recognize(query)
            actual_intent = result.intent_type.value
            
            print(f"   Actual intent: {actual_intent}")
            print(f"   Confidence: {result.confidence:.2f}")
            print(f"   Entity count: {len(result.entities)}")
            
            # Display extracted entities
            if result.entities:
                for entity in result.entities:
                    print(f"      - {entity.entity_type}: {entity.value} (conf: {entity.confidence:.2f})")
            
            # Check if intent is correct
            intent_correct = (actual_intent == expected_intent)
            
            # Check if has stock ticker
            if test_case.get("should_have_ticker"):
                tickers = result.get_tickers()
                has_ticker = len(tickers) > 0
                ticker_correct = True
                
                if "expected_ticker" in test_case:
                    ticker_correct = test_case["expected_ticker"] in tickers
                
                if has_ticker and ticker_correct:
                    print(f"   ✅ Correctly extracted stock ticker: {', '.join(tickers)}")
                else:
                    print(f"   ❌ Failed to correctly extract stock ticker (expected: {test_case.get('expected_ticker')}, actual: {tickers})")
                    intent_correct = False
            
            # Check if has clarification hint
            if test_case.get("should_have_hint"):
                if result.fallback_message:
                    hint_keywords = test_case.get("expected_hint_keywords", [])
                    has_keywords = any(kw in result.fallback_message for kw in hint_keywords)
                    
                    if has_keywords:
                        print(f"   ✅ Contains clarification hint")
                        print(f"      Hint content: {result.fallback_message[:100]}...")
                    else:
                        print(f"   ⚠️  Has hint but missing keywords: {hint_keywords}")
                else:
                    print(f"   ❌ Missing clarification hint")
                    intent_correct = False
            
            # Check if has fallback message
            if test_case.get("should_have_fallback"):
                if result.fallback_message and len(result.fallback_message) > 50:
                    print(f"   ✅ Contains fallback message (length: {len(result.fallback_message)})")
                else:
                    print(f"   ❌ Missing fallback message or content too short")
                    intent_correct = False
            
            # Summarize test result
            if intent_correct:
                print(f"   ✅ Passed")
                passed += 1
            else:
                print(f"   ❌ Failed")
                failed += 1
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Summary
    print("\n" + "="*70)
    print(f"📊 Test Results: {passed} passed, {failed} failed, total {len(test_cases)}")
    print("="*70)
    
    return failed == 0


if __name__ == "__main__":
    success = test_llm_intent_recognition()
    sys.exit(0 if success else 1)