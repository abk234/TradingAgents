"""
Todo list storage and data structures for TradingAgents.

Provides data structures for managing todo lists and tracking task progress.
"""

from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)


class TodoStatus(Enum):
    """Status of a todo item."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class TodoItem:
    """Represents a single todo item."""
    id: str
    description: str
    status: TodoStatus = TodoStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)
    
    def mark_complete(self):
        """Mark this todo item as completed."""
        self.status = TodoStatus.COMPLETED
        self.completed_at = datetime.now()
    
    def mark_in_progress(self):
        """Mark this todo item as in progress."""
        self.status = TodoStatus.IN_PROGRESS
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata
        }


@dataclass
class TodoList:
    """Represents a todo list with multiple items."""
    id: str
    title: str
    items: List[TodoItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    context: Dict = field(default_factory=dict)  # Analysis ID, ticker, etc.
    
    def add_item(self, description: str, metadata: Dict = None) -> TodoItem:
        """Add a new item to the todo list."""
        item = TodoItem(
            id=str(uuid.uuid4()),
            description=description,
            metadata=metadata or {}
        )
        self.items.append(item)
        return item
    
    def get_item(self, item_id: str) -> Optional[TodoItem]:
        """Get an item by ID."""
        for item in self.items:
            if item.id == item_id:
                return item
        return None
    
    def mark_complete(self, item_id: str) -> bool:
        """Mark an item as complete."""
        item = self.get_item(item_id)
        if item:
            item.mark_complete()
            return True
        return False
    
    def get_progress(self) -> Dict[str, int]:
        """Get progress statistics."""
        total = len(self.items)
        completed = sum(1 for item in self.items if item.status == TodoStatus.COMPLETED)
        pending = sum(1 for item in self.items if item.status == TodoStatus.PENDING)
        in_progress = sum(1 for item in self.items if item.status == TodoStatus.IN_PROGRESS)
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "in_progress": in_progress,
            "completion_percentage": int((completed / total * 100)) if total > 0 else 0
        }
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "items": [item.to_dict() for item in self.items],
            "created_at": self.created_at.isoformat(),
            "context": self.context,
            "progress": self.get_progress()
        }


class TodoListManager:
    """Manages todo lists in agent state."""
    
    def __init__(self):
        """Initialize the todo list manager."""
        self.active_todos: Dict[str, TodoList] = {}
        logger.debug("Initialized TodoListManager")
    
    def create_todo_list(
        self, 
        tasks: List[str], 
        title: str = "Analysis Tasks",
        context: Dict = None
    ) -> str:
        """
        Create a new todo list.
        
        Args:
            tasks: List of task descriptions
            title: Title for the todo list
            context: Optional context (ticker, analysis_id, etc.)
        
        Returns:
            Todo list ID
        """
        todo_id = str(uuid.uuid4())
        items = [
            TodoItem(id=str(uuid.uuid4()), description=task)
            for task in tasks
        ]
        
        todo_list = TodoList(
            id=todo_id,
            title=title,
            items=items,
            context=context or {}
        )
        
        self.active_todos[todo_id] = todo_list
        logger.info(f"Created todo list '{title}' with {len(tasks)} tasks (ID: {todo_id})")
        return todo_id
    
    def get_todo_list(self, todo_id: str = None) -> Optional[TodoList]:
        """
        Get todo list (most recent if ID not provided).
        
        Args:
            todo_id: Optional specific todo list ID
        
        Returns:
            TodoList instance or None
        """
        if todo_id:
            return self.active_todos.get(todo_id)
        
        # Return most recent
        if self.active_todos:
            return max(self.active_todos.values(), key=lambda t: t.created_at)
        return None
    
    def mark_complete(self, todo_id: str, item_id: str) -> bool:
        """
        Mark a todo item as complete.
        
        Args:
            todo_id: Todo list ID
            item_id: Item ID to mark complete
        
        Returns:
            True if successful, False otherwise
        """
        todo_list = self.active_todos.get(todo_id)
        if not todo_list:
            return False
        
        return todo_list.mark_complete(item_id)
    
    def format_todos(self, todo_list: TodoList) -> str:
        """
        Format todos for display.
        
        Args:
            todo_list: TodoList instance
        
        Returns:
            Formatted string representation
        """
        lines = [f"📋 {todo_list.title}"]
        lines.append("=" * 60)
        
        for i, item in enumerate(todo_list.items, 1):
            status_icon = {
                TodoStatus.PENDING: "⏳",
                TodoStatus.IN_PROGRESS: "🔄",
                TodoStatus.COMPLETED: "✅",
                TodoStatus.CANCELLED: "❌"
            }.get(item.status, "❓")
            
            lines.append(f"{i}. {status_icon} {item.description}")
            if item.status == TodoStatus.COMPLETED and item.completed_at:
                lines.append(f"   ✓ Completed: {item.completed_at.strftime('%H:%M:%S')}")
        
        progress = todo_list.get_progress()
        lines.append("")
        lines.append(f"Progress: {progress['completed']}/{progress['total']} tasks completed ({progress['completion_percentage']}%)")
        
        if todo_list.context:
            context_str = ", ".join(f"{k}={v}" for k, v in todo_list.context.items())
            lines.append(f"Context: {context_str}")
        
        return "\n".join(lines)
    
    def clear_completed(self, todo_id: str):
        """Clear completed todos (for cleanup)."""
        todo_list = self.active_todos.get(todo_id)
        if todo_list:
            todo_list.items = [
                item for item in todo_list.items 
                if item.status != TodoStatus.COMPLETED
            ]

