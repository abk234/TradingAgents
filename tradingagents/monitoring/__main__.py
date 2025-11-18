"""
Agent Capability Monitoring CLI

Command-line interface for monitoring agent capabilities and performance.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from .agent_monitor import AgentCapabilityMonitor


def cmd_report(args):
    """Generate capability report."""
    monitor = AgentCapabilityMonitor()
    
    print(f"\n{'='*80}")
    print("Generating Agent Capability Report...")
    print(f"{'='*80}\n")
    
    report = monitor.generate_capability_report(
        days_back=args.days,
        include_trends=args.trends
    )
    
    print(report)
    
    # Save to file if requested
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report)
        print(f"\n✅ Report saved to: {output_path}")


def cmd_health(args):
    """Show agent health status."""
    monitor = AgentCapabilityMonitor()
    
    health_status = monitor.get_agent_health_status()
    
    print(f"\n{'='*80}")
    print("AGENT HEALTH STATUS")
    print(f"{'='*80}\n")
    
    # Group by status
    by_status = {}
    for agent in health_status:
        status = agent['health_status']
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(agent)
    
    for status, agents in sorted(by_status.items()):
        emoji = {
            'HEALTHY': '✅',
            'INACTIVE': '⏸️',
            'UNHEALTHY': '⚠️',
            'POOR_QUALITY': '📉'
        }.get(status, '❓')
        
        print(f"\n{emoji} {status} ({len(agents)} agents)")
        print("-" * 80)
        
        for agent in agents:
            print(f"  • {agent['agent_name']} ({agent['agent_team']})")
            if agent.get('executions_last_7_days'):
                print(f"    Executions (7d): {agent['executions_last_7_days']}")
                print(f"    Avg Quality: {agent.get('avg_quality_last_7_days', 0) or 0:.1f}")
                print(f"    Avg Duration: {agent.get('avg_duration_last_7_days', 0) or 0:.2f}s")
            if agent.get('errors_last_7_days', 0) or 0 > 0:
                print(f"    ⚠️  Errors: {agent['errors_last_7_days']}")


def cmd_compare(args):
    """Compare agents side-by-side."""
    monitor = AgentCapabilityMonitor()
    
    comparison = monitor.get_agent_comparison(days_back=args.days)
    
    print(f"\n{'='*80}")
    print(f"AGENT COMPARISON (Last {args.days} days)")
    print(f"{'='*80}\n")
    
    # Format as table
    print(f"{'Agent':<25} {'Team':<15} {'Executions':<12} {'Quality':<10} {'Duration':<12} {'Citations':<12}")
    print("-" * 80)
    
    for agent in comparison:
        print(
            f"{agent['agent_name']:<25} "
            f"{agent['agent_team']:<15} "
            f"{agent['total_executions']:<12} "
            f"{agent.get('avg_quality_score', 0) or 0:<10.1f} "
            f"{agent.get('avg_duration_seconds', 0) or 0:<12.2f}s "
            f"{agent.get('citation_rate_pct', 0) or 0:<12.1f}%"
        )


def cmd_trends(args):
    """Show performance trends for an agent."""
    monitor = AgentCapabilityMonitor()
    
    trends = monitor.get_agent_performance_trends(
        agent_name=args.agent,
        days_back=args.days
    )
    
    if trends.get('status') == 'NO_DATA':
        print(f"\n❌ {trends['message']}")
        return
    
    print(f"\n{'='*80}")
    print(f"PERFORMANCE TRENDS: {trends['agent_name']}")
    print(f"{'='*80}\n")
    
    print(f"Status: {trends['status']}")
    print(f"Quality Trend: {trends['quality_trend']}")
    print(f"Recent Avg Quality: {trends['recent_avg_quality']:.1f}/100")
    print(f"Days Tracked: {trends['total_days_tracked']}")
    print("\nDaily Metrics:")
    print("-" * 80)
    print(f"{'Date':<12} {'Executions':<12} {'Success %':<12} {'Quality':<10} {'Duration':<12}")
    print("-" * 80)
    
    for day in trends['daily_metrics'][-14:]:  # Last 14 days
        print(
            f"{day['metric_date']:<12} "
            f"{day['total_executions']:<12} "
            f"{day.get('success_rate', 0) or 0:<12.1f}% "
            f"{day.get('avg_quality_score', 0) or 0:<10.1f} "
            f"{day.get('avg_duration_seconds', 0) or 0:<12.2f}s"
        )


def cmd_top(args):
    """Show top performing agents."""
    monitor = AgentCapabilityMonitor()
    
    top = monitor.get_top_performers(
        metric=args.metric,
        days_back=args.days,
        limit=args.limit
    )
    
    metric_name = args.metric.replace('_', ' ').title()
    print(f"\n{'='*80}")
    print(f"TOP {args.limit} AGENTS BY {metric_name.upper()}")
    print(f"{'='*80}\n")
    
    for i, agent in enumerate(top, 1):
        print(f"{i}. {agent['agent_name']} ({agent['agent_team']})")
        print(f"   Quality: {agent.get('avg_quality_score', 0) or 0:.1f}")
        print(f"   Contribution: {agent.get('avg_contribution_score', 0) or 0:.1f}")
        print(f"   Citations: {agent.get('citation_rate_pct', 0) or 0:.1f}%")
        print(f"   Duration: {agent.get('avg_duration_seconds', 0) or 0:.2f}s")
        print(f"   Executions: {agent['total_executions']}")
        print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Agent Capability Monitoring CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate full capability report
  python -m tradingagents.monitoring report --days 30

  # Show agent health status
  python -m tradingagents.monitoring health

  # Compare all agents
  python -m tradingagents.monitoring compare --days 30

  # Show trends for specific agent
  python -m tradingagents.monitoring trends --agent market_analyst

  # Show top 5 agents by quality
  python -m tradingagents.monitoring top --metric quality_score --limit 5
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate capability report')
    report_parser.add_argument('--days', type=int, default=30, help='Days to analyze (default: 30)')
    report_parser.add_argument('--trends', action='store_true', help='Include trend analysis')
    report_parser.add_argument('--output', type=str, help='Save report to file')
    report_parser.set_defaults(func=cmd_report)
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Show agent health status')
    health_parser.set_defaults(func=cmd_health)
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare agents side-by-side')
    compare_parser.add_argument('--days', type=int, default=30, help='Days to analyze (default: 30)')
    compare_parser.set_defaults(func=cmd_compare)
    
    # Trends command
    trends_parser = subparsers.add_parser('trends', help='Show performance trends for an agent')
    trends_parser.add_argument('--agent', type=str, required=True, help='Agent name')
    trends_parser.add_argument('--days', type=int, default=30, help='Days to analyze (default: 30)')
    trends_parser.set_defaults(func=cmd_trends)
    
    # Top command
    top_parser = subparsers.add_parser('top', help='Show top performing agents')
    top_parser.add_argument('--metric', type=str, default='quality_score',
                          choices=['quality_score', 'contribution_score', 'citation_rate', 'speed'],
                          help='Metric to rank by')
    top_parser.add_argument('--days', type=int, default=30, help='Days to analyze (default: 30)')
    top_parser.add_argument('--limit', type=int, default=5, help='Number of top agents to show')
    top_parser.set_defaults(func=cmd_top)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

