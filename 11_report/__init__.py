"""
报告生成模块
提供公司分析报告生success能（支持云端和本地 LLM）
"""
from .report_generator import (
    analyze_company_and_generate_report,
    generate_enhanced_report,
    save_prompt_to_file,
    example_company_analysis
)

__all__ = [
    # 统一版本 - 支持云端和本地
    'analyze_company_and_generate_report',
    'generate_enhanced_report',
    'save_prompt_to_file',
    'example_company_analysis',
]