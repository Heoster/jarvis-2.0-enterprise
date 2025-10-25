"""Permission and consent management system."""

import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime, timedelta
import asyncio

from core.logger import get_logger

logger = get_logger(__name__)


class PermissionType(Enum):
    """Types of permissions."""
    MONITOR_WEB = "monitor_web"
    MONITOR_APPS = "monitor_apps"
    CONTROL_DEVICE = "control_device"
    CONTROL_BROWSER = "control_browser"
    ACCESS_MEMORY = "access_memory"
    CALL_APIS = "call_apis"
    UPLOAD_DATA = "upload_data"


class RiskLevel(Enum):
    """Risk levels for actions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConsentManager:
    """Manages permissions and consent for assistant actions."""
    
    def __init__(self, db_path: str = "data/permissions.db"):
        """
        Initialize consent manager.
        
        Args:
            db_path: Path to permissions database
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Cooldown tracking for high-risk actions
        self.cooldowns: Dict[str, datetime] = {}
        
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize permissions database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS permissions (
                permission_type TEXT PRIMARY KEY,
                granted BOOLEAN DEFAULT 0,
                granted_at TIMESTAMP,
                expires_at TIMESTAMP,
                scope TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS permission_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                permission_type TEXT,
                action TEXT,
                granted BOOLEAN,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("Consent manager initialized")
    
    async def request_permission(
        self,
        permission_type: PermissionType,
        reason: str,
        scope: Optional[str] = None,
        duration_days: Optional[int] = None
    ) -> bool:
        """
        Request permission from user.
        
        Args:
            permission_type: Type of permission
            reason: Reason for requesting permission
            scope: Optional scope limitation
            duration_days: Permission duration in days
            
        Returns:
            True if granted
        """
        # Check if already granted
        if await self.check_permission(permission_type):
            return True
        
        # In a real implementation, this would show a UI prompt
        # For now, we'll log the request
        logger.info(f"Permission requested: {permission_type.value} - {reason}")
        
        # Store permission request
        await asyncio.to_thread(
            self._store_permission_sync,
            permission_type,
            granted=False,  # Default to not granted
            scope=scope,
            duration_days=duration_days
        )
        
        return False
    
    def _store_permission_sync(
        self,
        permission_type: PermissionType,
        granted: bool,
        scope: Optional[str],
        duration_days: Optional[int]
    ) -> None:
        """Store permission in database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        now = datetime.utcnow()
        expires_at = now + timedelta(days=duration_days) if duration_days else None
        
        cursor.execute("""
            INSERT INTO permissions (permission_type, granted, granted_at, expires_at, scope)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(permission_type) DO UPDATE SET
                granted = excluded.granted,
                granted_at = excluded.granted_at,
                expires_at = excluded.expires_at,
                scope = excluded.scope
        """, (permission_type.value, granted, now, expires_at, scope))
        
        # Log the request
        cursor.execute("""
            INSERT INTO permission_log (permission_type, action, granted)
            VALUES (?, ?, ?)
        """, (permission_type.value, 'request', granted))
        
        conn.commit()
        conn.close()
    
    async def check_permission(self, permission_type: PermissionType) -> bool:
        """
        Check if permission is granted.
        
        Args:
            permission_type: Type of permission
            
        Returns:
            True if granted and not expired
        """
        return await asyncio.to_thread(self._check_permission_sync, permission_type)
    
    def _check_permission_sync(self, permission_type: PermissionType) -> bool:
        """Synchronous permission check."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT granted, expires_at FROM permissions
            WHERE permission_type = ?
        """, (permission_type.value,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row or not row[0]:
            return False
        
        # Check expiration
        if row[1]:
            expires_at = datetime.fromisoformat(row[1])
            if datetime.utcnow() > expires_at:
                return False
        
        return True
    
    async def revoke_permission(self, permission_type: PermissionType) -> None:
        """
        Revoke a permission.
        
        Args:
            permission_type: Type of permission to revoke
        """
        await asyncio.to_thread(self._revoke_permission_sync, permission_type)
    
    def _revoke_permission_sync(self, permission_type: PermissionType) -> None:
        """Synchronous permission revocation."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE permissions
            SET granted = 0
            WHERE permission_type = ?
        """, (permission_type.value,))
        
        # Log revocation
        cursor.execute("""
            INSERT INTO permission_log (permission_type, action, granted)
            VALUES (?, ?, ?)
        """, (permission_type.value, 'revoke', False))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Permission revoked: {permission_type.value}")
    
    def classify_risk(self, action_type: str, parameters: Dict[str, Any]) -> RiskLevel:
        """
        Classify risk level of an action.
        
        Args:
            action_type: Type of action
            parameters: Action parameters
            
        Returns:
            Risk level
        """
        # High-risk actions
        high_risk_actions = [
            'delete', 'remove', 'shutdown', 'restart', 'format',
            'install', 'uninstall', 'execute', 'run'
        ]
        
        # Critical actions
        critical_actions = [
            'format', 'delete_all', 'factory_reset'
        ]
        
        action_lower = action_type.lower()
        
        # Check for critical
        if any(crit in action_lower for crit in critical_actions):
            return RiskLevel.CRITICAL
        
        # Check for high risk
        if any(high in action_lower for high in high_risk_actions):
            return RiskLevel.HIGH
        
        # Check parameters for sensitive data
        if 'password' in str(parameters).lower() or 'token' in str(parameters).lower():
            return RiskLevel.HIGH
        
        # Medium risk for control actions
        if 'control' in action_type.lower():
            return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    async def require_confirmation(
        self,
        action_type: str,
        parameters: Dict[str, Any]
    ) -> bool:
        """
        Check if action requires user confirmation.
        
        Args:
            action_type: Type of action
            parameters: Action parameters
            
        Returns:
            True if confirmation required
        """
        risk_level = self.classify_risk(action_type, parameters)
        
        # High and critical always require confirmation
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            # Check cooldown
            if await self._check_cooldown(action_type):
                return True
            
            return True
        
        return False
    
    async def _check_cooldown(self, action_type: str) -> bool:
        """Check if action is in cooldown period."""
        if action_type in self.cooldowns:
            last_time = self.cooldowns[action_type]
            cooldown_seconds = 5  # 5 second cooldown
            
            if (datetime.utcnow() - last_time).total_seconds() < cooldown_seconds:
                return True
        
        # Update cooldown
        self.cooldowns[action_type] = datetime.utcnow()
        return False
    
    async def get_all_permissions(self) -> List[Dict[str, Any]]:
        """
        Get all permissions and their status.
        
        Returns:
            List of permission dictionaries
        """
        return await asyncio.to_thread(self._get_all_permissions_sync)
    
    def _get_all_permissions_sync(self) -> List[Dict[str, Any]]:
        """Synchronous get all permissions."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM permissions")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
