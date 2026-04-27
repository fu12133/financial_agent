"""
Company Analysis Report Generation Module - Unified Version (supports cloud and local)
Input company name, automatically generate complete analysis report and enhanced report
"""
import sys
import os
import json
import importlib
from datetime import datetime
from typing import Dict, Optional

# Add project root directory to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Use importlib to import modules
_retrieve_module = importlib.import_module('09_retrieve.rag_service')
RAGService = _retrieve_module.RAGService

_json_convertor_module = importlib.import_module('09_retrieve.json_convertor')
extract_core_metrics = _json_convertor_module.extract_core_metrics
analyze_news_sentiment = _json_convertor_module.analyze_news_sentiment
extract_full_llm_analysis = _json_convertor_module.extract_full_llm_analysis


def save_prompt_to_file(prompt: str, filename: str = "impact_analysis_prompt.txt"):
    """
    Save prompt to file

    :param prompt: Prompt content
    :param filename: Filename
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(prompt)
        print(f"💾 Prompt saved to: {filename}")
        print(f"   File size: {os.path.getsize(filename)} bytes")
        print(f"   Character count: {len(prompt)}")
        return True
    except Exception as e:
        print(f"❌ Failed to save prompt: {e}")
        return False


def generate_enhanced_report(raw_data: dict, output_file: str = "enhanced_analysis_report.json"):
    """
    Generate enhanced analysis report using json_convertor

    :param raw_data: Raw analysis data
    :param output_file: Output filename
    """
    print("\n" + "=" * 70)
    print("📝 Generating Enhanced Analysis Report")
    print("=" * 70)

    # 1. Extract core metrics
    print("\n🔍 Extracting core metrics...")
    core_metrics = extract_core_metrics(raw_data)

    if not core_metrics:
        print("❌ Unable to extract core metrics")
        return None

    print("✅ Core metrics extraction successful")

    # 2. Analyze news sentiment
    print("\n📊 Analyzing news sentiment...")
    sentiment_conclusion = analyze_news_sentiment(core_metrics.get("News Sentiment Distribution", {}))
    print(f"   {sentiment_conclusion}")

    # 3. 🆕 Directly parse raw_response to JSON
    print("\n🤖 Parsing LLM raw response...")
    full_llm_analysis = extract_full_llm_analysis(raw_data)

    if full_llm_analysis:
        print("✅ LLM response parsing complete")
    else:
        print("⚠️  LLM response parsing failed")

    # 4. Build enhanced report
    enhanced_report = {
        "report_metadata": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "report_type": "enhanced_company_analysis",
            "version": "1.0"
        },
        "core_metrics": core_metrics,
        "sentiment_analysis": {
            "conclusion": sentiment_conclusion,
            "distribution": core_metrics.get("News Sentiment Distribution", {})
        },
        "basic_info": core_metrics.get("Basic Information", {}),
        "news_distribution": core_metrics.get("News Type Distribution", {}),
        "llm_scores": core_metrics.get("LLM Analysis Scores", {}),
        "recent_headlines": raw_data.get("news_overview", {}).get("recent_headlines", [])[:10],
        "full_llm_analysis": full_llm_analysis  # Directly parsed JSON
    }

    # 5. Save enhanced report
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_report, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Enhanced report saved to: {output_file}")
        print(f"   File size: {os.path.getsize(output_file)} bytes")
        return enhanced_report
    except Exception as e:
        print(f"❌ Failed to save enhanced report: {e}")
        return None


def analyze_company_and_generate_report(
        company_name: str,
        ticker: str = None,
        days: int = None,
        use_cloud: bool = None,
        model: str = None,
        device: str = None,
        use_quantization: bool = None,
        output_dir: str = None
) -> Dict:
    """
    Analyze company and generate complete report (supports cloud and local)

    :param company_name: Company name (required), e.g., "Apple Inc."
    :param ticker: Stock ticker (optional), e.g., "AAPL". If not provided, will use uppercase prefix of company name
    :param days: Analysis days (optional), default read from .env
    :param use_cloud: Whether to use cloud model (None=auto detect, True=cloud, False=local)
    :param model: Model name (optional), cloud default "qwen-plus", local default read HF_MODEL_NAME from .env
    :param device: Computing device ('cuda' or 'cpu', only for local mode)
    :param use_quantization: Whether to use 4bit quantization (only for local mode, default True)
    :param output_dir: Output root directory (default 11_report/output/)
    :return: Dictionary containing analysis results
    """
    # If ticker not provided, generate from company name
    if not ticker:
        ticker = company_name.upper().replace(" ", "_")[:10]
        print(f"⚠️  Stock ticker not provided, using: {ticker}")

    # Set default output directory to 11_report/output/
    if output_dir is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(current_dir, "output")
    
    # Ensure using absolute path
    output_dir = os.path.abspath(output_dir)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 Output root directory (absolute path): {output_dir}")
    
    # Create company-specific folder
    safe_ticker = ticker.replace("/", "_").replace("\\", "_")
    safe_company_name = company_name.replace("/", "_").replace("\\", "_").replace(" ", "_")
    company_folder = os.path.join(output_dir, f"{safe_ticker}_{safe_company_name}")
    
    os.makedirs(company_folder, exist_ok=True)
    print(f"📁 Report will be saved to: {company_folder}")

    mode_suffix = "cloud" if use_cloud else ("local" if use_cloud is False else "auto")
    raw_output_file = os.path.join(company_folder, f"company_analysis_{mode_suffix}.json")
    enhanced_output_file = os.path.join(company_folder, f"enhanced_report_{mode_suffix}.json")
    prompt_file = os.path.join(company_folder, f"impact_analysis_prompt_{mode_suffix}.txt")

    mode_text = "Cloud" if use_cloud else ("Local" if use_cloud is False else "Auto")
    print("=" * 70)
    print(f"🚀 Starting analysis for company: {company_name} ({ticker}) [{mode_text} mode]")
    print("=" * 70)

    # Create RAG service
    rag = RAGService(device=device or 'cuda')

    # Initialize LLM
    try:
        if model:
            model_name = model
        elif use_cloud:
            model_name = os.getenv("QWEN_CLOUD_MODEL", "qwen-plus")
        elif use_cloud is False:
            model_name = os.getenv("HF_MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")
        else:
            model_name = os.getenv("DEFAULT_LLM_MODEL", "qwen-plus")

        print(f"\n📥 Initializing LLM...")
        print(f"   Mode: {'Cloud' if use_cloud else ('Local' if use_cloud is False else 'Auto')}")
        print(f"   Model: {model_name}")

        if not use_cloud and use_cloud is not True:
            device_to_use = device or ('cuda' if __import__('torch').cuda.is_available() else 'cpu')
            print(f"   Device: {device_to_use}")
            print(f"   Quantization: {'4bit' if use_quantization is None or use_quantization else 'FP16'}")

        rag.initialize_llm(model=model_name, use_cloud=use_cloud)
        print(f"✅ LLM ready")

    except Exception as e:
        print(f"❌ LLM initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

    # Execute analysis
    print(f"\n🔍 Starting analysis of {company_name} ({ticker})...")
    result = rag.analyze_company(
        ticker=ticker,
        company_name=company_name,
        days=days
    )

    # View results
    print("\n" + "=" * 70)
    print("📊 Analysis Results")
    print("=" * 70)

    if 'error' in result:
        print(f"❌ Analysis failed: {result['error']}")
        return result

    print(f"\n📈 Company Overview:")
    print(f"   Stock Ticker: {result['ticker']}")
    print(f"   Company Name: {result['company_name']}")
    print(f"   Number of news analyzed: {result['total_news']}")

    # Display news overview
    overview = result.get('news_overview', {})
    if overview:
        print(f"\n📰 News Overview:")
        print(f"   Event Types: {overview.get('event_types', {})}")
        print(f"   Sentiment Distribution: {overview.get('sentiments', {})}")

    # Display LLM analysis results
    analysis = result.get('llm_analysis', {})
    
    print(f"\n🔍 Debug Information:")
    print(f"   result type: {type(result)}")
    print(f"   llm_analysis type: {type(analysis)}")
    print(f"   llm_analysis is empty: {not analysis}")
    if isinstance(analysis, dict):
        print(f"   llm_analysis keys: {list(analysis.keys())}")
        print(f"   has error: {'error' in analysis}")
    
    if 'error' not in analysis and isinstance(analysis, dict) and analysis:
        if 'financial_impact' in analysis:
            fi = analysis['financial_impact']
            print(f"\n💰 Financial Impact (Score: {fi.get('score', 'N/A')})")
            print(f"   {fi.get('analysis', '')[:300]}")

        if 'market_impact' in analysis:
            mi = analysis['market_impact']
            print(f"\n📈 Market Impact (Score: {mi.get('score', 'N/A')})")
            print(f"   {mi.get('analysis', '')[:300]}")

        if 'overall_assessment' in analysis:
            oa = analysis['overall_assessment']
            print(f"\n🎯 Overall Assessment")
            print(f"   Total Score: {oa.get('total_score', 'N/A')}")
            print(f"   Recommendation: {oa.get('recommendation', 'N/A')}")
            print(f"   Confidence: {oa.get('confidence', 'N/A')}")
            print(f"   Summary: {oa.get('summary', '')[:300]}")

        # Save complete results
        try:
            print(f"\n💾 Attempting to save raw data to: {raw_output_file}")
            print(f"   Absolute path: {os.path.abspath(raw_output_file)}")
            
            with open(raw_output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            if os.path.exists(raw_output_file):
                print(f"✅ Raw data saved: {raw_output_file}")
                print(f"   File size: {os.path.getsize(raw_output_file)} bytes")
            else:
                print(f"❌ File save failed, file does not exist: {raw_output_file}")
        except Exception as e:
            print(f"❌ Failed to save raw data: {e}")
            import traceback
            traceback.print_exc()

        # Generate enhanced report
        try:
            print(f"\n📝 Attempting to generate enhanced report to: {enhanced_output_file}")
            enhanced_report = generate_enhanced_report(
                raw_data=result,
                output_file=enhanced_output_file
            )

            if enhanced_report:
                print(f"\n✅ Analysis complete!")
                print(f"   Raw data: {raw_output_file}")
                print(f"   Enhanced report: {enhanced_output_file}")
                print(f"   Prompt file: {prompt_file}")
                
                # Build return result
                result['report_path'] = enhanced_output_file
                result['raw_data_path'] = raw_output_file
                result['prompt_file'] = prompt_file
                result['success'] = True
                
                # Extract summary
                if 'overall_assessment' in analysis:
                    result['summary'] = analysis['overall_assessment'].get('summary', '')
            else:
                print(f"\n⚠️  Enhanced report generation failed")
                result['report_path'] = raw_output_file
                result['raw_data_path'] = raw_output_file
                result['prompt_file'] = prompt_file
                result['success'] = True
                if 'overall_assessment' in analysis:
                    result['summary'] = analysis['overall_assessment'].get('summary', '')
        except Exception as e:
            print(f"❌ Failed to generate enhanced report: {e}")
            import traceback
            traceback.print_exc()
            result['success'] = False
    else:
        print(f"\n❌ LLM analysis failed or empty")
        if isinstance(analysis, dict):
            print(f"   error: {analysis.get('error', 'Unknown')}")
        else:
            print(f"   analysis type: {type(analysis)}")
            print(f"   analysis content: {str(analysis)[:200]}")
        result['success'] = False

    return result


def generate_industry_report(
        industry: str,
        industry_name: str = None,
        days: int = None,
        use_cloud: bool = None,
        model: str = None,
        device: str = None,
        use_quantization: bool = None,
        output_dir: str = None
) -> Dict:
    """
    Analyze industry and generate complete report (supports cloud and local)

    :param industry: Industry code (required), e.g., "technology"
    :param industry_name: Industry name (optional), e.g., "Tech Industry". If not provided, will use industry code
    :param days: Analysis days (optional), default read from .env
    :param use_cloud: Whether to use cloud model (None=auto detect, True=cloud, False=local)
    :param model: Model name (optional), cloud default "qwen-plus", local default read HF_MODEL_NAME from .env
    :param device: Computing device ('cuda' or 'cpu', only for local mode)
    :param use_quantization: Whether to use 4bit quantization (only for local mode, default True)
    :param output_dir: Output root directory (default 11_report/output/)
    :return: Dictionary containing analysis results
    """
    # If industry_name not provided, use industry code
    if not industry_name:
        industry_name = industry
        print(f"⚠️  Industry name not provided, using: {industry_name}")

    # Set default output directory to 11_report/output/
    if output_dir is None:
        # Get current file directory (11_report/)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(current_dir, "output")
    
    # Ensure using absolute path
    output_dir = os.path.abspath(output_dir)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 Output root directory (absolute path): {output_dir}")
    
    # Create industry-specific folder: 11_report/output/INDUSTRY_IndustryName/
    safe_industry = industry.replace("/", "_").replace("\\", "_")
    safe_industry_name = industry_name.replace("/", "_").replace("\\", "_").replace(" ", "_")
    industry_folder = os.path.join(output_dir, f"{safe_industry}_{safe_industry_name}")
    
    # Create output directory structure
    os.makedirs(industry_folder, exist_ok=True)
    print(f"📁 Report will be saved to: {industry_folder}")

    # Generate output filenames (inside industry folder)
    mode_suffix = "cloud" if use_cloud else ("local" if use_cloud is False else "auto")
    raw_output_file = os.path.join(industry_folder, f"industry_analysis_{mode_suffix}.json")
    enhanced_output_file = os.path.join(industry_folder, f"enhanced_report_{mode_suffix}.json")
    prompt_file = os.path.join(industry_folder, f"impact_analysis_prompt_{mode_suffix}.txt")

    mode_text = "Cloud" if use_cloud else ("Local" if use_cloud is False else "Auto")
    print("=" * 70)
    print(f"🚀 Starting analysis for industry: {industry_name} ({industry}) [{mode_text} mode]")
    print("=" * 70)

    # Create RAG service
    rag = RAGService(device=device or 'cuda')

    # Initialize LLM
    try:
        if model:
            model_name = model
        elif use_cloud:
            model_name = os.getenv("QWEN_CLOUD_MODEL", "qwen-plus")
        elif use_cloud is False:
            model_name = os.getenv("HF_MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")
        else:
            model_name = os.getenv("DEFAULT_LLM_MODEL", "qwen-plus")

        print(f"\n📥 Initializing LLM...")
        print(f"   Mode: {'Cloud' if use_cloud else ('Local' if use_cloud is False else 'Auto')}")
        print(f"   Model: {model_name}")

        if not use_cloud and use_cloud is not True:
            device_to_use = device or ('cuda' if __import__('torch').cuda.is_available() else 'cpu')
            print(f"   Device: {device_to_use}")
            print(f"   Quantization: {'4bit' if use_quantization is None or use_quantization else 'FP16'}")

        rag.initialize_llm(model=model_name, use_cloud=use_cloud)
        print(f"✅ LLM ready")

    except Exception as e:
        print(f"❌ LLM initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

    # Execute analysis
    print(f"\n🔍 Starting analysis of {industry_name} ({industry})...")
    result = rag.analyze_industry(
        industry=industry,
        industry_name=industry_name,
        days=days
    )

    # View results
    print("\n" + "=" * 70)
    print("📊 Analysis Results")
    print("=" * 70)

    if 'error' in result:
        print(f"❌ Analysis failed: {result['error']}")
        return result

    print(f"\n📈 Industry Overview:")
    print(f"   Industry Code: {result['industry']}")
    print(f"   Industry Name: {result['industry_name']}")
    print(f"   Number of news analyzed: {result['total_news']}")
    print(f"   Companies covered: {', '.join(result.get('companies_covered', [])[:10])}")

    # Display news overview
    overview = result.get('news_overview', {})
    if overview:
        print(f"\n📰 News Overview:")
        print(f"   Event Types: {overview.get('event_types', {})}")
        print(f"   Sentiment Distribution: {overview.get('sentiments', {})}")

    # Display LLM analysis results
    analysis = result.get('llm_analysis', {})
    if 'error' not in analysis and isinstance(analysis, dict):
        if 'industry_trend' in analysis:
            it = analysis['industry_trend']
            print(f"\n📊 Industry Trend (Score: {it.get('score', 'N/A')})")
            print(f"   {it.get('analysis', '')[:300]}")
            if it.get('source_urls'):
                print(f"   🔗 Sources ({len(it['source_urls'])} items): {it['source_urls'][:2]}")

        if 'competitive_landscape' in analysis:
            cl = analysis['competitive_landscape']
            print(f"\n🏆 Competitive Landscape (Score: {cl.get('score', 'N/A')})")
            print(f"   {cl.get('analysis', '')[:300]}")

        if 'overall_assessment' in analysis:
            oa = analysis['overall_assessment']
            print(f"\n🎯 Overall Assessment")
            print(f"   Total Score: {oa.get('total_score', 'N/A')}")
            print(f"   Recommendation: {oa.get('recommendation', 'N/A')}")
            print(f"   Confidence: {oa.get('confidence', 'N/A')}")
            print(f"   Summary: {oa.get('summary', '')[:300]}")
            if oa.get('key_insights'):
                print(f"   Key Insights:")
                for insight in oa['key_insights'][:3]:
                    print(f"     - {insight}")

        # Save complete results
        with open(raw_output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Complete results saved to: {raw_output_file}")

        # Generate enhanced report (if needed)
        enhanced_output_file = os.path.join(industry_folder, f"enhanced_report_{mode_suffix}.json")
        enhanced_report = generate_enhanced_report(
            raw_data=result,
            output_file=enhanced_output_file
        )

        print(f"\n✅ Analysis complete!")
        print(f"   Raw data: {raw_output_file}")
        if enhanced_report:
            print(f"   Enhanced report: {enhanced_output_file}")
        print(f"   Prompt file: {prompt_file}")
        
        # Build return result
        result['report_path'] = enhanced_output_file if enhanced_report else raw_output_file
        result['raw_data_path'] = raw_output_file
        result['prompt_file'] = prompt_file
        result['success'] = True
        
        # Extract summary
        if 'llm_analysis' in result and 'overall_assessment' in result['llm_analysis']:
            result['summary'] = result['llm_analysis']['overall_assessment'].get('summary', '')
    else:
        print(f"\n❌ LLM analysis failed")
        if isinstance(analysis, dict):
            print(f"   error: {analysis.get('error', 'Unknown')}")
        result['success'] = False

    return result


# Backward compatibility example function
def example_company_analysis():
    """Example: Comprehensive analysis of all news for Milvus"""
    # Analyze Apple using cloud model - report saved in 11_report/output/AAPL_Apple_Inc/
    analyze_company_and_generate_report(
        company_name="Apple Inc.",
        ticker="AAPL",
        use_cloud=True,
        model="qwen-plus"
        # output_dir defaults to 11_report/output/
    )


if __name__ == "__main__":
    # Example usage
    print("Usage example:")
    print("=" * 70)
    print()
    print("# Analyze Apple (Cloud)")
    print("# Report saved in: 11_report/output/AAPL_Apple_Inc/")
    print("analyze_company_and_generate_report(")
    print("    company_name='Apple Inc.',")
    print("    ticker='AAPL',")
    print("    use_cloud=True,")
    print("    model='qwen-plus'")
    print(")")
    print()
    print("# Analyze Microsoft (Local)")
    print("# Report saved in: 11_report/output/MSFT_Microsoft_Corporation/")
    print("analyze_company_and_generate_report(")
    print("    company_name='Microsoft Corporation',")
    print("    ticker='MSFT',")
    print("    days=14,")  # Analyze recent 14 days
    print("    use_cloud=False,")
    print("    device='cuda',")
    print("    use_quantization=True")
    print(")")
    print()
    print("# Auto detect (based on model name)")
    print("# Report saved in: 11_report/output/TSLA_Tesla/")
    print("analyze_company_and_generate_report(")
    print("    company_name='Tesla',")
    print("    ticker='TSLA',")
    print("    model='qwen-plus'")  # Automatically use cloud
    print(")")
    print()
    
    # Run example
    example_company_analysis()
