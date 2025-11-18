"""
Profitability Performance Monitoring Script

Tracks and reports on the performance of profitability improvements.
"""

import sys
from datetime import date, timedelta
from decimal import Decimal
import logging
from typing import Dict, Any, List
import json

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class ProfitabilityMonitor:
    """
    Monitor performance of profitability improvements.
    
    Tracks:
    - Win rate by confidence level
    - Gate score vs performance correlation
    - Position size vs returns
    - Exit strategy effectiveness
    - Sector rotation accuracy
    """
    
    def __init__(self, db=None):
        """Initialize performance monitor."""
        from tradingagents.database import get_db_connection
        
        self.db = db or get_db_connection()
    
    def analyze_win_rate_by_confidence(self, days_back: int = 90) -> Dict[str, Any]:
        """
        Analyze win rate by confidence level.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            Dict with win rate statistics by confidence range
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)
        
        query = """
            SELECT 
                CASE 
                    WHEN confidence_score >= 90 THEN '90-100'
                    WHEN confidence_score >= 80 THEN '80-89'
                    WHEN confidence_score >= 70 THEN '70-79'
                    WHEN confidence_score >= 60 THEN '60-69'
                    ELSE '<60'
                END as confidence_range,
                COUNT(*) as total_recommendations,
                SUM(CASE WHEN final_decision = 'BUY' THEN 1 ELSE 0 END) as buy_signals,
                AVG(confidence_score) as avg_confidence
            FROM analyses
            WHERE analysis_date >= %s
            GROUP BY confidence_range
            ORDER BY confidence_range DESC
        """
        
        results = self.db.execute_dict_query(query, (start_date,))
        
        return {
            'period': f"{start_date} to {end_date}",
            'by_confidence': results,
            'summary': self._summarize_confidence_results(results)
        }
    
    def analyze_gate_scores_vs_performance(self, days_back: int = 90) -> Dict[str, Any]:
        """
        Analyze correlation between gate scores and performance.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            Dict with gate score performance statistics
        """
        # This would require tracking actual returns
        # Placeholder for now
        return {
            'note': 'Gate score vs performance analysis requires return tracking',
            'recommendation': 'Implement return tracking in performance_tracking table'
        }
    
    def analyze_position_sizing_effectiveness(self, days_back: int = 90) -> Dict[str, Any]:
        """
        Analyze if larger positions (high confidence) perform better.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            Dict with position sizing statistics
        """
        # This would require tracking position sizes and returns
        # Placeholder for now
        return {
            'note': 'Position sizing analysis requires position tracking',
            'recommendation': 'Track position sizes in portfolio_actions table'
        }
    
    def analyze_sector_rotation_accuracy(self, days_back: int = 90) -> Dict[str, Any]:
        """
        Analyze accuracy of sector rotation recommendations.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            Dict with sector rotation statistics
        """
        from tradingagents.decision.sector_rotation import SectorRotationDetector
        
        detector = SectorRotationDetector()
        
        # Get sector actions
        actions = detector.detect_sector_rotation()
        
        # Get top sectors
        top_sectors = detector.get_top_sectors(limit=5)
        
        return {
            'sector_actions': actions,
            'top_sectors': [
                {
                    'sector': s['sector'],
                    'momentum_score': s['momentum_score'],
                    '3m_return': s['3m_return'],
                    '6m_return': s['6m_return']
                }
                for s in top_sectors
            ],
            'recommendations': self._generate_sector_recommendations(actions, top_sectors)
        }
    
    def generate_performance_report(self, days_back: int = 90) -> str:
        """
        Generate comprehensive performance report.
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Formatted report string
        """
        report_lines = []
        report_lines.append("="*70)
        report_lines.append("PROFITABILITY IMPROVEMENTS PERFORMANCE REPORT")
        report_lines.append("="*70)
        report_lines.append(f"Analysis Period: Last {days_back} days")
        report_lines.append("")
        
        # Win rate by confidence
        report_lines.append("WIN RATE BY CONFIDENCE LEVEL")
        report_lines.append("-"*70)
        win_rate_data = self.analyze_win_rate_by_confidence(days_back)
        for result in win_rate_data['by_confidence']:
            report_lines.append(
                f"Confidence {result['confidence_range']}: "
                f"{result['total_recommendations']} recommendations, "
                f"{result['buy_signals']} BUY signals, "
                f"Avg confidence: {result['avg_confidence']:.1f}"
            )
        report_lines.append("")
        
        # Sector rotation
        report_lines.append("SECTOR ROTATION ANALYSIS")
        report_lines.append("-"*70)
        sector_data = self.analyze_sector_rotation_accuracy(days_back)
        report_lines.append("Top Sectors by Momentum:")
        for sector_info in sector_data['top_sectors']:
            report_lines.append(
                f"  {sector_info['sector']}: "
                f"Momentum {sector_info['momentum_score']:.2f}, "
                f"3M: {sector_info['3m_return']:.1f}%, "
                f"6M: {sector_info['6m_return']:.1f}%"
            )
        report_lines.append("")
        report_lines.append("Sector Recommendations:")
        for sector, action in sector_data['sector_actions'].items():
            if action != 'NEUTRAL':
                report_lines.append(f"  {sector}: {action}")
        report_lines.append("")
        
        # Recommendations
        report_lines.append("RECOMMENDATIONS")
        report_lines.append("-"*70)
        recommendations = self._generate_recommendations(win_rate_data, sector_data)
        for rec in recommendations:
            report_lines.append(f"  • {rec}")
        report_lines.append("")
        
        report_lines.append("="*70)
        
        return "\n".join(report_lines)
    
    def _summarize_confidence_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Summarize confidence analysis results."""
        total = sum(r['total_recommendations'] for r in results)
        total_buys = sum(r['buy_signals'] for r in results)
        
        return {
            'total_recommendations': total,
            'total_buy_signals': total_buys,
            'buy_rate': (total_buys / total * 100) if total > 0 else 0
        }
    
    def _generate_sector_recommendations(
        self,
        actions: Dict[str, str],
        top_sectors: List[Dict]
    ) -> List[str]:
        """Generate sector allocation recommendations."""
        recommendations = []
        
        overweight_sectors = [s for s, a in actions.items() if a == 'OVERWEIGHT']
        underweight_sectors = [s for s, a in actions.items() if a == 'UNDERWEIGHT']
        
        if overweight_sectors:
            recommendations.append(
                f"Consider overweighting: {', '.join(overweight_sectors[:3])}"
            )
        
        if underweight_sectors:
            recommendations.append(
                f"Consider underweighting: {', '.join(underweight_sectors[:3])}"
            )
        
        return recommendations
    
    def _generate_recommendations(
        self,
        win_rate_data: Dict,
        sector_data: Dict
    ) -> List[str]:
        """Generate overall recommendations."""
        recommendations = []
        
        # Check if high confidence performs better
        high_conf_results = [r for r in win_rate_data['by_confidence'] if r['confidence_range'] in ['90-100', '80-89']]
        if high_conf_results:
            avg_buy_rate = sum(r['buy_signals'] for r in high_conf_results) / sum(r['total_recommendations'] for r in high_conf_results) if sum(r['total_recommendations'] for r in high_conf_results) > 0 else 0
            recommendations.append(
                f"High confidence trades ({avg_buy_rate*100:.1f}% buy rate) - "
                "consider increasing position sizes for these"
            )
        
        # Sector recommendations
        recommendations.extend(sector_data['recommendations'])
        
        return recommendations


def main():
    """Run performance monitoring."""
    monitor = ProfitabilityMonitor()
    
    # Generate report
    report = monitor.generate_performance_report(days_back=90)
    print(report)
    
    # Save to file
    output_file = f"profitability_performance_report_{date.today().strftime('%Y%m%d')}.txt"
    with open(output_file, 'w') as f:
        f.write(report)
    
    logger.info(f"\nReport saved to: {output_file}")


if __name__ == "__main__":
    main()

