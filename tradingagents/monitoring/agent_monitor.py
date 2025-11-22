# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Agent Capability Monitor

Analyzes and reports on agent capabilities and performance.
"""

from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
import logging

from tradingagents.database import get_db_connection

logger = logging.getLogger(__name__)


class AgentCapabilityMonitor:
    """
    Monitor and analyze agent capabilities and performance.
    
    Provides insights into:
    - Individual agent performance metrics
    - Agent health and availability
    - Comparative analysis between agents
    - Capability trends over time
    - Cost and efficiency metrics
    """

    def __init__(self, db=None):
        """
        Initialize agent capability monitor.
        
        Args:
            db: Database connection (creates one if not provided)
        """
        from tradingagents.database import get_db_connection
        self.db = db or get_db_connection()

    def get_agent_comparison(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Get side-by-side comparison of all agents.
        
        Args:
            days_back: Number of days to look back
        
        Returns:
            List of agent comparison dictionaries
        """
        query = """
            SELECT 
                agent_name,
                agent_team,
                COUNT(*) as total_executions,
                SUM(CASE WHEN has_errors = false THEN 1 ELSE 0 END) as successful_executions,
                ROUND(AVG(duration_seconds), 2) as avg_duration_seconds,
                ROUND(AVG(output_quality_score), 2) as avg_quality_score,
                ROUND(AVG(contribution_score), 2) as avg_contribution_score,
                ROUND(SUM(CASE WHEN was_cited_in_final_report THEN 1 ELSE 0 END)::NUMERIC / 
                      NULLIF(COUNT(*), 0) * 100, 2) as citation_rate_pct,
                ROUND(SUM(llm_cost_usd), 2) as total_cost_usd,
                ROUND(AVG(llm_cost_usd), 6) as avg_cost_per_execution
            FROM agent_executions
            WHERE execution_start_time >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY agent_name, agent_team
            ORDER BY avg_quality_score DESC
        """
        
        results = self.db.execute_dict_query(query, (days_back,))
        return results or []

    def get_agent_health_status(self) -> List[Dict[str, Any]]:
        """
        Get health status of all agents.
        
        Returns:
            List of agent health dictionaries
        """
        query = """
            SELECT * FROM v_agent_health
            ORDER BY agent_team, agent_name
        """
        
        results = self.db.execute_dict_query(query)
        return results or []

    def get_agent_performance_trends(
        self,
        agent_name: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get performance trends for a specific agent.
        
        Args:
            agent_name: Name of the agent
            days_back: Number of days to analyze
        
        Returns:
            Dictionary with trend data
        """
        query = """
            SELECT 
                metric_date,
                total_executions,
                success_rate,
                avg_quality_score,
                avg_duration_seconds,
                avg_contribution_score,
                citation_rate,
                avg_cost_per_execution
            FROM agent_capability_metrics
            WHERE agent_name = %s
              AND metric_date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY metric_date ASC
        """
        
        results = self.db.execute_dict_query(query, (agent_name, days_back))
        
        if not results:
            return {
                'agent_name': agent_name,
                'status': 'NO_DATA',
                'message': f'No performance data found for {agent_name}'
            }
        
        # Calculate trends
        recent_quality = [r['avg_quality_score'] for r in results[-7:]]  # Last 7 days
        older_quality = [r['avg_quality_score'] for r in results[:-7]] if len(results) > 7 else recent_quality
        
        quality_trend = 'STABLE'
        if len(recent_quality) > 0 and len(older_quality) > 0:
            recent_avg = sum(recent_quality) / len(recent_quality)
            older_avg = sum(older_quality) / len(older_quality)
            if recent_avg > older_avg + 5:
                quality_trend = 'IMPROVING'
            elif recent_avg < older_avg - 5:
                quality_trend = 'DECLINING'
        
        return {
            'agent_name': agent_name,
            'status': 'ACTIVE',
            'total_days_tracked': len(results),
            'quality_trend': quality_trend,
            'recent_avg_quality': sum(recent_quality) / len(recent_quality) if recent_quality else 0,
            'daily_metrics': results
        }

    def get_top_performers(
        self,
        metric: str = 'quality_score',
        days_back: int = 30,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get top performing agents by metric.
        
        Args:
            metric: Metric to rank by ('quality_score', 'contribution_score', 'citation_rate', 'speed')
            days_back: Number of days to analyze
            limit: Number of top performers to return
        
        Returns:
            List of top performing agents
        """
        metric_map = {
            'quality_score': 'avg_quality_score',
            'contribution_score': 'avg_contribution_score',
            'citation_rate': 'citation_rate_pct',
            'speed': 'avg_duration_seconds'  # Lower is better
        }
        
        order_by = metric_map.get(metric, 'avg_quality_score')
        order_dir = 'ASC' if metric == 'speed' else 'DESC'
        
        query = f"""
            SELECT 
                agent_name,
                agent_team,
                COUNT(*) as total_executions,
                ROUND(AVG(output_quality_score), 2) as avg_quality_score,
                ROUND(AVG(contribution_score), 2) as avg_contribution_score,
                ROUND(SUM(CASE WHEN was_cited_in_final_report THEN 1 ELSE 0 END)::NUMERIC / 
                      NULLIF(COUNT(*), 0) * 100, 2) as citation_rate_pct,
                ROUND(AVG(duration_seconds), 2) as avg_duration_seconds
            FROM agent_executions
            WHERE execution_start_time >= CURRENT_DATE - INTERVAL '%s days'
              AND has_errors = false
            GROUP BY agent_name, agent_team
            HAVING COUNT(*) >= 3  -- At least 3 successful executions
            ORDER BY {order_by} {order_dir}
            LIMIT %s
        """
        
        results = self.db.execute_dict_query(query, (days_back, limit))
        return results or []

    def get_agent_capabilities_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of all agent capabilities.
        
        Returns:
            Dictionary with capability summary
        """
        comparison = self.get_agent_comparison(days_back=30)
        health = self.get_agent_health_status()
        
        # Group by team
        by_team = {}
        for agent in comparison:
            team = agent['agent_team']
            if team not in by_team:
                by_team[team] = []
            by_team[team].append(agent)
        
        # Calculate overall statistics
        total_executions = sum(a['total_executions'] for a in comparison)
        total_cost = sum(a.get('total_cost_usd', 0) or 0 for a in comparison)
        avg_quality = sum(a.get('avg_quality_score', 0) or 0 for a in comparison) / len(comparison) if comparison else 0
        
        # Identify issues
        issues = []
        for agent_health in health:
            if agent_health['health_status'] != 'HEALTHY':
                issues.append({
                    'agent': agent_health['agent_name'],
                    'team': agent_health['agent_team'],
                    'status': agent_health['health_status'],
                    'reason': self._get_health_reason(agent_health)
                })
        
        return {
            'summary': {
                'total_agents': len(comparison),
                'total_executions_30d': total_executions,
                'total_cost_30d': round(total_cost, 2),
                'avg_quality_score': round(avg_quality, 2),
                'agents_by_team': {team: len(agents) for team, agents in by_team.items()}
            },
            'by_team': by_team,
            'health_status': health,
            'issues': issues,
            'top_performers': {
                'quality': self.get_top_performers('quality_score', limit=3),
                'contribution': self.get_top_performers('contribution_score', limit=3),
                'speed': self.get_top_performers('speed', limit=3)
            }
        }

    def generate_capability_report(
        self,
        days_back: int = 30,
        include_trends: bool = True
    ) -> str:
        """
        Generate a comprehensive capability report.
        
        Args:
            days_back: Number of days to analyze
            include_trends: Whether to include trend analysis
        
        Returns:
            Formatted report string
        """
        summary = self.get_agent_capabilities_summary()
        report_lines = []
        
        report_lines.append("=" * 80)
        report_lines.append("AGENT CAPABILITY MONITORING REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Analysis Period: Last {days_back} days")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Overall Summary
        report_lines.append("📊 OVERALL SUMMARY")
        report_lines.append("-" * 80)
        s = summary['summary']
        report_lines.append(f"Total Agents: {s['total_agents']}")
        report_lines.append(f"Total Executions (30d): {s['total_executions_30d']}")
        report_lines.append(f"Total Cost (30d): ${s['total_cost_30d']:.2f}")
        report_lines.append(f"Average Quality Score: {s['avg_quality_score']:.1f}/100")
        report_lines.append("")
        report_lines.append("Agents by Team:")
        for team, count in s['agents_by_team'].items():
            report_lines.append(f"  • {team.title()}: {count} agents")
        report_lines.append("")
        
        # Health Status
        report_lines.append("🏥 AGENT HEALTH STATUS")
        report_lines.append("-" * 80)
        healthy_count = sum(1 for h in summary['health_status'] if h['health_status'] == 'HEALTHY')
        report_lines.append(f"Healthy: {healthy_count}/{len(summary['health_status'])}")
        
        if summary['issues']:
            report_lines.append("\n⚠️  Issues Detected:")
            for issue in summary['issues']:
                report_lines.append(
                    f"  • {issue['agent']} ({issue['team']}): {issue['status']} - {issue['reason']}"
                )
        else:
            report_lines.append("\n✅ All agents are healthy!")
        report_lines.append("")
        
        # Top Performers
        report_lines.append("🏆 TOP PERFORMERS")
        report_lines.append("-" * 80)
        
        report_lines.append("\nBy Quality Score:")
        for i, agent in enumerate(summary['top_performers']['quality'], 1):
            report_lines.append(
                f"  {i}. {agent['agent_name']} ({agent['agent_team']}): "
                f"Quality {agent['avg_quality_score']:.1f}, "
                f"{agent['total_executions']} executions"
            )
        
        report_lines.append("\nBy Contribution Score:")
        for i, agent in enumerate(summary['top_performers']['contribution'], 1):
            report_lines.append(
                f"  {i}. {agent['agent_name']} ({agent['agent_team']}): "
                f"Contribution {agent['avg_contribution_score']:.1f}, "
                f"Citation Rate {agent['citation_rate_pct']:.1f}%"
            )
        
        report_lines.append("\nBy Speed (Fastest):")
        for i, agent in enumerate(summary['top_performers']['speed'], 1):
            report_lines.append(
                f"  {i}. {agent['agent_name']} ({agent['agent_team']}): "
                f"{agent['avg_duration_seconds']:.2f}s avg"
            )
        report_lines.append("")
        
        # By Team Breakdown
        report_lines.append("👥 PERFORMANCE BY TEAM")
        report_lines.append("-" * 80)
        for team, agents in summary['by_team'].items():
            report_lines.append(f"\n{team.upper()} TEAM:")
            for agent in sorted(agents, key=lambda x: x.get('avg_quality_score', 0) or 0, reverse=True):
                report_lines.append(
                    f"  • {agent['agent_name']}: "
                    f"Quality {agent.get('avg_quality_score', 0) or 0:.1f}, "
                    f"Duration {agent.get('avg_duration_seconds', 0) or 0:.2f}s, "
                    f"Citations {agent.get('citation_rate_pct', 0) or 0:.1f}%"
                )
        
        report_lines.append("")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)

    def _get_health_reason(self, health_data: Dict[str, Any]) -> str:
        """Get human-readable reason for health status."""
        status = health_data['health_status']
        
        if status == 'INACTIVE':
            return "No executions in last 7 days"
        elif status == 'UNHEALTHY':
            error_rate = (health_data.get('errors_last_7_days', 0) or 0) / max(
                health_data.get('executions_last_7_days', 1) or 1, 1
            ) * 100
            return f"High error rate: {error_rate:.1f}%"
        elif status == 'POOR_QUALITY':
            quality = health_data.get('avg_quality_last_7_days', 0) or 0
            return f"Low quality score: {quality:.1f}/100"
        else:
            return "All systems operational"

