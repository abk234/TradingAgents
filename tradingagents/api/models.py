# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(BaseModel):
    role: Role
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Message] = []
    conversation_id: Optional[str] = None
    prompt_type: Optional[str] = None  # Category: quick_wins, analysis, risk, market
    prompt_id: Optional[str] = None    # Specific prompt identifier

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

class AnalysisRequest(BaseModel):
    ticker: str
    risk_level: str = "Moderate"
    investment_style: str = "Growth"

class AnalysisResponse(BaseModel):
    ticker: str
    decision: str
    confidence: int
    summary: str
    details: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)

class FeedbackRequest(BaseModel):
    conversation_id: str
    message_id: Optional[str] = None
    rating: int = Field(..., ge=1, le=5) # 1-5 stars
    comment: Optional[str] = None
    correction: Optional[str] = None # User provided correction

class UserPreference(BaseModel):
    risk_tolerance: str
    investment_horizon: str
    favorite_sectors: List[str] = []
    excluded_sectors: List[str] = []

class TickerCreate(BaseModel):
    symbol: str
    company_name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[int] = None
    priority_tier: int = 1
    tags: List[str] = []
    notes: Optional[str] = None

class TickerUpdate(BaseModel):
    company_name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[int] = None
    priority_tier: Optional[int] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    active: Optional[bool] = None
