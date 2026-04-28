"""
Test script for OpenAI Compatible API (Aliyun Token Plan)
Tests the cloud LLM client using OpenAI SDK compatible mode
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_openai_compatible_chat():
    """Test chat using OpenAI compatible API"""
    print("\n" + "="*70)
    print("TEST 1: OpenAI Compatible Mode - Basic Chat")
    print("="*70)
    
    try:
        from openai import OpenAI
        
        # Get configuration from environment
        base_url = os.getenv("OPENAI_COMPATIBLE_BASE_URL")
        api_key = os.getenv("OPENAI_COMPATIBLE_API_KEY")
        model = "qwen3.6-plus"
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
        
        if not base_url or not api_key:
            print("❌ OPENAI_COMPATIBLE_BASE_URL or OPENAI_COMPATIBLE_API_KEY not configured")
            print(f"   Base URL: {base_url}")
            print(f"   API Key: {'Set' if api_key else 'Not Set'}")
            return False
        
        print(f"\n📡 Base URL: {base_url}")
        print(f"🔑 API Key: {api_key[:20]}...")
        print(f"🤖 Model: {model}")
        print(f"🌡️  Temperature: {temperature}")
        
        # Initialize OpenAI client with custom base URL
        client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        
        # Test simple conversation
        print("\n📤 Sending message...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "你好，请简单介绍一下你自己"}
            ],
            temperature=temperature,
            max_tokens=200
        )
        
        content = response.choices[0].message.content
        
        print(f"\n✅ Response received ({len(content)} characters):")
        print("-" * 70)
        print(content)
        print("-" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_openai_compatible_models():
    """Test different models available in OpenAI compatible mode"""
    print("\n" + "="*70)
    print("TEST 2: OpenAI Compatible Mode - Multiple Models")
    print("="*70)

    try:
        from openai import OpenAI

        base_url = os.getenv("OPENAI_COMPATIBLE_BASE_URL")
        api_key = os.getenv("OPENAI_COMPATIBLE_API_KEY")

        if not base_url or not api_key:
            print("❌ API configuration not found")
            return False

        # Models to test
        models_to_test = ["qwen3.6-plus"]

        results = {}

        for model_name in models_to_test:
            print(f"\n🧪 Testing model: {model_name}")
            try:
                client = OpenAI(
                    base_url=base_url,
                    api_key=api_key
                )

                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": "Say hello in one sentence"}],
                    max_tokens=30
                )

                content = response.choices[0].message.content
                results[model_name] = "✅ Success"
                print(f"   ✅ {model_name}: {content[:60]}...")

            except Exception as e:
                results[model_name] = f"❌ Failed: {str(e)}"
                print(f"   ❌ {model_name}: {e}")

        print("\n" + "="*70)
        print("Model Test Summary:")
        print("="*70)
        for model, status in results.items():
            print(f"  {model}: {status}")

        return all("Success" in status for status in results.values())

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_financial_analysis():
    """Test financial analysis using OpenAI compatible API"""
    print("\n" + "="*70)
    print("TEST 3: OpenAI Compatible Mode - Financial Analysis")
    print("="*70)
    
    try:
        from openai import OpenAI
        
        base_url = os.getenv("OPENAI_COMPATIBLE_BASE_URL")
        api_key = os.getenv("OPENAI_COMPATIBLE_API_KEY")
        model = "qwen3.6-plus"
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
        
        if not base_url or not api_key:
            print("❌ API configuration not found")
            return False
        
        print(f"🌡️  Temperature: {temperature}")
        
        client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        
        # Financial analysis prompt
        test_prompt = """
        请对以下新闻进行影响分析，并以JSON格式输出：
        
        新闻标题：苹果公司发布最新季度财报，营收同比增长15%
        新闻内容：苹果公司今日发布了2026年第一季度财报，显示公司营收达到1200亿美元，同比增长15%。其中iPhone业务营收增长12%，服务业务增长20%。CEO库克表示，公司对未来发展前景保持乐观。
        
        请输出包含以下字段的JSON：
        {
            "market_sentiment": "正面/负面/中性",
            "impact_level": "高/中/低",
            "short_term_impact": "短期影响描述",
            "long_term_impact": "长期影响描述",
            "investment_suggestion": "投资建议"
        }
        """
        
        print("\n📤 Generating financial analysis...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional financial analyst. Output only JSON format, no extra text."
                },
                {"role": "user", "content": test_prompt}
            ],
            temperature=temperature,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        
        print(f"\n✅ Analysis completed ({len(content)} characters):")
        print("-" * 70)
        print(content)
        print("-" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_unified_llm_client_openai_mode():
    """Test UnifiedLLMClient with OpenAI compatible mode"""
    print("\n" + "="*70)
    print("TEST 4: UnifiedLLMClient Integration Test")
    print("="*70)
    
    try:
        from importlib import import_module
        llm_client_module = import_module('09_retrieve.llm_client')
        UnifiedLLMClient = llm_client_module.UnifiedLLMClient
        
        print("\n✅ Testing UnifiedLLMClient with OpenAI Compatible Mode")
        
        # Test with OpenAI compatible implementation
        client = UnifiedLLMClient(
            model="qwen3.6-plus",
            use_cloud=True
        )
        
        messages = [{"role": "user", "content": "Hello"}]
        response = client.chat(messages, max_tokens=20)
        
        print(f"\n✅ UnifiedLLMClient (OpenAI Compatible) works: {response[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("OpenAI Compatible API Test Suite")
    print("="*70)
    print(f"Testing Aliyun Token Plan with OpenAI compatible mode")
    print(f"Base URL configured: {'Yes' if os.getenv('OPENAI_COMPATIBLE_BASE_URL') else 'No'}")
    print(f"API Key configured: {'Yes' if os.getenv('OPENAI_COMPATIBLE_API_KEY') else 'No'}")

    tests = [
        ("Basic Chat (OpenAI Compatible)", test_openai_compatible_chat),
        ("Multiple Models", test_openai_compatible_models),
        ("Financial Analysis", test_financial_analysis),
        ("UnifiedLLMClient Integration", test_unified_llm_client_openai_mode),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ {test_name} encountered unexpected error: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}")

    print("="*70)
    print(f"Total: {passed}/{total} tests passed")
    print("="*70)

    if passed == total:
        print("\n🎉 All tests passed! Your OpenAI Compatible API is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
