"""
Eddie Database Prerequisites Validation

Validates that all required database tables and data are available
for Eddie to perform valid trading strategies and make prompt decisions.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple
import sys

from tradingagents.database import get_db_connection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EddiePrerequisitesValidator:
    """Validates Eddie's database prerequisites."""

    def __init__(self):
        self.db = get_db_connection()
        self.results = {
            'checks': {},
            'overall_status': 'UNKNOWN',
            'recommendations': []
        }

    def check_tickers(self) -> Tuple[bool, str, Dict]:
        """Check if tickers table has sufficient data."""
        query = """
        SELECT 
            COUNT(*) as total_tickers,
            COUNT(*) FILTER (WHERE active = true) as active_tickers,
            COUNT(DISTINCT sector) as sector_count,
            COUNT(*) FILTER (WHERE sector IS NOT NULL) as tickers_with_sector
        FROM tickers
        """
        
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query)
                row = cursor.fetchone()
                
            total = row[0] if row else 0
            active = row[1] if row else 0
            sectors = row[2] if row else 0
            with_sector = row[3] if row else 0

            passed = active >= 10 and sectors >= 3
            
            status = "✅ PASS" if passed else "❌ FAIL"
            message = (
                f"{status} Tickers: {active} active tickers across {sectors} sectors"
            )
            
            if not passed:
                if active < 10:
                    self.results['recommendations'].append(
                        f"Add more tickers to watchlist (currently {active}, need >= 10)"
                    )
                if sectors < 3:
                    self.results['recommendations'].append(
                        f"Add tickers from more sectors (currently {sectors}, need >= 3)"
                    )

            return passed, message, {
                'total_tickers': total,
                'active_tickers': active,
                'sector_count': sectors,
                'tickers_with_sector': with_sector
            }
            
        except Exception as e:
            return False, f"❌ ERROR checking tickers: {e}", {}

    def check_price_cache(self) -> Tuple[bool, str, Dict]:
        """Check if price_cache table has recent data."""
        query = """
        SELECT 
            COUNT(DISTINCT ticker_id) as tickers_with_data,
            MIN(price_date) as oldest_date,
            MAX(price_date) as newest_date,
            COUNT(*) as total_records,
            COUNT(*) FILTER (WHERE is_realtime = true) as realtime_records,
            COUNT(*) FILTER (WHERE price_date >= CURRENT_DATE - INTERVAL '7 days') as recent_records
        FROM price_cache
        """
        
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query)
                row = cursor.fetchone()
                
            tickers = row[0] if row else 0
            oldest = row[1] if row else None
            newest = row[2] if row else None
            total = row[3] if row else 0
            realtime = row[4] if row else 0
            recent = row[5] if row else 0

            # Check if newest data is recent (within 24 hours)
            is_recent = False
            if newest:
                days_old = (date.today() - newest).days
                is_recent = days_old <= 1
            
            passed = tickers >= 10 and is_recent and recent >= 50
            
            status = "✅ PASS" if passed else "❌ FAIL"
            message = (
                f"{status} Price Cache: {tickers} tickers, "
                f"newest: {newest}, {recent} recent records"
            )
            
            if not passed:
                if tickers < 10:
                    self.results['recommendations'].append(
                        f"Populate price cache for more tickers (currently {tickers}, need >= 10)"
                    )
                if not is_recent:
                    self.results['recommendations'].append(
                        f"Refresh price cache (newest data: {newest}, need today or yesterday)"
                    )

            return passed, message, {
                'tickers_with_data': tickers,
                'oldest_date': str(oldest) if oldest else None,
                'newest_date': str(newest) if newest else None,
                'total_records': total,
                'realtime_records': realtime,
                'recent_records': recent,
                'is_recent': is_recent
            }
            
        except Exception as e:
            return False, f"❌ ERROR checking price cache: {e}", {}

    def check_daily_scans(self) -> Tuple[bool, str, Dict]:
        """Check if daily_scans table has recent scans."""
        query = """
        SELECT 
            MAX(scan_date) as latest_scan_date,
            COUNT(*) FILTER (WHERE scan_date >= CURRENT_DATE - INTERVAL '1 day') as today_scans,
            COUNT(*) FILTER (WHERE scan_date >= CURRENT_DATE - INTERVAL '7 days') as week_scans,
            AVG(priority_score) FILTER (WHERE scan_date >= CURRENT_DATE - INTERVAL '1 day') as avg_score,
            COUNT(DISTINCT ticker_id) FILTER (WHERE scan_date >= CURRENT_DATE - INTERVAL '1 day') as tickers_scanned
        FROM daily_scans
        """
        
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query)
                row = cursor.fetchone()
                
            latest = row[0] if row else None
            today_count = row[1] if row else 0
            week_count = row[2] if row else 0
            avg_score = float(row[3]) if row[3] else 0
            tickers = row[4] if row else 0

            # Check if latest scan is recent (within 24 hours)
            is_recent = False
            if latest:
                days_old = (date.today() - latest).days
                is_recent = days_old <= 1
            
            passed = is_recent and tickers >= 10
            
            status = "✅ PASS" if passed else "❌ FAIL"
            message = (
                f"{status} Daily Scans: Latest scan {latest}, "
                f"{tickers} tickers scanned today"
            )
            
            if not passed:
                if not is_recent:
                    self.results['recommendations'].append(
                        f"Run daily screener (latest scan: {latest}, need today or yesterday)"
                    )
                if tickers < 10:
                    self.results['recommendations'].append(
                        f"Scan more tickers (currently {tickers}, need >= 10)"
                    )

            return passed, message, {
                'latest_scan_date': str(latest) if latest else None,
                'today_scans': today_count,
                'week_scans': week_count,
                'avg_score': avg_score,
                'tickers_scanned': tickers,
                'is_recent': is_recent
            }
            
        except Exception as e:
            return False, f"❌ ERROR checking daily scans: {e}", {}

    def check_analyses(self) -> Tuple[bool, str, Dict]:
        """Check if analyses table has historical data."""
        query = """
        SELECT 
            COUNT(*) as total_analyses,
            COUNT(DISTINCT ticker_id) as unique_tickers,
            COUNT(*) FILTER (WHERE embedding IS NOT NULL) as with_embeddings,
            MAX(analysis_date) as latest_analysis,
            COUNT(*) FILTER (WHERE analysis_date >= CURRENT_DATE - INTERVAL '7 days') as recent_analyses
        FROM analyses
        """
        
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query)
                row = cursor.fetchone()
                
            total = row[0] if row else 0
            unique = row[1] if row else 0
            with_emb = row[2] if row else 0
            latest = row[3] if row else None
            recent = row[4] if row else 0

            # Recommended but not critical
            passed = total >= 5 and with_emb >= 5
            
            status = "✅ PASS" if passed else "⚠️  WARN"
            message = (
                f"{status} Analyses: {total} total, {with_emb} with embeddings, "
                f"latest: {latest}"
            )
            
            if not passed:
                self.results['recommendations'].append(
                    "Generate more analyses for better learning and pattern recognition"
                )

            return passed, message, {
                'total_analyses': total,
                'unique_tickers': unique,
                'with_embeddings': with_emb,
                'latest_analysis': str(latest) if latest else None,
                'recent_analyses': recent
            }
            
        except Exception as e:
            return False, f"❌ ERROR checking analyses: {e}", {}

    def check_system_config(self) -> Tuple[bool, str, Dict]:
        """Check if system_config table has required settings."""
        query = """
        SELECT config_key, config_value
        FROM system_config
        WHERE config_key IN ('screening_thresholds', 'buy_decision_gates', 'position_sizing_rules')
        """
        
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                
            configs = {row[0]: row[1] for row in rows}
            required = ['screening_thresholds', 'buy_decision_gates', 'position_sizing_rules']
            missing = [k for k in required if k not in configs]
            
            passed = len(missing) == 0
            
            status = "✅ PASS" if passed else "❌ FAIL"
            message = (
                f"{status} System Config: {len(configs)}/{len(required)} required configs present"
            )
            
            if not passed:
                self.results['recommendations'].append(
                    f"Add missing system configs: {', '.join(missing)}"
                )

            return passed, message, {
                'configs_present': list(configs.keys()),
                'missing_configs': missing
            }
            
        except Exception as e:
            return False, f"❌ ERROR checking system config: {e}", {}

    def check_vector_extension(self) -> Tuple[bool, str, Dict]:
        """Check if pgvector extension is enabled."""
        query = """
        SELECT EXISTS (
            SELECT 1 FROM pg_extension WHERE extname = 'vector'
        )
        """
        
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query)
                row = cursor.fetchone()
                
            enabled = row[0] if row else False
            
            status = "✅ PASS" if enabled else "❌ FAIL"
            message = f"{status} Vector Extension: {'Enabled' if enabled else 'Not enabled'}"
            
            if not enabled:
                self.results['recommendations'].append(
                    "Enable pgvector extension: CREATE EXTENSION vector;"
                )

            return enabled, message, {'enabled': enabled}
            
        except Exception as e:
            return False, f"❌ ERROR checking vector extension: {e}", {}

    def check_llm_tracking(self) -> Tuple[bool, str, Dict]:
        """Check if LLM tracking columns exist."""
        query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'analyses'
        AND column_name IN ('llm_prompts', 'llm_responses', 'llm_metadata')
        """
        
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                
            columns = [row[0] for row in rows]
            required = ['llm_prompts', 'llm_responses', 'llm_metadata']
            missing = [c for c in required if c not in columns]
            
            passed = len(missing) == 0
            
            status = "✅ PASS" if passed else "⚠️  WARN"
            message = (
                f"{status} LLM Tracking: {len(columns)}/{len(required)} columns present"
            )
            
            if not passed:
                self.results['recommendations'].append(
                    f"Run migration 013_add_llm_tracking.sql to add missing columns"
                )

            return passed, message, {
                'columns_present': columns,
                'missing_columns': missing
            }
            
        except Exception as e:
            return False, f"❌ ERROR checking LLM tracking: {e}", {}

    def validate_all(self) -> Dict:
        """Run all validation checks."""
        logger.info("="*80)
        logger.info("EDDIE DATABASE PREREQUISITES VALIDATION")
        logger.info("="*80)
        logger.info("")

        checks = [
            ("Tickers", self.check_tickers),
            ("Price Cache", self.check_price_cache),
            ("Daily Scans", self.check_daily_scans),
            ("Analyses", self.check_analyses),
            ("System Config", self.check_system_config),
            ("Vector Extension", self.check_vector_extension),
            ("LLM Tracking", self.check_llm_tracking),
        ]

        passed_count = 0
        total_count = 0

        for name, check_func in checks:
            logger.info(f"Checking {name}...")
            passed, message, details = check_func()
            logger.info(f"  {message}")
            
            self.results['checks'][name] = {
                'passed': passed,
                'message': message,
                'details': details
            }
            
            if passed:
                passed_count += 1
            total_count += 1
            logger.info("")

        # Calculate overall status
        critical_checks = ['Tickers', 'Price Cache', 'Daily Scans', 'System Config', 'Vector Extension']
        critical_passed = sum(
            1 for name in critical_checks 
            if self.results['checks'][name]['passed']
        )
        
        if critical_passed == len(critical_checks):
            self.results['overall_status'] = 'READY'
        elif critical_passed >= len(critical_checks) * 0.8:
            self.results['overall_status'] = 'PARTIAL'
        else:
            self.results['overall_status'] = 'NOT_READY'

        # Print summary
        logger.info("="*80)
        logger.info("VALIDATION SUMMARY")
        logger.info("="*80)
        logger.info(f"Overall Status: {self.results['overall_status']}")
        logger.info(f"Checks Passed: {passed_count}/{total_count}")
        logger.info("")

        if self.results['recommendations']:
            logger.info("RECOMMENDATIONS:")
            for i, rec in enumerate(self.results['recommendations'], 1):
                logger.info(f"  {i}. {rec}")
            logger.info("")

        # Status-specific messages
        if self.results['overall_status'] == 'READY':
            logger.info("✅ Eddie is ready for trading strategies and prompt decisions!")
            logger.info("")
            logger.info("Next steps:")
            logger.info("  1. Test Eddie: Ask 'What data do you have?'")
            logger.info("  2. Run analysis: Ask 'Should I buy AAPL?'")
            logger.info("  3. Monitor freshness: Use dashboard regularly")
        elif self.results['overall_status'] == 'PARTIAL':
            logger.info("⚠️  Eddie is partially ready. Some features may be limited.")
            logger.info("")
            logger.info("Fix the issues above, then re-run validation.")
        else:
            logger.info("❌ Eddie is NOT ready. Critical prerequisites missing.")
            logger.info("")
            logger.info("Please fix the issues above before using Eddie for trading decisions.")

        return self.results


def main():
    """Run validation."""
    try:
        validator = EddiePrerequisitesValidator()
        results = validator.validate_all()
        
        # Return exit code based on status
        if results['overall_status'] == 'READY':
            return 0
        elif results['overall_status'] == 'PARTIAL':
            return 1
        else:
            return 2
            
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        return 3


if __name__ == "__main__":
    exit(main())

