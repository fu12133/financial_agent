"""
Industry Analysis Function Test Script
Test complete industry analysis workflow
"""
import sys
import importlib
from pathlib import Path
from datetime import datetime

# Add project root directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_intent_recognition():
    """Test 1: Intent recognition"""
    print("\n" + "=" * 70)
    print("🧪 Test 1: Industry Analysis Intent Recognition")
    print("=" * 70)
    
    intent_module = importlib.import_module('06_intent.intent_recognizer')
    IntentRecognizer = intent_module.IntentRecognizer
    
    recognizer = IntentRecognizer()
    
    test_queries = [
        "Analyze the technology industry",
        "How is the finance industry doing recently",
        "What are the development trends in healthcare industry",
        "I want to understand consumer retail industry",
        "Investment prospects of energy industry"
    ]
    
    for query in test_queries:
        result = recognizer.recognize(query)
        print(f"\nQuery: {query}")
        print(f"  Intent: {result.intent_type.value}")
        print(f"  Confidence: {result.confidence:.2f}")
        industries = result.get_industries()
        if industries:
            print(f"  Recognized industry: {industries}")


def test_rag_service():
    """Test 2: RAG Service industry analysis"""
    print("\n" + "=" * 70)
    print("🧪 Test 2: RAG Service Industry Analysis")
    print("=" * 70)
    
    rag_module = importlib.import_module('09_retrieve.rag_service')
    RAGService = rag_module.RAGService
    
    print("\nInitializing RAG Service...")
    rag = RAGService(device='cuda')
    
    print("Initialize LLM (cloud qwen-plus)...")
    rag.initialize_llm(model='qwen-plus', use_cloud=True)
    
    print("\nStarting technology industry analysis...")
    result = rag.analyze_industry_comprehensive(
        industry='technology',
        industry_name='Technology Industry',
        days=7
    )
    
    if 'error' in result:
        print(f"❌ Analysis failed: {result['error']}")
        return False
    
    print(f"\n✅ Analysis successful!")
    print(f"   Industry: {result['industry_name']}")
    print(f"   Analysis period: {result['analysis_period_days']} days")
    print(f"   News count: {result['total_news']}")
    print(f"   Companies covered: {len(result.get('companies_covered', []))}")
    
    # Display analysis result summary
    analysis = result.get('llm_analysis', {})
    if isinstance(analysis, dict) and 'overall_assessment' in analysis:
        oa = analysis['overall_assessment']
        print(f"\n📊 Overall Assessment:")
        print(f"   Total score: {oa.get('total_score', 'N/A')}")
        print(f"   Recommendation: {oa.get('recommendation', 'N/A')}")
        print(f"   Confidence: {oa.get('confidence', 'N/A')}")
        if oa.get('key_insights'):
            print(f"   Key insights:")
            for insight in oa['key_insights'][:3]:
                print(f"     - {insight}")
    
    return True


def test_report_generation():
    """Test 3: Report generation"""
    print("\n" + "=" * 70)
    print("🧪 Test 3: Industry Report Generation")
    print("=" * 70)
    
    report_module = importlib.import_module('11_report.report_generator')
    generate_industry_report = report_module.generate_industry_report
    
    print("\nStarting finance industry report generation...")
    result = generate_industry_report(
        industry='finance',
        industry_name='Finance Industry',
        days=7,
        use_cloud=True,
        model='qwen-plus'
    )
    
    if 'error' in result:
        print(f"❌ Report generation failed: {result['error']}")
        return False
    
    print(f"\n✅ Report generated successfully!")
    print(f"   Industry: {result['industry_name']}")
    print(f"   News count: {result['total_news']}")
    
    return True


def test_agent_integration():
    """Test 4: Agent integration"""
    print("\n" + "=" * 70)
    print("🧪 Test 4: Agent Integration Test")
    print("=" * 70)
    
    agent_module = importlib.import_module('03_agent.agent_core')
    FinancialAgent = agent_module.FinancialAgent
    
    print("\nCreating Agent...")
    agent = FinancialAgent(user_id='test_user', verbose=True)
    
    print("\nTesting industry analysis conversation...")
    response = agent.chat("Analyze the latest developments in the technology industry")
    
    if response.get('success'):
        print(f"\n✅ Agent response successful!")
        print(f"   Intent: {response.get('intent', {}).get('intent_type')}")
        resp_data = response.get('response', {})
        print(f"   Message: {resp_data.get('message', '')[:200]}")
    else:
        print(f"❌ Agent response failed: {response.get('error')}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("=" * 70)
    print("🚀 Industry Analysis Function Complete Test")
    print("=" * 70)
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Intent Recognition", test_intent_recognition),
        ("RAG Service", test_rag_service),
        ("Report Generation", test_report_generation),
        ("Agent Integration", test_agent_integration)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success if success is not None else True))
        except Exception as e:
            print(f"\n❌ {name} test exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Print test summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    
    for name, success in results:
        status = "✅ Passed" if success else "❌ Failed"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} tests failed, please check logs")


if __name__ == "__main__":
    main()