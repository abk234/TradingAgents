# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

import logging
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from .connection import get_db_connection, DatabaseConnection

logger = logging.getLogger(__name__)

class LearningOperations:
    """
    Operations for storing and retrieving user interactions and preferences
    to enable the agent to learn and adapt.
    """

    def __init__(self, db: Optional[DatabaseConnection] = None):
        self.db = db or get_db_connection()
        self._ensure_tables_exist()

    def _ensure_tables_exist(self):
        """Create necessary tables if they don't exist."""
        try:
            # User Interactions Table
            # Stores chat history and embeddings for "memory"
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS user_interactions (
                    interaction_id SERIAL PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL, -- 'user' or 'assistant'
                    content TEXT NOT NULL,
                    embedding vector(1536), -- OpenAI embedding dimension
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    feedback_rating INTEGER, -- 1-5
                    feedback_comment TEXT,
                    correction TEXT, -- User provided correction
                    prompt_type TEXT, -- Category: quick_wins, analysis, risk, market
                    prompt_id TEXT -- Specific prompt identifier
                );
            """, fetch=False)
            
            # Add prompt metadata columns if they don't exist (for existing tables)
            try:
                self.db.execute_query("""
                    ALTER TABLE user_interactions 
                    ADD COLUMN IF NOT EXISTS prompt_type TEXT,
                    ADD COLUMN IF NOT EXISTS prompt_id TEXT;
                """, fetch=False)
                
                # Create indexes for prompt analytics
                self.db.execute_query("""
                    CREATE INDEX IF NOT EXISTS idx_interactions_prompt_type 
                    ON user_interactions(prompt_type);
                """, fetch=False)
                self.db.execute_query("""
                    CREATE INDEX IF NOT EXISTS idx_interactions_prompt_id 
                    ON user_interactions(prompt_id);
                """, fetch=False)
                self.db.execute_query("""
                    CREATE INDEX IF NOT EXISTS idx_interactions_prompt_feedback 
                    ON user_interactions(prompt_type, prompt_id, feedback_rating) 
                    WHERE prompt_type IS NOT NULL AND feedback_rating IS NOT NULL;
                """, fetch=False)
            except Exception as e:
                logger.warning(f"Could not add prompt metadata columns (may already exist): {e}")
            
            # Create index for vector search
            # Note: Requires pgvector extension which should be enabled
            try:
                self.db.execute_query("""
                    CREATE INDEX IF NOT EXISTS idx_interactions_embedding 
                    ON user_interactions 
                    USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100);
                """, fetch=False)
            except Exception as e:
                logger.warning(f"Could not create vector index (pgvector might not be fully setup): {e}")

            # User Preferences Table
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT NOT NULL,
                    pref_key TEXT NOT NULL,
                    pref_value JSONB NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, pref_key)
                );
            """, fetch=False)
            
            logger.info("✓ Learning tables initialized")
            
        except Exception as e:
            logger.error(f"Error initializing learning tables: {e}")

    def log_interaction(
        self, 
        conversation_id: str, 
        role: str, 
        content: str, 
        embedding: List[float] = None,
        prompt_type: Optional[str] = None,
        prompt_id: Optional[str] = None
    ) -> int:
        """
        Log a chat interaction with optional prompt metadata.
        
        Args:
            conversation_id: Unique conversation identifier
            role: 'user' or 'assistant'
            content: Message content
            embedding: Optional vector embedding for semantic search
            prompt_type: Optional prompt category (quick_wins, analysis, risk, market)
            prompt_id: Optional specific prompt identifier
        """
        data = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content
        }
        
        # Add prompt metadata if provided
        if prompt_type:
            data["prompt_type"] = prompt_type
        if prompt_id:
            data["prompt_id"] = prompt_id
        
        # Handle embedding insertion manually since it needs casting
        if embedding:
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'
            # Build query with prompt fields if provided
            prompt_fields = ""
            prompt_values = []
            if prompt_type:
                prompt_fields += ", prompt_type"
                prompt_values.append(prompt_type)
            if prompt_id:
                prompt_fields += ", prompt_id"
                prompt_values.append(prompt_id)
                
            query = f"""
                INSERT INTO user_interactions (conversation_id, role, content, embedding{prompt_fields})
                VALUES (%s, %s, %s, %s::vector{', %s' * len(prompt_values) if prompt_values else ''})
                RETURNING interaction_id
            """
            params = [conversation_id, role, content, embedding_str] + prompt_values
            result = self.db.execute_query(query, tuple(params), fetch_one=True)
            return result[0] if result else None
        else:
            return self.db.insert("user_interactions", data, returning="interaction_id")

    def add_feedback(
        self, 
        interaction_id: int, 
        rating: int, 
        comment: str = None,
        correction: str = None
    ):
        """
        Add user feedback to an interaction.
        """
        data = {"feedback_rating": rating}
        if comment:
            data["feedback_comment"] = comment
        if correction:
            data["correction"] = correction
            
        self.db.update(
            "user_interactions",
            data,
            where={"interaction_id": interaction_id}
        )

    def get_relevant_history(
        self, 
        query_embedding: List[float], 
        limit: int = 3,
        min_rating: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Find similar past interactions that had positive feedback.
        This is used for "Few-Shot" learning - showing the model what it did right before.
        """
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        query = """
            SELECT 
                content, 
                correction,
                feedback_rating,
                1 - (embedding <=> %s::vector) as similarity
            FROM user_interactions
            WHERE role = 'assistant'
              AND embedding IS NOT NULL
              AND (feedback_rating >= %s OR correction IS NOT NULL)
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        
        return self.db.execute_dict_query(
            query, 
            (embedding_str, min_rating, embedding_str, limit)
        ) or []

    def set_user_preference(self, user_id: str, key: str, value: Any):
        """
        Set a user preference.
        """
        query = """
            INSERT INTO user_preferences (user_id, pref_key, pref_value, updated_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id, pref_key) 
            DO UPDATE SET pref_value = EXCLUDED.pref_value, updated_at = CURRENT_TIMESTAMP
        """
        self.db.execute_query(query, (user_id, key, json.dumps(value)), fetch=False)

    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get all preferences for a user.
        """
        query = "SELECT pref_key, pref_value FROM user_preferences WHERE user_id = %s"
        results = self.db.execute_dict_query(query, (user_id,))
        
        if not results:
            return {}
            
        return {row['pref_key']: row['pref_value'] for row in results}
    
    def get_prompt_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get analytics on prompt usage and performance.
        
        Args:
            days: Number of days to look back (default: 30)
            
        Returns:
            Dictionary with:
            - most_used_prompts: List of prompts sorted by usage count
            - category_usage: Usage count by category
            - average_ratings: Average feedback rating per prompt
            - success_rate: Percentage of prompts with positive feedback (>=4)
        """
        # Most used prompts
        most_used_query = """
            SELECT 
                prompt_id,
                prompt_type,
                COUNT(*) as usage_count,
                AVG(feedback_rating) FILTER (WHERE feedback_rating IS NOT NULL) as avg_rating,
                COUNT(*) FILTER (WHERE feedback_rating >= 4) as positive_feedback_count,
                COUNT(*) FILTER (WHERE feedback_rating IS NOT NULL) as total_feedback_count
            FROM user_interactions
            WHERE prompt_id IS NOT NULL
              AND role = 'user'
              AND timestamp >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY prompt_id, prompt_type
            ORDER BY usage_count DESC
        """
        most_used = self.db.execute_dict_query(most_used_query, (days,)) or []
        
        # Category usage
        category_query = """
            SELECT 
                prompt_type,
                COUNT(*) as usage_count,
                AVG(feedback_rating) FILTER (WHERE feedback_rating IS NOT NULL) as avg_rating
            FROM user_interactions
            WHERE prompt_type IS NOT NULL
              AND role = 'user'
              AND timestamp >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY prompt_type
            ORDER BY usage_count DESC
        """
        category_usage = self.db.execute_dict_query(category_query, (days,)) or []
        
        # Calculate success rates
        for prompt in most_used:
            if prompt.get('total_feedback_count', 0) > 0:
                prompt['success_rate'] = (
                    prompt.get('positive_feedback_count', 0) / prompt['total_feedback_count'] * 100
                )
            else:
                prompt['success_rate'] = None
        
        return {
            "most_used_prompts": most_used,
            "category_usage": category_usage,
            "period_days": days,
            "total_prompt_interactions": sum(cat.get('usage_count', 0) for cat in category_usage)
        }
