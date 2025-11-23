# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Workspace Database Operations

Handles database operations for workspace management.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import json

from .connection import DatabaseConnection, get_db_connection

logger = logging.getLogger(__name__)


class WorkspaceOperations:
    """Database operations for workspaces"""
    
    def __init__(self, db: Optional[DatabaseConnection] = None):
        self.db = db or get_db_connection()
    
    def create_workspace(
        self,
        name: str,
        description: Optional[str] = None,
        default_ticker_list: Optional[List[int]] = None,
        analysis_preferences: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None,
        is_default: bool = False
    ) -> int:
        """
        Create a new workspace.
        
        Returns:
            workspace_id
        """
        # If setting as default, unset other defaults
        if is_default:
            self.db.execute_query(
                "UPDATE workspaces SET is_default = false WHERE is_default = true"
            )
        
        query = """
            INSERT INTO workspaces (
                name, description, default_ticker_list,
                analysis_preferences, created_by, is_default
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING workspace_id
        """
        
        analysis_prefs_json = json.dumps(analysis_preferences) if analysis_preferences else None
        
        result = self.db.execute_query(
            query,
            (
                name, description, default_ticker_list,
                analysis_prefs_json, created_by, is_default
            )
        )
        
        return result[0][0] if result else None
    
    def get_workspace(self, workspace_id: int) -> Optional[Dict[str, Any]]:
        """Get workspace by ID"""
        query = """
            SELECT
                workspace_id, name, description,
                default_ticker_list, analysis_preferences,
                created_by, created_at, updated_at,
                is_default, is_active
            FROM workspaces
            WHERE workspace_id = %s
        """
        
        result = self.db.execute_dict_query(query, (workspace_id,), fetch_one=True)
        return result
    
    def get_default_workspace(self) -> Optional[Dict[str, Any]]:
        """Get the default workspace"""
        query = """
            SELECT
                workspace_id, name, description,
                default_ticker_list, analysis_preferences,
                created_by, created_at, updated_at,
                is_default, is_active
            FROM workspaces
            WHERE is_default = true AND is_active = true
            LIMIT 1
        """
        
        result = self.db.execute_dict_query(query, fetch_one=True)
        return result
    
    def list_workspaces(
        self,
        active_only: bool = True,
        include_default: bool = True
    ) -> List[Dict[str, Any]]:
        """List all workspaces"""
        conditions = []
        params = []
        
        if active_only:
            conditions.append("is_active = true")
        
        if not include_default:
            conditions.append("is_default = false")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
            SELECT
                workspace_id, name, description,
                is_default, is_active,
                created_at, updated_at
            FROM workspaces
            WHERE {where_clause}
            ORDER BY is_default DESC, created_at DESC
        """
        
        return self.db.execute_dict_query(query, tuple(params)) or []
    
    def update_workspace(
        self,
        workspace_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        default_ticker_list: Optional[List[int]] = None,
        analysis_preferences: Optional[Dict[str, Any]] = None,
        is_default: Optional[bool] = None,
        is_active: Optional[bool] = None
    ) -> bool:
        """Update workspace"""
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = %s")
            params.append(name)
        
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        
        if default_ticker_list is not None:
            updates.append("default_ticker_list = %s")
            params.append(default_ticker_list)
        
        if analysis_preferences is not None:
            updates.append("analysis_preferences = %s")
            params.append(json.dumps(analysis_preferences))
        
        if is_default is not None:
            # If setting as default, unset other defaults
            if is_default:
                self.db.execute_query(
                    "UPDATE workspaces SET is_default = false WHERE is_default = true AND workspace_id != %s",
                    (workspace_id,)
                )
            updates.append("is_default = %s")
            params.append(is_default)
        
        if is_active is not None:
            updates.append("is_active = %s")
            params.append(is_active)
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(workspace_id)
        
        query = f"""
            UPDATE workspaces
            SET {', '.join(updates)}
            WHERE workspace_id = %s
        """
        
        self.db.execute_query(query, tuple(params))
        return True
    
    def delete_workspace(self, workspace_id: int, soft_delete: bool = True) -> bool:
        """Delete workspace (soft delete by default)"""
        if soft_delete:
            query = "UPDATE workspaces SET is_active = false WHERE workspace_id = %s"
        else:
            query = "DELETE FROM workspaces WHERE workspace_id = %s"
        
        self.db.execute_query(query, (workspace_id,))
        return True
    
    def get_workspace_tickers(self, workspace_id: int) -> List[Dict[str, Any]]:
        """Get all tickers in a workspace"""
        query = """
            SELECT
                t.ticker_id, t.symbol, t.company_name,
                t.sector, t.industry, t.active
            FROM tickers t
            WHERE t.workspace_id = %s OR t.workspace_id IS NULL
            ORDER BY t.symbol
        """
        
        return self.db.execute_dict_query(query, (workspace_id,)) or []
    
    def get_workspace_analyses(
        self,
        workspace_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get analyses for a workspace"""
        query = """
            SELECT
                a.analysis_id, a.ticker_id, a.analysis_date,
                a.final_decision, a.confidence_score,
                a.executive_summary,
                t.symbol, t.company_name
            FROM analyses a
            JOIN tickers t ON a.ticker_id = t.ticker_id
            WHERE (a.workspace_id = %s OR a.workspace_id IS NULL)
            ORDER BY a.analysis_date DESC
            LIMIT %s OFFSET %s
        """
        
        return self.db.execute_dict_query(query, (workspace_id, limit, offset)) or []

