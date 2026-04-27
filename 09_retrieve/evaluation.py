"""
Agent Performance Evaluation Module
Provides multi-dimensional analysis quality evaluation without external tools
"""
import json
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AnalysisEvaluator:
    """
    Analysis Quality Evaluator

    Evaluation Dimensions:
    1. Completeness - All required fields present
    2. Traceability - URL citation coverage
    3. Consistency - Score logical consistency
    4. Depth - Analysis detail level
    5. Timeliness - Data recency
    6. Balance - Positive/negative balance
    """

    def __init__(self):
        self.evaluation_criteria = {
            'completeness': {
                'weight': 0.20,
                'description': 'All required fields present'
            },
            'traceability': {
                'weight': 0.25,
                'description': 'URL citation coverage and quality'
            },
            'consistency': {
                'weight': 0.20,
                'description': 'Score logical consistency'
            },
            'depth': {
                'weight': 0.15,
                'description': 'Analysis detail and insightfulness'
            },
            'timeliness': {
                'weight': 0.10,
                'description': 'Data recency'
            },
            'balance': {
                'weight': 0.10,
                'description': 'Positive/negative balance'
            }
        }

    def evaluate_analysis(self, analysis_result: Dict) -> Dict[str, Any]:
        """
        Evaluate analysis quality

        Args:
            analysis_result: Analysis result (supports company and industry analysis)

        Returns:
            Report with dimension scores and overall score
        """
        # Determine if industry or company analysis
        is_industry_analysis = 'industry_trend' in analysis_result or 'industry' in analysis_result

        if is_industry_analysis:
            return self._evaluate_industry_analysis(analysis_result)
        else:
            return self._evaluate_company_analysis(analysis_result)

    def _evaluate_industry_analysis(self, result: Dict) -> Dict[str, Any]:
        """Evaluate industry analysis quality"""
        logger.info("🔍 Evaluating industry analysis quality...")

        # Six dimension evaluation
        completeness_score = self._check_completeness(result, is_industry=True)
        traceability_score = self._check_traceability(result, is_industry=True)
        consistency_score = self._check_consistency(result, is_industry=True)
        depth_score = self._check_industry_depth(result)
        timeliness_score = self._check_timeliness(result)
        balance_score = self._check_industry_balance(result)

        # Calculate weighted total score
        overall_score = sum([
            completeness_score['score'] * 0.20,
            traceability_score['score'] * 0.25,
            consistency_score['score'] * 0.20,
            depth_score['score'] * 0.15,
            timeliness_score['score'] * 0.10,
            balance_score['score'] * 0.10
        ])

        overall_grade = self._score_to_grade(overall_score)

        # Collect all dimension issues
        all_issues = []
        for dim_name, dim_eval in [
            ("Completeness", completeness_score),
            ("Traceability", traceability_score),
            ("Consistency", consistency_score),
            ("Depth", depth_score),
            ("Timeliness", timeliness_score),
            ("Balance", balance_score)
        ]:
            if 'issues' in dim_eval and dim_eval['issues']:
                for issue in dim_eval['issues']:
                    all_issues.append(f"[{dim_name}] {issue}")

        # Generate improvement recommendations
        recommendations = []
        for dim_name, dim_eval in [
            ("Completeness", completeness_score),
            ("Traceability", traceability_score),
            ("Consistency", consistency_score),
            ("Depth", depth_score),
            ("Timeliness", timeliness_score),
            ("Balance", balance_score)
        ]:
            if dim_eval['score'] < 80:
                recommendations.append(f"{dim_name} score is low ({dim_eval['score']:.1f}/100), needs improvement")

            # Add dimension-specific recommendations
            if 'recommendations' in dim_eval and dim_eval['recommendations']:
                for rec in dim_eval['recommendations']:
                    recommendations.append(f"[{dim_name}] {rec}")

        evaluation_report = {
            'overall_score': round(overall_score, 2),
            'grade': overall_grade,
            'dimensions': {
                'completeness': completeness_score,
                'traceability': traceability_score,
                'consistency': consistency_score,
                'depth': depth_score,
                'timeliness': timeliness_score,
                'balance': balance_score
            },
            'issues': all_issues,
            'recommendations': recommendations,
            'analysis_type': 'industry'
        }

        logger.info(f"📊 Industry Analysis Evaluation Results:")
        logger.info(f"   Overall Score: {overall_score:.2f}/100")
        logger.info(f"   Grade: {overall_grade}")
        logger.info(f"   Issues Found: {len(all_issues)}")
        logger.info(f"   Recommendations: {len(recommendations)}")
        logger.info(f"   Completeness: {completeness_score['score']:.1f}/100 - {completeness_score.get('reasoning', '')}")
        logger.info(f"   Traceability: {traceability_score['score']:.1f}/100 - {traceability_score.get('reasoning', '')}")
        logger.info(f"   Consistency: {consistency_score['score']:.1f}/100 - {consistency_score.get('reasoning', '')}")
        logger.info(f"   Depth: {depth_score['score']:.1f}/100 - {depth_score.get('reasoning', '')}")
        logger.info(f"   Timeliness: {timeliness_score['score']:.1f}/100 - {timeliness_score.get('reasoning', '')}")
        logger.info(f"   Balance: {balance_score['score']:.1f}/100 - {balance_score.get('reasoning', '')}")

        return evaluation_report

    def _evaluate_company_analysis(self, result: Dict) -> Dict[str, Any]:
        """Evaluate company analysis quality"""
        logger.info("🔍 Evaluating company analysis quality...")

        # Six dimension evaluation
        completeness_score = self._check_completeness(result)
        traceability_score = self._check_traceability(result, is_industry=False)
        consistency_score = self._check_consistency(result)
        depth_score = self._check_depth(result)
        timeliness_score = self._check_timeliness(result)
        balance_score = self._check_balance(result)

        # Calculate weighted total score
        overall_score = sum([
            completeness_score['score'] * 0.20,
            traceability_score['score'] * 0.25,
            consistency_score['score'] * 0.20,
            depth_score['score'] * 0.15,
            timeliness_score['score'] * 0.10,
            balance_score['score'] * 0.10
        ])

        overall_grade = self._score_to_grade(overall_score)

        # Collect all dimension issues
        all_issues = []
        for dim_name, dim_eval in [
            ("Completeness", completeness_score),
            ("Traceability", traceability_score),
            ("Consistency", consistency_score),
            ("Depth", depth_score),
            ("Timeliness", timeliness_score),
            ("Balance", balance_score)
        ]:
            if 'issues' in dim_eval and dim_eval['issues']:
                for issue in dim_eval['issues']:
                    all_issues.append(f"[{dim_name}] {issue}")

        # Generate improvement recommendations
        recommendations = []
        for dim_name, dim_eval in [
            ("Completeness", completeness_score),
            ("Traceability", traceability_score),
            ("Consistency", consistency_score),
            ("Depth", depth_score),
            ("Timeliness", timeliness_score),
            ("Balance", balance_score)
        ]:
            if dim_eval['score'] < 80:
                recommendations.append(f"{dim_name} score is low ({dim_eval['score']:.1f}/100), needs improvement")

            # Add dimension-specific recommendations
            if 'recommendations' in dim_eval and dim_eval['recommendations']:
                for rec in dim_eval['recommendations']:
                    recommendations.append(f"[{dim_name}] {rec}")

        evaluation_report = {
            'overall_score': round(overall_score, 2),
            'grade': overall_grade,
            'dimensions': {
                'completeness': completeness_score,
                'traceability': traceability_score,
                'consistency': consistency_score,
                'depth': depth_score,
                'timeliness': timeliness_score,
                'balance': balance_score
            },
            'issues': all_issues,
            'recommendations': recommendations,
            'analysis_type': 'company'
        }

        logger.info(f"📊 Company Analysis Evaluation Results:")
        logger.info(f"   Overall Score: {overall_score:.2f}/100")
        logger.info(f"   Grade: {overall_grade}")
        logger.info(f"   Issues Found: {len(all_issues)}")
        logger.info(f"   Recommendations: {len(recommendations)}")
        logger.info(f"   Completeness: {completeness_score['score']:.1f}/100 - {completeness_score.get('reasoning', '')}")
        logger.info(f"   Traceability: {traceability_score['score']:.1f}/100 - {traceability_score.get('reasoning', '')}")
        logger.info(f"   Consistency: {consistency_score['score']:.1f}/100 - {consistency_score.get('reasoning', '')}")
        logger.info(f"   Depth: {depth_score['score']:.1f}/100 - {depth_score.get('reasoning', '')}")
        logger.info(f"   Timeliness: {timeliness_score['score']:.1f}/100 - {timeliness_score.get('reasoning', '')}")
        logger.info(f"   Balance: {balance_score['score']:.1f}/100 - {balance_score.get('reasoning', '')}")

        return evaluation_report

    def _check_completeness(self, result: Dict, is_industry: bool = False) -> Dict:
        """Check completeness - all required fields present"""
        issues = []
        recommendations = []
        score = 100
        reasoning_parts = []

        # Check basic fields
        basic_fields = ['analysis_date', 'analysis_period', 'total_news_analyzed']
        missing_basic = [f for f in basic_fields if f not in result]
        if missing_basic:
            issues.append(f"Missing basic fields: {', '.join(missing_basic)}")
            score -= len(missing_basic) * 5
            reasoning_parts.append(f"Missing {len(missing_basic)} basic field(s)")

        # Check storyline
        if 'storyline' not in result:
            issues.append("Missing required field: storyline")
            score -= 15
            reasoning_parts.append("Storyline section is missing")
        else:
            storyline = result['storyline']
            storyline_fields = ['summary', 'key_events', 'timeline', 'source_urls']
            missing_storyline = [f for f in storyline_fields if f not in storyline]
            if missing_storyline:
                issues.append(f"Storyline missing fields: {', '.join(missing_storyline)}")
                score -= len(missing_storyline) * 5
                reasoning_parts.append(f"Storyline missing {len(missing_storyline)} field(s)")
            else:
                reasoning_parts.append("Storyline complete")

        # Check dimension completeness - distinguish industry vs company analysis
        if is_industry:
            dimension_fields = [
                'industry_trend', 'competitive_landscape', 'policy_regulatory',
                'supply_chain_ecosystem', 'investment_attractiveness', 'future_outlook'
            ]
        else:
            dimension_fields = [
                'financial_impact', 'operational_impact', 'market_impact',
                'regulatory_impact', 'strategic_impact', 'future_outlook'
            ]

        present_dimensions = 0
        missing_dimensions = []
        dimensions_with_missing_fields = []

        for dim in dimension_fields:
            if dim in result:
                present_dimensions += 1
                dim_data = result[dim]

                # Check required fields for each dimension
                required_dim_fields = ['score', 'analysis', 'source_urls']
                missing = [f for f in required_dim_fields if f not in dim_data]
                if missing:
                    issues.append(f"{dim} missing fields: {', '.join(missing)}")
                    score -= len(missing) * 3
                    dimensions_with_missing_fields.append(f"{dim}({len(missing)} fields)")
            else:
                missing_dimensions.append(dim)
                issues.append(f"Missing analysis dimension: {dim}")
                score -= 10

        if missing_dimensions:
            reasoning_parts.append(f"Missing {len(missing_dimensions)} dimension(s): {', '.join(missing_dimensions[:3])}")

        if dimensions_with_missing_fields:
            reasoning_parts.append(f"{len(dimensions_with_missing_fields)} dimension(s) with incomplete fields")

        # Check overall_assessment
        if 'overall_assessment' in result:
            oa = result['overall_assessment']
            oa_fields = ['total_score', 'recommendation', 'confidence', 'summary', 'key_insights']
            missing_oa = [f for f in oa_fields if f not in oa]
            if missing_oa:
                issues.append(f"Overall assessment missing fields: {', '.join(missing_oa)}")
                score -= len(missing_oa) * 3
                reasoning_parts.append(f"Overall assessment missing {len(missing_oa)} field(s)")
        else:
            issues.append("Missing overall_assessment section")
            score -= 15
            reasoning_parts.append("Overall assessment section is missing")

        if present_dimensions < 4:
            recommendations.append("Recommend including at least 4+ analysis dimensions")

        if score < 0:
            score = 0

        # Generate reasoning summary
        if not reasoning_parts:
            reasoning = "All required fields and dimensions are present"
        else:
            reasoning = "; ".join(reasoning_parts)

        return {
            'score': score,
            'max_score': 100,
            'present_dimensions': present_dimensions,
            'expected_dimensions': len(dimension_fields),
            'issues': issues,
            'recommendations': recommendations,
            'reasoning': reasoning
        }

    def _check_traceability(self, result: Dict, is_industry: bool = False) -> Dict:
        """Check traceability - URL citation coverage"""
        issues = []
        recommendations = []
        score = 100
        reasoning_parts = []

        total_dimensions = 0
        dimensions_with_urls = 0
        total_urls = 0
        dimensions_without_urls = []
        dimensions_with_few_urls = []

        # Check source_urls for each dimension - distinguish industry vs company analysis
        if is_industry:
            dimension_fields = [
                'storyline', 'industry_trend', 'competitive_landscape',
                'policy_regulatory', 'supply_chain_ecosystem', 'investment_attractiveness',
                'future_outlook', 'overall_assessment'
            ]
        else:
            dimension_fields = [
                'storyline', 'financial_impact', 'operational_impact',
                'market_impact', 'regulatory_impact', 'strategic_impact',
                'future_outlook', 'overall_assessment'
            ]

        for dim in dimension_fields:
            if dim in result:
                total_dimensions += 1
                dim_data = result[dim]

                if isinstance(dim_data, dict) and 'source_urls' in dim_data:
                    urls = dim_data['source_urls']
                    if isinstance(urls, list) and len(urls) > 0:
                        dimensions_with_urls += 1
                        total_urls += len(urls)

                        # Check if URL count is sufficient
                        if len(urls) < 2:
                            dimensions_with_few_urls.append(dim)
                            issues.append(f"{dim} has only {len(urls)} source(s), recommend at least 2-3")
                            score -= 5
                    else:
                        dimensions_without_urls.append(dim)
                        score -= 10
                else:
                    dimensions_without_urls.append(dim)
                    score -= 10

        # Calculate URL coverage rate
        if total_dimensions > 0:
            coverage_rate = dimensions_with_urls / total_dimensions * 100
        else:
            coverage_rate = 0
            issues.append("No analysis dimensions found")

        if dimensions_without_urls:
            reasoning_parts.append(f"{len(dimensions_without_urls)} dimension(s) missing URLs")

        if dimensions_with_few_urls:
            reasoning_parts.append(f"{len(dimensions_with_few_urls)} dimension(s) with insufficient URLs (<2)")

        if coverage_rate < 80:
            recommendations.append(f"URL coverage is only {coverage_rate:.1f}%, target should be >80%")
            reasoning_parts.append(f"Low URL coverage ({coverage_rate:.1f}%)")
        else:
            reasoning_parts.append(f"Good URL coverage ({coverage_rate:.1f}%)")

        if total_urls < 10:
            recommendations.append(f"Total URL count ({total_urls}) is low, recommend at least 15-20")
            reasoning_parts.append(f"Low total URL count ({total_urls})")
        else:
            reasoning_parts.append(f"Adequate total URLs ({total_urls})")

        # Check if analysis text has URL citation annotations
        url_citation_count = 0
        for dim in dimension_fields:
            if dim in result and isinstance(result[dim], dict):
                analysis_text = result[dim].get('analysis', '')
                if '[参考来源:' in analysis_text or '[Source:' in analysis_text:
                    url_citation_count += 1

        if url_citation_count < total_dimensions * 0.5:
            issues.append("Some dimensions lack [Source: URL] citations in analysis text")
            score -= 10
            reasoning_parts.append(f"Insufficient in-text citations ({url_citation_count}/{total_dimensions})")
        else:
            reasoning_parts.append(f"Good in-text citation coverage ({url_citation_count}/{total_dimensions})")

        if score < 0:
            score = 0

        # Generate reasoning summary
        reasoning = "; ".join(reasoning_parts)

        return {
            'score': score,
            'max_score': 100,
            'url_coverage_rate': coverage_rate,
            'dimensions_with_urls': dimensions_with_urls,
            'total_dimensions': total_dimensions,
            'total_urls': total_urls,
            'avg_urls_per_dimension': round(total_urls / max(total_dimensions, 1), 2),
            'url_citations_in_text': url_citation_count,
            'issues': issues,
            'recommendations': recommendations,
            'reasoning': reasoning
        }

    def _check_consistency(self, result: Dict, is_industry: bool = False) -> Dict:
        """Check score logical consistency"""
        issues = []
        recommendations = []
        score = 100
        reasoning_parts = []

        # 1. Check dimension score ranges (-10 to 10) - distinguish industry vs company analysis
        if is_industry:
            dimension_fields = [
                'industry_trend', 'competitive_landscape', 'policy_regulatory',
                'supply_chain_ecosystem', 'investment_attractiveness', 'future_outlook'
            ]
        else:
            dimension_fields = [
                'financial_impact', 'operational_impact', 'market_impact',
                'regulatory_impact', 'strategic_impact', 'future_outlook'
            ]

        dimension_scores = []
        invalid_scores = []
        out_of_range_scores = []

        for dim in dimension_fields:
            if dim in result and isinstance(result[dim], dict):
                dim_score = result[dim].get('score')
                if dim_score is not None:
                    if not isinstance(dim_score, (int, float)):
                        invalid_scores.append(dim)
                        issues.append(f"{dim}.score is not numeric")
                        score -= 10
                    elif dim_score < -10 or dim_score > 10:
                        out_of_range_scores.append(f"{dim}({dim_score})")
                        issues.append(f"{dim}.score ({dim_score}) out of range [-10, 10]")
                        score -= 10
                    else:
                        dimension_scores.append(dim_score)

        if invalid_scores:
            reasoning_parts.append(f"{len(invalid_scores)} dimension(s) with non-numeric scores")

        if out_of_range_scores:
            reasoning_parts.append(f"{len(out_of_range_scores)} dimension(s) with out-of-range scores")

        # 2. Check if total_score is reasonable
        total_score_valid = True
        if 'overall_assessment' in result:
            oa = result['overall_assessment']
            total_score = oa.get('total_score')

            if total_score is not None:
                # Calculate sum of dimension scores
                if dimension_scores:
                    expected_total = sum(dimension_scores)
                    # Allow 15% error or at least 10 points tolerance
                    tolerance = max(abs(expected_total) * 0.15, 10)

                    if abs(total_score - expected_total) > tolerance:
                        issues.append(
                            f"total_score ({total_score}) differs significantly from dimension sum ({expected_total}) "
                            f"(difference >{tolerance:.1f})"
                        )
                        score -= 15
                        total_score_valid = False
                        reasoning_parts.append(f"Total score inconsistency (expected {expected_total}, got {total_score})")
                    else:
                        reasoning_parts.append(f"Total score consistent ({total_score} ≈ {expected_total})")

                # Check total_score range
                num_dimensions = len(dimension_scores)
                expected_range = num_dimensions * 10
                if total_score < -expected_range or total_score > expected_range:
                    issues.append(f"total_score ({total_score}) out of reasonable range [-{expected_range}, {expected_range}]")
                    score -= 10
                    total_score_valid = False
        else:
            reasoning_parts.append("Overall assessment missing")

        # 3. Check confidence range (0-1)
        confidence_valid = True
        if 'overall_assessment' in result:
            confidence = result['overall_assessment'].get('confidence')
            if confidence is not None:
                if not isinstance(confidence, (int, float)):
                    issues.append("confidence is not numeric")
                    score -= 5
                    confidence_valid = False
                    reasoning_parts.append("Confidence is not numeric")
                elif confidence < 0 or confidence > 1:
                    issues.append(f"confidence ({confidence}) out of range [0, 1]")
                    score -= 10
                    confidence_valid = False
                    reasoning_parts.append(f"Confidence out of range ({confidence})")
                elif confidence < 0.6:
                    recommendations.append(f"Low confidence ({confidence:.2f}), recommend re-analysis")
                    reasoning_parts.append(f"Low confidence ({confidence:.2f})")
                else:
                    reasoning_parts.append(f"Good confidence ({confidence:.2f})")
        else:
            confidence_valid = False

        # 4. Check if recommendation is valid
        recommendation_valid = True
        if 'overall_assessment' in result:
            rec = result['overall_assessment'].get('recommendation', '').lower()
            valid_recommendations = ['买入', '持有', '卖出', '超配', '标配', '低配',
                                   'buy', 'hold', 'sell', 'overweight', 'equal-weight', 'underweight']

            if rec and rec not in valid_recommendations:
                issues.append(f"recommendation '{rec}' is not valid")
                score -= 5
                recommendation_valid = False
                reasoning_parts.append(f"Invalid recommendation ('{rec}')")
            elif rec:
                reasoning_parts.append(f"Valid recommendation ('{rec}')")
        else:
            recommendation_valid = False

        if score < 0:
            score = 0

        # Generate reasoning summary
        if not reasoning_parts:
            reasoning = "All scores are consistent and valid"
        else:
            reasoning = "; ".join(reasoning_parts)

        return {
            'score': score,
            'max_score': 100,
            'dimension_scores': dimension_scores,
            'dimension_scores_sum': sum(dimension_scores) if dimension_scores else None,
            'issues': issues,
            'recommendations': recommendations,
            'reasoning': reasoning
        }

    def _check_depth(self, result: Dict) -> Dict:
        """Check analysis depth"""
        issues = []
        recommendations = []
        score = 100
        reasoning_parts = []

        # 1. Check Storyline detail level
        storyline_quality = "good"
        if 'storyline' in result:
            storyline = result['storyline']
            summary = storyline.get('summary', '')

            if len(summary) < 100:
                issues.append(f"Storyline summary too short ({len(summary)} characters), recommend >200 characters")
                score -= 10
                storyline_quality = "poor"
            elif len(summary) > 500:
                recommendations.append("Storyline summary is long, consider condensing to 200-400 characters")
                storyline_quality = "acceptable"
            else:
                storyline_quality = "good"

            key_events = storyline.get('key_events', [])
            if len(key_events) < 2:
                issues.append(f"Key events count ({len(key_events)}) is low, recommend at least 3-5")
                score -= 10
                storyline_quality = "poor"
            elif len(key_events) >= 3:
                storyline_quality = "excellent"
        else:
            storyline_quality = "missing"
            issues.append("Storyline section is missing")
            score -= 15

        reasoning_parts.append(f"Storyline quality: {storyline_quality}")

        # 2. Check word count for each dimension analysis
        dimension_fields = [
            'financial_impact', 'operational_impact', 'market_impact',
            'regulatory_impact', 'strategic_impact', 'future_outlook'
        ]

        short_analyses = []
        for dim in dimension_fields:
            if dim in result and isinstance(result[dim], dict):
                analysis = result[dim].get('analysis', '')
                if len(analysis) < 50:
                    short_analyses.append(dim)
                    score -= 5

        if short_analyses:
            issues.append(f"Short analyses in: {', '.join(short_analyses)}")
            recommendations.append("Each dimension analysis should be at least 100-200 words")
            reasoning_parts.append(f"{len(short_analyses)} dimension(s) with short analyses")
        else:
            reasoning_parts.append("All dimension analyses have adequate length")

        # 3. Check key_insights count
        insights_count = 0
        if 'overall_assessment' in result:
            insights = result['overall_assessment'].get('key_insights', [])
            insights_count = len(insights)
            if len(insights) < 3:
                issues.append(f"Key insights count ({len(insights)}) is low, recommend at least 3-5")
                score -= 10
                reasoning_parts.append(f"Few key insights ({insights_count})")
            else:
                reasoning_parts.append(f"Good number of key insights ({insights_count})")

        # 4. Check future_outlook phase analysis
        future_outlook_complete = False
        if 'future_outlook' in result:
            fo = result['future_outlook']
            required_phases = ['short_term_impact', 'medium_term_impact', 'long_term_impact']
            missing_phases = [p for p in required_phases if p not in fo]

            if missing_phases:
                issues.append(f"Future Outlook missing phase analysis: {', '.join(missing_phases)}")
                score -= len(missing_phases) * 5
                reasoning_parts.append(f"Future outlook missing {len(missing_phases)} phase(s)")
            else:
                future_outlook_complete = True
                reasoning_parts.append("Future outlook has all phase analyses")
        else:
            issues.append("Future outlook section is missing")
            score -= 15
            reasoning_parts.append("Future outlook missing")

        if score < 0:
            score = 0

        # Generate reasoning summary
        reasoning = "; ".join(reasoning_parts)

        return {
            'score': score,
            'max_score': 100,
            'storyline_summary_length': len(result.get('storyline', {}).get('summary', '')),
            'key_events_count': len(result.get('storyline', {}).get('key_events', [])),
            'key_insights_count': insights_count,
            'issues': issues,
            'recommendations': recommendations,
            'reasoning': reasoning
        }

    def _check_industry_depth(self, result: Dict) -> Dict:
        """Check industry analysis depth"""
        issues = []
        recommendations = []
        score = 100
        reasoning_parts = []

        # 1. Check Storyline detail level
        storyline_quality = "good"
        if 'storyline' in result:
            storyline = result['storyline']
            summary = storyline.get('summary', '')

            if len(summary) < 100:
                issues.append(f"Storyline summary too short ({len(summary)} characters), recommend >200 characters")
                score -= 10
                storyline_quality = "poor"
            elif len(summary) > 500:
                recommendations.append("Storyline summary is long, consider condensing to 200-400 characters")
                storyline_quality = "acceptable"
            else:
                storyline_quality = "good"

            key_events = storyline.get('key_events', [])
            if len(key_events) < 2:
                issues.append(f"Key events count ({len(key_events)}) is low, recommend at least 3-5")
                score -= 10
                storyline_quality = "poor"
            elif len(key_events) >= 3:
                storyline_quality = "excellent"
        else:
            storyline_quality = "missing"
            issues.append("Storyline section is missing")
            score -= 15

        reasoning_parts.append(f"Storyline quality: {storyline_quality}")

        # 2. Check word count for each dimension analysis
        dimension_fields = [
            'industry_trend', 'competitive_landscape', 'policy_regulatory',
            'supply_chain_ecosystem', 'investment_attractiveness', 'future_outlook'
        ]

        short_analyses = []
        for dim in dimension_fields:
            if dim in result and isinstance(result[dim], dict):
                analysis = result[dim].get('analysis', '')
                if len(analysis) < 50:
                    short_analyses.append(dim)
                    score -= 5

        if short_analyses:
            issues.append(f"Short analyses in: {', '.join(short_analyses)}")
            recommendations.append("Each dimension analysis should be at least 100-200 words")
            reasoning_parts.append(f"{len(short_analyses)} dimension(s) with short analyses")
        else:
            reasoning_parts.append("All dimension analyses have adequate length")

        # 3. Check key_insights count
        insights_count = 0
        if 'overall_assessment' in result:
            insights = result['overall_assessment'].get('key_insights', [])
            insights_count = len(insights)
            if len(insights) < 3:
                issues.append(f"Key insights count ({len(insights)}) is low, recommend at least 3-5")
                score -= 10
                reasoning_parts.append(f"Few key insights ({insights_count})")
            else:
                reasoning_parts.append(f"Good number of key insights ({insights_count})")

        # 4. Check future_outlook phase analysis
        future_outlook_complete = False
        if 'future_outlook' in result:
            fo = result['future_outlook']
            required_phases = ['short_term_impact', 'medium_term_impact', 'long_term_impact']
            missing_phases = [p for p in required_phases if p not in fo]

            if missing_phases:
                issues.append(f"Future Outlook missing phase analysis: {', '.join(missing_phases)}")
                score -= len(missing_phases) * 5
                reasoning_parts.append(f"Future outlook missing {len(missing_phases)} phase(s)")
            else:
                future_outlook_complete = True
                reasoning_parts.append("Future outlook has all phase analyses")
        else:
            issues.append("Future outlook section is missing")
            score -= 15
            reasoning_parts.append("Future outlook missing")

        if score < 0:
            score = 0

        # Generate reasoning summary
        reasoning = "; ".join(reasoning_parts)

        return {
            'score': score,
            'max_score': 100,
            'storyline_summary_length': len(result.get('storyline', {}).get('summary', '')),
            'key_events_count': len(result.get('storyline', {}).get('key_events', [])),
            'key_insights_count': insights_count,
            'issues': issues,
            'recommendations': recommendations,
            'reasoning': reasoning
        }

    def _check_timeliness(self, result: Dict) -> Dict:
        """Check data timeliness"""
        issues = []
        recommendations = []
        score = 100
        reasoning_parts = []

        # Check analysis date
        analysis_date = result.get('analysis_date')
        days_old = None
        if analysis_date:
            try:
                analysis_dt = datetime.strptime(analysis_date, '%Y-%m-%d')
                days_old = (datetime.now() - analysis_dt).days

                if days_old > 7:
                    issues.append(f"Analysis date is old ({analysis_date}), {days_old} days ago")
                    score -= 20
                    reasoning_parts.append(f"Analysis is {days_old} days old (>7 days)")
                elif days_old > 3:
                    recommendations.append(f"Analysis date is {analysis_date}, recommend update")
                    reasoning_parts.append(f"Analysis is {days_old} days old (3-7 days)")
                else:
                    reasoning_parts.append(f"Analysis is recent ({days_old} days old)")
            except:
                issues.append("Analysis date format is incorrect")
                score -= 10
                reasoning_parts.append("Invalid date format")
        else:
            issues.append("Analysis date is missing")
            score -= 10
            reasoning_parts.append("Analysis date missing")

        # Check analysis period
        analysis_period = result.get('analysis_period', '')
        if 'recent' in analysis_period or 'Past' in analysis_period or 'past' in analysis_period:
            try:
                match = re.search(r'(\d+)', analysis_period)
                if match:
                    days = int(match.group(1))
                    if days < 3:
                        recommendations.append(f"Analysis period is short ({days} days), recommend 7-30 days")
                        reasoning_parts.append(f"Short analysis period ({days} days)")
                    elif days > 90:
                        recommendations.append(f"Analysis period is long ({days} days), may contain outdated information")
                        reasoning_parts.append(f"Long analysis period ({days} days)")
                    else:
                        reasoning_parts.append(f"Appropriate analysis period ({days} days)")
            except:
                pass

        if score < 0:
            score = 0

        # Generate reasoning summary
        reasoning = "; ".join(reasoning_parts)

        return {
            'score': score,
            'max_score': 100,
            'analysis_date': analysis_date,
            'days_old': days_old,
            'issues': issues,
            'recommendations': recommendations,
            'reasoning': reasoning
        }

    def _check_balance(self, result: Dict) -> Dict:
        """Check analysis balance"""
        issues = []
        recommendations = []
        score = 100
        reasoning_parts = []

        # Check positive/negative score distribution
        dimension_fields = [
            'financial_impact', 'operational_impact', 'market_impact',
            'regulatory_impact', 'strategic_impact', 'future_outlook'
        ]

        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for dim in dimension_fields:
            if dim in result and isinstance(result[dim], dict):
                dim_score = result[dim].get('score', 0)
                if dim_score > 2:
                    positive_count += 1
                elif dim_score < -2:
                    negative_count += 1
                else:
                    neutral_count += 1

        total_scored = positive_count + negative_count + neutral_count

        # Check if too biased toward positive or negative
        balance_status = "balanced"
        if total_scored > 0:
            positive_ratio = positive_count / total_scored
            negative_ratio = negative_count / total_scored

            if positive_ratio > 0.8:
                recommendations.append("Analysis is too positive, recommend adding risk warnings")
                score -= 10
                balance_status = "too positive"
                reasoning_parts.append(f"Too positive ({positive_count}/{total_scored} positive)")
            elif negative_ratio > 0.8:
                recommendations.append("Analysis is too negative, recommend balanced view")
                score -= 10
                balance_status = "too negative"
                reasoning_parts.append(f"Too negative ({negative_count}/{total_scored} negative)")
            else:
                reasoning_parts.append(f"Balanced distribution (P:{positive_count}, N:{negative_count}, Neutral:{neutral_count})")

        # Check if risk analysis is present
        risk_analysis_present = False
        if 'future_outlook' in result:
            fo = result['future_outlook']
            risk_analysis = fo.get('risk_analysis', '')
            if not risk_analysis or len(risk_analysis) < 30:
                recommendations.append("Missing detailed risk analysis")
                score -= 10
                reasoning_parts.append("Insufficient risk analysis")
            else:
                risk_analysis_present = True
                reasoning_parts.append("Risk analysis present")

        if score < 0:
            score = 0

        # Generate reasoning summary
        reasoning = "; ".join(reasoning_parts)

        return {
            'score': score,
            'max_score': 100,
            'positive_dimensions': positive_count,
            'negative_dimensions': negative_count,
            'neutral_dimensions': neutral_count,
            'balance_status': balance_status,
            'risk_analysis_present': risk_analysis_present,
            'issues': issues,
            'recommendations': recommendations,
            'reasoning': reasoning
        }

    def _check_industry_balance(self, result: Dict) -> Dict:
        """Check industry analysis balance"""
        issues = []
        recommendations = []
        score = 100
        reasoning_parts = []

        # Check positive/negative score distribution
        dimension_fields = [
            'industry_trend', 'competitive_landscape', 'policy_regulatory',
            'supply_chain_ecosystem', 'investment_attractiveness', 'future_outlook'
        ]

        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for dim in dimension_fields:
            if dim in result and isinstance(result[dim], dict):
                dim_score = result[dim].get('score', 0)
                if dim_score > 2:
                    positive_count += 1
                elif dim_score < -2:
                    negative_count += 1
                else:
                    neutral_count += 1

        total_scored = positive_count + negative_count + neutral_count

        # Check if too biased toward positive or negative
        balance_status = "balanced"
        if total_scored > 0:
            positive_ratio = positive_count / total_scored
            negative_ratio = negative_count / total_scored

            if positive_ratio > 0.8:
                recommendations.append("Analysis is too positive, recommend adding risk warnings")
                score -= 10
                balance_status = "too positive"
                reasoning_parts.append(f"Too positive ({positive_count}/{total_scored} positive)")
            elif negative_ratio > 0.8:
                recommendations.append("Analysis is too negative, recommend balanced view")
                score -= 10
                balance_status = "too negative"
                reasoning_parts.append(f"Too negative ({negative_count}/{total_scored} negative)")
            else:
                reasoning_parts.append(f"Balanced distribution (P:{positive_count}, N:{negative_count}, Neutral:{neutral_count})")

        # Check if risk analysis is present
        risk_analysis_present = False
        if 'future_outlook' in result:
            fo = result['future_outlook']
            risk_analysis = fo.get('risk_analysis', '')
            if not risk_analysis or len(risk_analysis) < 30:
                recommendations.append("Missing detailed risk analysis")
                score -= 10
                reasoning_parts.append("Insufficient risk analysis")
            else:
                risk_analysis_present = True
                reasoning_parts.append("Risk analysis present")

        if score < 0:
            score = 0

        # Generate reasoning summary
        reasoning = "; ".join(reasoning_parts)

        return {
            'score': score,
            'max_score': 100,
            'positive_dimensions': positive_count,
            'negative_dimensions': negative_count,
            'neutral_dimensions': neutral_count,
            'balance_status': balance_status,
            'risk_analysis_present': risk_analysis_present,
            'issues': issues,
            'recommendations': recommendations,
            'reasoning': reasoning
        }

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

    def generate_evaluation_report(self, analysis_result: Dict, output_file: str = None) -> Dict:
        """
        Generate complete evaluation report and optionally save to file

        Args:
            analysis_result: Analysis result
            output_file: Output file path (optional)

        Returns:
            Evaluation report
        """
        evaluation = self.evaluate_analysis(analysis_result)

        # Add metadata
        evaluation['report_metadata'] = {
            'evaluator_version': '1.0',
            'evaluation_method': 'rule_based_multi_dimensional',
            'criteria': self.evaluation_criteria
        }

        # Save to file
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(evaluation, f, indent=2, ensure_ascii=False)
                logger.info(f"💾 Evaluation report saved to: {output_file}")
            except Exception as e:
                logger.error(f"❌ Failed to save evaluation report: {e}")

        return evaluation


# Convenience function
def evaluate_analysis_quality(analysis_result: Dict) -> Dict:
    """Quickly evaluate analysis quality"""
    evaluator = AnalysisEvaluator()
    return evaluator.evaluate_analysis(analysis_result)


if __name__ == "__main__":
    # Test example
    print("Analysis Evaluator Module")
    print("=" * 60)
    print("Usage:")
    print("  from 09_retrieve.evaluation import AnalysisEvaluator")
    print("  evaluator = AnalysisEvaluator()")
    print("  report = evaluator.evaluate_analysis(analysis_result)")
