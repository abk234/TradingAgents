# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Document Database Operations

Handles database operations for document storage and retrieval.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import json

from .connection import DatabaseConnection, get_db_connection

logger = logging.getLogger(__name__)


class DocumentOperations:
    """Database operations for documents"""
    
    def __init__(self, db: Optional[DatabaseConnection] = None):
        self.db = db or get_db_connection()
    
    def add_document(
        self,
        filename: str,
        original_filename: str,
        document_type: str,
        file_size_bytes: int,
        ticker_id: Optional[int] = None,
        workspace_id: Optional[int] = None,
        mime_type: Optional[str] = None,
        storage_path: Optional[str] = None,
        uploaded_by: Optional[str] = None
    ) -> int:
        """
        Add a new document record.
        
        Returns:
            document_id
        """
        query = """
            INSERT INTO documents (
                ticker_id, workspace_id, filename, original_filename,
                document_type, mime_type, file_size_bytes,
                storage_path, uploaded_by, processing_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
            RETURNING document_id
        """
        
        result = self.db.execute_query(
            query,
            (
                ticker_id, workspace_id, filename, original_filename,
                document_type, mime_type, file_size_bytes,
                storage_path, uploaded_by
            )
        )
        
        return result[0][0] if result else None
    
    def update_document_processing(
        self,
        document_id: int,
        text_content: Optional[str] = None,
        financial_data: Optional[Dict[str, Any]] = None,
        summary: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None,
        status: str = 'completed',
        error: Optional[str] = None
    ) -> bool:
        """Update document with processing results"""
        query = """
            UPDATE documents
            SET
                text_content = COALESCE(%s, text_content),
                financial_data = COALESCE(%s, financial_data),
                summary = COALESCE(%s, summary),
                embedding = COALESCE(%s::vector, embedding),
                processing_status = %s,
                processing_error = COALESCE(%s, processing_error),
                processed_at = CASE WHEN %s = 'completed' THEN CURRENT_TIMESTAMP ELSE processed_at END,
                updated_at = CURRENT_TIMESTAMP
            WHERE document_id = %s
        """
        
        financial_data_json = json.dumps(financial_data) if financial_data else None
        summary_json = json.dumps(summary) if summary else None
        
        self.db.execute_query(
            query,
            (
                text_content,
                financial_data_json,
                summary_json,
                str(embedding) if embedding else None,
                status,
                error,
                status,
                document_id
            )
        )
        
        return True
    
    def get_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        query = """
            SELECT
                document_id, ticker_id, workspace_id,
                filename, original_filename, document_type,
                mime_type, file_size_bytes,
                processing_status, processing_error,
                text_content, financial_data, summary,
                storage_path, storage_type,
                uploaded_by, uploaded_at, processed_at, updated_at
            FROM documents
            WHERE document_id = %s
        """
        
        result = self.db.execute_dict_query(query, (document_id,), fetch_one=True)
        return result
    
    def list_documents(
        self,
        ticker_id: Optional[int] = None,
        workspace_id: Optional[int] = None,
        document_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List documents with filters"""
        conditions = []
        params = []
        
        if ticker_id:
            conditions.append("ticker_id = %s")
            params.append(ticker_id)
        
        if workspace_id:
            conditions.append("workspace_id = %s")
            params.append(workspace_id)
        
        if document_type:
            conditions.append("document_type = %s")
            params.append(document_type)
        
        if status:
            conditions.append("processing_status = %s")
            params.append(status)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
            SELECT
                document_id, ticker_id, workspace_id,
                filename, original_filename, document_type,
                file_size_bytes, processing_status,
                summary, uploaded_at, processed_at
            FROM documents
            WHERE {where_clause}
            ORDER BY uploaded_at DESC
            LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        return self.db.execute_dict_query(query, tuple(params)) or []
    
    def add_document_insight(
        self,
        document_id: int,
        analysis_id: int,
        ticker_id: int,
        insight_type: str,
        insight_value: str,
        confidence_score: float = 1.0,
        extracted_from_section: Optional[str] = None,
        relevance_score: float = 1.0
    ) -> int:
        """Add a document insight linking to an analysis"""
        query = """
            INSERT INTO document_insights (
                document_id, analysis_id, ticker_id,
                insight_type, insight_value, confidence_score,
                extracted_from_section, relevance_score
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING insight_id
        """
        
        result = self.db.execute_query(
            query,
            (
                document_id, analysis_id, ticker_id,
                insight_type, insight_value, confidence_score,
                extracted_from_section, relevance_score
            )
        )
        
        return result[0][0] if result else None
    
    def get_document_insights(
        self,
        analysis_id: Optional[int] = None,
        document_id: Optional[int] = None,
        ticker_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get document insights"""
        conditions = []
        params = []
        
        if analysis_id:
            conditions.append("di.analysis_id = %s")
            params.append(analysis_id)
        
        if document_id:
            conditions.append("di.document_id = %s")
            params.append(document_id)
        
        if ticker_id:
            conditions.append("di.ticker_id = %s")
            params.append(ticker_id)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
            SELECT
                di.insight_id, di.document_id, di.analysis_id, di.ticker_id,
                di.insight_type, di.insight_value, di.confidence_score,
                di.extracted_from_section, di.relevance_score,
                d.filename, d.original_filename
            FROM document_insights di
            JOIN documents d ON di.document_id = d.document_id
            WHERE {where_clause}
            ORDER BY di.relevance_score DESC, di.created_at DESC
        """
        
        return self.db.execute_dict_query(query, tuple(params)) or []
    
    def delete_document(self, document_id: int) -> bool:
        """Delete a document"""
        query = "DELETE FROM documents WHERE document_id = %s"
        self.db.execute_query(query, (document_id,))
        return True

