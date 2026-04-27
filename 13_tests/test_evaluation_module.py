"""
Test Evaluation Module Functionality
"""
import sys
import importlib
from pathlib import Path

# Add project root directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_evaluation_module():
    """Test evaluation module"""
    print("=" * 70)
    print("🧪 Testing Evaluation Module")
    print("=" * 70)

    # Import evaluation module
    eval_module = importlib.import_module('09_retrieve.evaluation')
    AnalysisEvaluator = eval_module.AnalysisEvaluator

    # Create evaluator
    evaluator = AnalysisEvaluator()
    print("\n✅ Evaluator created successfully")

    # Create a mock analysis result
    mock_analysis = {
        "company": "AAPL",
        "analysis_date": "2024-04-27",
        "analysis_period": "Last 7 days",
        "total_news_analyzed": 50,
        "storyline": {
            "summary": "Apple Inc. announced new AI strategy this week, partnering with OpenAI and showcasing multiple AI features at WWDC. This move triggered strong market reaction, with stock price rising 5%.",
            "key_events": [
                {
                    "date": "2024-04-25",
                    "event": "Apple announces partnership with OpenAI",
                    "impact": "Stock price rose 5%",
                    "source_urls": ["https://example.com/news1"]
                },
                {
                    "date": "2024-04-26",
                    "event": "WWDC showcases AI features",
                    "impact": "Enthusiastic market response",
                    "source_urls": ["https://example.com/news2", "https://example.com/news3"]
                }
            ],
            "timeline": "April 25 partnership announcement → April 26 WWDC showcase → Positive market reaction",
            "key_players": ["Apple", "OpenAI"],
            "cause_effect": "AI cooperation announcement led to increased market confidence",
            "source_urls": ["https://example.com/news1", "https://example.com/news2"]
        },
        "financial_impact": {
            "score": 8,
            "analysis": "Strong financial position with robust revenue growth [Source: https://example.com/news1]",
            "key_factors": ["Revenue growth", "Margin improvement"],
            "source_urls": ["https://example.com/news1", "https://example.com/news2"]
        },
        "operational_impact": {
            "score": 7,
            "analysis": "Operational efficiency continues to improve [Source: https://example.com/news3]",
            "key_factors": ["Supply chain optimization"],
            "source_urls": ["https://example.com/news3"]
        },
        "market_impact": {
            "score": 9,
            "analysis": "Market share expansion with optimistic investor sentiment [Source: https://example.com/news1]",
            "key_factors": ["Market share", "Investor confidence"],
            "source_urls": ["https://example.com/news1", "https://example.com/news2"]
        },
        "regulatory_impact": {
            "score": -2,
            "analysis": "Facing certain regulatory pressures [Source: https://example.com/news4]",
            "key_factors": ["Antitrust investigation"],
            "source_urls": ["https://example.com/news4"]
        },
        "strategic_impact": {
            "score": 8,
            "analysis": "Clear AI strategic layout [Source: https://example.com/news2]",
            "key_factors": ["AI strategy", "Partnerships"],
            "source_urls": ["https://example.com/news2", "https://example.com/news3"]
        },
        "future_outlook": {
            "score": 7,
            "short_term_impact": "Stock price may continue to rise in the short term",
            "medium_term_impact": "Medium term requires observing AI product commercialization progress",
            "long_term_impact": "Long term, AI will become core competitiveness",
            "risk_analysis": "Main risks include regulatory pressure and intensifying competition",
            "stakeholder_impact": {
                "investors": "Positive for investors",
                "employees": "Employees need to learn new skills",
                "customers": "User experience will improve"
            },
            "key_factors": ["AI commercialization", "Regulatory policies"],
            "source_urls": ["https://example.com/news1", "https://example.com/news2"]
        },
        "overall_assessment": {
            "total_score": 37,
            "recommendation": "Buy",
            "confidence": 0.85,
            "summary": "Based on Storyline event analysis and Future Outlook impact prediction, Apple Inc. shows excellent overall performance",
            "key_insights": ["Clear AI strategy", "Financially healthy", "Solid market position"],
            "source_urls": ["https://example.com/news1", "https://example.com/news2", "https://example.com/news3"]
        }
    }

    print("\n🔍 Starting evaluation of mock analysis results...")
    report = evaluator.evaluate_analysis(mock_analysis)

    print(f"\n📊 Evaluation Results:")
    print(f"   Total Score: {report['overall_score']:.2f}")
    print(f"   Grade: {report['grade']}")
    print(f"   Passed: {'✅' if report['passed'] else '❌'}")

    print(f"\n📋 Dimension Scores:")
    for dim_name, dim_data in report['dimensions'].items():
        print(f"   {dim_name}: {dim_data['score']:.2f}/100")

    if report['issues']:
        print(f"\n⚠️  Issues Found ({len(report['issues'])} issues):")
        for issue in report['issues'][:5]:  # Only show first 5
            print(f"   - {issue}")

    if report['recommendations']:
        print(f"\n💡 Improvement Suggestions ({len(report['recommendations'])} suggestions):")
        for rec in report['recommendations'][:5]:  # Only show first 5
            print(f"   - {rec}")

    # Test saving report
    output_file = Path(__file__).parent / "test_evaluation_report.json"
    full_report = evaluator.generate_evaluation_report(mock_analysis, str(output_file))

    if output_file.exists():
        print(f"\n💾 Evaluation report saved to: {output_file}")
        print(f"   File size: {output_file.stat().st_size} bytes")

    print("\n✅ Evaluation module test complete!")
    return report


if __name__ == "__main__":
    test_evaluation_module()