"""
Enhanced Quality Evaluator with LLM Assistance
Provides intelligent quality evaluation combining rule-based and LLM-based assessment
"""
import json
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class EnhancedAnalysisEvaluator:
    """
    Enhanced Analysis Quality Evaluator with LLM Assistance
    
    Combines rule-based evaluation with LLM-powered intelligent assessment
    for more accurate and insightful quality evaluation.
    """

    def __init__(self, llm_client=None):
        """
        Initialize enhanced evaluator
        
        Args:
            llm_client: Optional LLM client for intelligent evaluation
                       If None, falls back to rule-based evaluation only
        """
        self.llm_client = llm_client
        self.use_llm = llm_client is not None
        
        # Load YAML prompt template
        try:
            from .prompt_loader import PromptLoader
            self.prompt_loader = PromptLoader()
            self.template = self.prompt_loader.load_template('quality_evaluation')
            logger.info("✅ Quality evaluation prompt template loaded from YAML")
        except Exception as e:
            logger.warning(f"️ Failed to load YAML template: {e}")
            self.template = None
        
        # Rule-based evaluation weights
        self.rule_weights = {
            'completeness': 0.15,
            'traceability': 0.20,
            'consistency': 0.15,
            'depth': 0.15,
            'timeliness': 0.10,
            'balance': 0.10,
            'llm_quality': 0.15  # LLM assessment weight
        }
        
        logger.info(f"🔍 Enhanced Analysis Evaluator initialized")
        logger.info(f"   LLM assistance: {'Enabled' if self.use_llm else 'Disabled'}")

    def evaluate_with_llm(self, analysis_result: Dict) -> Dict[str, Any]:
        """
        Evaluate analysis quality with LLM assistance
        
        Args:
            analysis_result: Complete analysis result
            
        Returns:
            Enhanced evaluation report with both rule-based and LLM-based scores
        """
        logger.info("🔍 Starting enhanced quality evaluation with LLM assistance...")
        
        # Step 1: Get rule-based evaluation
        from .evaluation import AnalysisEvaluator
        rule_evaluator = AnalysisEvaluator()
        rule_report = rule_evaluator.evaluate_analysis(analysis_result)
        
        # Step 2: Get LLM-based evaluation (if available)
        llm_report = None
        if self.use_llm:
            llm_report = self._get_llm_evaluation(analysis_result)
        else:
            logger.info("⚠️ LLM client not provided, using rule-based evaluation only")
            llm_report = {
                'overall_score': 70,
                'reasoning': 'LLM evaluation skipped (no LLM client)',
                'strengths': [],
                'weaknesses': [],
                'recommendations': rule_report.get('recommendations', [])
            }
        
        # Step 3: Combine evaluations
        combined_report = self._combine_evaluations(rule_report, llm_report)
        
        logger.info(f"✅ Enhanced evaluation completed")
        logger.info(f"   Rule-based score: {rule_report['overall_score']:.1f}/100")
        logger.info(f"   LLM-based score: {llm_report['overall_score']:.1f}/100")
        logger.info(f"   Combined score: {combined_report['overall_score']:.1f}/100")
        
        return combined_report

    def _get_llm_evaluation(self, analysis_result: Dict) -> Dict:
        """
        Use LLM to evaluate analysis quality
        
        Args:
            analysis_result: Complete analysis result
            
        Returns:
            LLM-based evaluation report
        """
        try:
            logger.info("🤖 Calling LLM for quality evaluation...")
            
            # Create evaluation prompt using YAML template
            evaluation_prompt = self._create_llm_evaluation_prompt(analysis_result)
            
            if not evaluation_prompt:
                logger.error("❌ Failed to create evaluation prompt")
                return self._get_fallback_llm_evaluation()
            
            # Call LLM
            response = self.llm_client.generate_impact_analysis(
                evaluation_prompt,
                temperature=0.1,
                max_tokens=2048
            )
            
            # Parse LLM response
            if 'error' in response:
                logger.error(f" LLM evaluation failed: {response['error']}")
                return self._get_fallback_llm_evaluation()
            
            # Try to parse JSON response
            try:
                llm_evaluation = json.loads(response['raw_response'])
                logger.info(f"✅ LLM evaluation successful")
                return llm_evaluation
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse LLM response as JSON: {e}")
                logger.error(f"   Raw response: {response['raw_response'][:500]}")
                return self._get_fallback_llm_evaluation()
                
        except Exception as e:
            logger.error(f" LLM evaluation error: {e}")
            return self._get_fallback_llm_evaluation()

    def _create_llm_evaluation_prompt(self, analysis_result: Dict) -> Optional[str]:
        """
        Create prompt for LLM quality evaluation using YAML template
        
        Args:
            analysis_result: Complete analysis result
            
        Returns:
            Formatted prompt string or None if template unavailable
        """
        # Determine analysis type
        is_industry = 'industry_trend' in analysis_result
        analysis_type = "Industry" if is_industry else "Company"
        
        # Convert analysis result to JSON string
        analysis_content = json.dumps(analysis_result, indent=2, ensure_ascii=False)
        
        # Use YAML template if available
        if self.template:
            try:
                # Render template with variables
                prompt = self.template.render(
                    analysis_type=analysis_type,
                    analysis_content=analysis_content
                )
                logger.info("✅ Prompt created from YAML template")
                return prompt
            except Exception as e:
                logger.error(f"❌ Failed to render YAML template: {e}")
                # Fallback to manual template
                return self._create_manual_prompt(analysis_type, analysis_content)
        else:
            # Fallback to manual template
            logger.warning("⚠️ Using manual prompt template (YAML not available)")
            return self._create_manual_prompt(analysis_type, analysis_content)

    def _create_manual_prompt(self, analysis_type: str, analysis_content: str) -> str:
        """Create manual prompt as fallback"""
        return f"""
You are a professional financial analysis quality evaluator. Your task is to evaluate the quality of a financial analysis report.

## Analysis Type
{analysis_type} Analysis

## Evaluation Dimensions (Score 0-100 for each)

1. **Analytical Depth** (0-100)
   - Does the analysis provide deep insights?
   - Is there sufficient detail in each dimension?
   - Are the key insights meaningful and actionable?

2. **Logical Consistency** (0-100)
   - Are the scores logically consistent with the analysis?
   - Does the summary match the detailed analysis?
   - Is the overall assessment reasonable?

3. **Evidence Quality** (0-100)
   - Are the source URLs relevant and credible?
   - Is there sufficient evidence to support conclusions?
   - Are citations properly integrated?

4. **Objectivity & Balance** (0-100)
   - Is the analysis balanced (not overly positive or negative)?
   - Are risks and opportunities both addressed?
   - Is there objective reasoning?

5. **Actionability** (0-100)
   - Can investors use this analysis for decision-making?
   - Are the recommendations clear and practical?
   - Is the timeline realistic?

## Analysis Content to Evaluate

{analysis_content}

## Output Format (JSON ONLY, no extra text)

{{
  "overall_score": 85,
  "dimensions": {{
    "analytical_depth": {{
      "score": 85,
      "reasoning": "Detailed analysis with good insights..."
    }},
    "logical_consistency": {{
      "score": 90,
      "reasoning": "Scores are consistent with analysis..."
    }},
    "evidence_quality": {{
      "score": 80,
      "reasoning": "Good source coverage..."
    }},
    "objectivity_balance": {{
      "score": 88,
      "reasoning": "Well-balanced analysis..."
    }},
    "actionability": {{
      "score": 82,
      "reasoning": "Clear recommendations..."
    }}
  }},
  "strengths": [
    "Comprehensive storyline coverage",
    "Good use of multiple sources"
  ],
  "weaknesses": [
    "Some dimensions could be more detailed",
    "Risk analysis is brief"
  ],
  "recommendations": [
    "Add more quantitative data support",
    "Expand risk analysis section"
  ],
  "confidence_justification": "High confidence based on comprehensive evidence and logical analysis"
}}

IMPORTANT: Output ONLY the JSON object. No markdown, no code blocks, no explanations.
"""

    def _get_fallback_llm_evaluation(self) -> Dict:
        """Return fallback evaluation when LLM fails"""
        return {
            'overall_score': 70,
            'dimensions': {
                'analytical_depth': {
                    'score': 70,
                    'reasoning': 'LLM evaluation unavailable, using default'
                },
                'logical_consistency': {
                    'score': 70,
                    'reasoning': 'LLM evaluation unavailable, using default'
                },
                'evidence_quality': {
                    'score': 70,
                    'reasoning': 'LLM evaluation unavailable, using default'
                },
                'objectivity_balance': {
                    'score': 70,
                    'reasoning': 'LLM evaluation unavailable, using default'
                },
                'actionability': {
                    'score': 70,
                    'reasoning': 'LLM evaluation unavailable, using default'
                }
            },
            'strengths': [],
            'weaknesses': [],
            'recommendations': [],
            'confidence_justification': 'Default evaluation (LLM unavailable)'
        }

    def _combine_evaluations(self, rule_report: Dict, llm_report: Dict) -> Dict:
        """
        Combine rule-based and LLM-based evaluations
        
        Args:
            rule_report: Rule-based evaluation report
            llm_report: LLM-based evaluation report
            
        Returns:
            Combined evaluation report
        """
        # Extract rule-based dimension scores
        rule_score = rule_report['overall_score']
        
        # Extract LLM-based score
        llm_score = llm_report['overall_score']
        
        # Calculate weighted combined score
        rule_weight = 0.60  # 60% rule-based
        llm_weight = 0.40   # 40% LLM-based
        
        combined_score = (
            rule_score * rule_weight +
            llm_score * llm_weight
        )
        
        # Determine grade
        grade = self._score_to_grade(combined_score)
        
        # Combine issues and recommendations
        all_issues = rule_report.get('issues', []).copy()
        all_recommendations = rule_report.get('recommendations', []).copy()
        
        # Add LLM-specific recommendations
        if llm_report.get('weaknesses'):
            for weakness in llm_report['weaknesses']:
                all_recommendations.append(f"[LLM] {weakness}")
        
        if llm_report.get('recommendations'):
            all_recommendations.extend(llm_report['recommendations'])
        
        # Create combined report
        combined_report = {
            'overall_score': round(combined_score, 2),
            'grade': grade,
            'rule_based_score': round(rule_score, 2),
            'llm_based_score': round(llm_score, 2),
            'dimensions': {
                **rule_report.get('dimensions', {}),
                'llm_evaluation': llm_report.get('dimensions', {})
            },
            'strengths': llm_report.get('strengths', []),
            'issues': all_issues,
            'recommendations': all_recommendations,
            'llm_reasoning': llm_report.get('confidence_justification', ''),
            'analysis_type': rule_report.get('analysis_type', 'unknown'),
            'evaluation_method': 'hybrid'  # Indicates combined evaluation
        }
        
        return combined_report

    def _score_to_grade(self, score: float) -> str:
        """Convert score to grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'


def create_enhanced_evaluator(llm_client=None) -> EnhancedAnalysisEvaluator:
    """
    Create enhanced analysis evaluator
    
    Args:
        llm_client: Optional LLM client for intelligent evaluation
        
    Returns:
        EnhancedAnalysisEvaluator instance
    """
    return EnhancedAnalysisEvaluator(llm_client=llm_client)