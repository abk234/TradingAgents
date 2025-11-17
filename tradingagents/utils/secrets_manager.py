"""
Secrets management with rotation support
"""
import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class APIKey:
    """API key with metadata"""
    key: str
    service: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    rotation_days: int = 90


class SecretsManager:
    """Manage API keys with rotation support"""
    
    def __init__(self, app_name: str = "tradingagents"):
        self.app_name = app_name
        self.cache_file = Path.home() / ".tradingagents" / "key_metadata.json"
        self.cache_file.parent.mkdir(exist_ok=True)
        self._metadata: Dict[str, dict] = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, dict]:
        """Load key metadata from cache"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load key metadata: {e}")
        return {}
    
    def _save_metadata(self):
        """Save key metadata to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self._metadata, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Could not save key metadata: {e}")
    
    def set_key(
        self,
        service: str,
        key: str,
        rotation_days: int = 90,
        use_keyring: bool = True
    ):
        """
        Store API key securely
        
        Args:
            service: Service name (e.g., 'openai', 'alpha_vantage')
            key: API key value
            rotation_days: Days until key should be rotated
            use_keyring: Use system keyring (more secure) vs env var
        """
        if use_keyring:
            try:
                import keyring
                keyring.set_password(self.app_name, service, key)
                logger.info(f"Stored {service} key in system keyring")
            except ImportError:
                logger.warning("keyring not installed, falling back to env vars")
                use_keyring = False
            except Exception as e:
                logger.warning(f"Could not store in keyring: {e}, falling back to env")
                use_keyring = False
        
        # Store metadata
        self._metadata[service] = {
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=rotation_days)).isoformat(),
            'rotation_days': rotation_days,
            'uses_keyring': use_keyring
        }
        self._save_metadata()
    
    def get_key(self, service: str) -> Optional[str]:
        """
        Get API key for service
        
        Priority:
        1. System keyring (if configured)
        2. Environment variable
        
        Args:
            service: Service name (e.g., 'openai', 'alpha_vantage')
        
        Returns:
            API key or None if not found
        """
        # Check if key needs rotation
        if self._should_rotate(service):
            logger.warning(f"⚠️  API key for {service} should be rotated!")
        
        metadata = self._metadata.get(service, {})
        uses_keyring = metadata.get('uses_keyring', False)
        
        # Try keyring first
        if uses_keyring:
            try:
                import keyring
                key = keyring.get_password(self.app_name, service)
                if key:
                    return key
            except ImportError:
                logger.debug("keyring not installed")
            except Exception as e:
                logger.debug(f"Could not get {service} from keyring: {e}")
        
        # Fall back to environment variable
        env_var = f"{service.upper()}_API_KEY"
        key = os.getenv(env_var)
        if key:
            return key
        
        # Try alternative env var names
        alt_names = {
            'alpha_vantage': 'ALPHA_VANTAGE_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'google': 'GOOGLE_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
        }
        
        if service in alt_names:
            return os.getenv(alt_names[service])
        
        return None
    
    def _should_rotate(self, service: str) -> bool:
        """Check if key should be rotated"""
        metadata = self._metadata.get(service)
        if not metadata or not metadata.get('expires_at'):
            return False
        
        try:
            expires_at = datetime.fromisoformat(metadata['expires_at'])
            return datetime.now() >= expires_at
        except (ValueError, TypeError):
            return False
    
    def rotate_key(self, service: str, new_key: str):
        """
        Rotate API key for service
        
        Args:
            service: Service name
            new_key: New API key value
        """
        old_metadata = self._metadata.get(service, {})
        rotation_days = old_metadata.get('rotation_days', 90)
        use_keyring = old_metadata.get('uses_keyring', True)
        
        logger.info(f"Rotating API key for {service}")
        self.set_key(service, new_key, rotation_days, use_keyring)
    
    def list_keys(self) -> Dict[str, dict]:
        """List all managed keys with status"""
        result = {}
        for service, metadata in self._metadata.items():
            expires_at_str = metadata.get('expires_at')
            if expires_at_str:
                try:
                    expires_at = datetime.fromisoformat(expires_at_str)
                    days_until_expiry = (expires_at - datetime.now()).days
                except (ValueError, TypeError):
                    days_until_expiry = None
            else:
                days_until_expiry = None
            
            result[service] = {
                'service': service,
                'created_at': metadata.get('created_at', 'Unknown'),
                'expires_at': expires_at_str or 'Never',
                'days_until_expiry': days_until_expiry,
                'needs_rotation': days_until_expiry is not None and days_until_expiry <= 0,
                'uses_keyring': metadata.get('uses_keyring', False)
            }
        
        return result


# Global instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """Get or create global secrets manager"""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


def get_api_key(service: str) -> Optional[str]:
    """
    Convenience function to get API key
    
    Usage:
        from tradingagents.utils.secrets_manager import get_api_key
        
        openai_key = get_api_key('openai')
        alpha_vantage_key = get_api_key('alpha_vantage')
    """
    return get_secrets_manager().get_key(service)

