"""
TodoList middleware for TradingAgents.

Provides task planning and progress tracking capabilities to agents.
"""

from typing import List, Dict, Any
from langchain_core.tools import tool, BaseTool
from .base import TradingMiddleware
from .todolist_storage import TodoListManager, TodoList
import logging

logger = logging.getLogger(__name__)

# Global todo manager (shared across middleware instances)
_todo_manager = TodoListManager()


def get_todo_manager() -> TodoListManager:
    """Get the global todo manager instance."""
    return _todo_manager


@tool
def write_todos(tasks: List[str], title: str = "Analysis Tasks") -> str:
    """
    Create a structured todo list for tracking progress through complex workflows.
    
    Use this when:
    - Starting a complex multi-step analysis
    - Need to track progress through a workflow
    - Coordinating multiple analysis steps
    - Planning a batch of analyses
    
    Do NOT use for:
    - Simple single-step queries
    - Quick lookups
    - Tasks that complete in < 10 seconds
    
    Args:
        tasks: List of task descriptions (e.g., ["Analyze NVDA", "Check fundamentals"])
        title: Optional title for the todo list
    
    Returns:
        Confirmation message with todo list ID
    """
    manager = get_todo_manager()
    
    # Extract context from current state if available
    # (This would be passed via middleware context in practice)
    context = {}
    
    todo_id = manager.create_todo_list(tasks, title, context)
    
    return f"✅ Created todo list '{title}' with {len(tasks)} tasks.\n\nTodo List ID: {todo_id}\n\nUse `read_todos()` to view progress."


@tool
def read_todos(todo_id: str = None) -> str:
    """
    Read current todo list and progress.
    
    Use this to:
    - Check progress on current tasks
    - See what's been completed
    - Review remaining work
    
    Args:
        todo_id: Optional specific todo list ID (if not provided, returns most recent)
    
    Returns:
        Formatted todo list with status and progress
    """
    manager = get_todo_manager()
    todo_list = manager.get_todo_list(todo_id)
    
    if not todo_list:
        return "No active todo list found. Use `write_todos()` to create one."
    
    return manager.format_todos(todo_list)


@tool
def mark_todo_complete(todo_id: str, item_index: int) -> str:
    """
    Mark a todo item as complete.
    
    Use this when you've finished a task to track progress.
    
    Args:
        todo_id: Todo list ID (use "current" for most recent)
        item_index: Index of the item to mark complete (1-based)
    
    Returns:
        Confirmation message
    """
    manager = get_todo_manager()
    
    # Handle "current" keyword
    if todo_id == "current" or not todo_id:
        todo_list = manager.get_todo_list()
        if not todo_list:
            return "No active todo list found."
        todo_id = todo_list.id
    else:
        todo_list = manager.get_todo_list(todo_id)
        if not todo_list:
            return f"Todo list not found: {todo_id}"
    
    # Convert 1-based index to 0-based
    if item_index < 1 or item_index > len(todo_list.items):
        return f"Invalid item index: {item_index}. Valid range: 1-{len(todo_list.items)}"
    
    item = todo_list.items[item_index - 1]
    item.mark_complete()
    
    progress = todo_list.get_progress()
    return f"✅ Marked task {item_index} as complete: {item.description}\n\nProgress: {progress['completed']}/{progress['total']} tasks completed ({progress['completion_percentage']}%)"


class TodoListMiddleware(TradingMiddleware):
    """
    Middleware for task planning and progress tracking.
    
    Provides todo list tools to agents for better workflow management.
    """
    
    def __init__(self):
        """Initialize todo list middleware."""
        self.manager = get_todo_manager()
        logger.info("Initialized TodoListMiddleware")
    
    @property
    def tools(self) -> List[BaseTool]:
        """Tools provided by this middleware."""
        return [write_todos, read_todos, mark_todo_complete]
    
    def modify_prompt(self, prompt: str, agent_type: str) -> str:
        """Add todo list instructions to prompt."""
        todo_instructions = """
        
## Task Planning Tools

You have access to task planning tools for managing complex workflows:
- `write_todos(tasks, title)`: Create a structured task list before starting complex work
- `read_todos(todo_id)`: Check current progress on tasks
- `mark_todo_complete(todo_id, item_index)`: Mark a task as complete when finished

**When to use todos:**
- Complex multi-step analyses (e.g., analyzing multiple stocks)
- Long-running workflows (e.g., daily screener)
- Tasks requiring coordination between agents
- Batch operations (e.g., analyzing top 5 stocks)

**When NOT to use todos:**
- Simple single-step queries
- Quick lookups
- Tasks that complete in < 10 seconds
- Single stock analysis (unless part of a batch)

**Example workflow:**
1. User asks: "Analyze NVDA, AAPL, and MSFT"
2. Create todos: `write_todos(["Analyze NVDA", "Analyze AAPL", "Analyze MSFT"], "Multi-Stock Analysis")`
3. Execute each task
4. Mark todos as complete: `mark_todo_complete("current", 1)` after each task
5. Check progress: `read_todos()` to see what's done

**Best Practices:**
- Create todos at the start of complex workflows
- Mark tasks complete as you finish them
- Use descriptive task names
- Check progress periodically with `read_todos()`
"""
        return prompt + todo_instructions
    
    def pre_process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """No pre-processing needed."""
        return state
    
    def post_process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store todo list state in agent state.
        
        Args:
            state: Current agent state
        
        Returns:
            State with todo list information added
        """
        # Store active todo list ID in state for reference
        active_todo = self.manager.get_todo_list()
        if active_todo:
            state["_active_todo_id"] = active_todo.id
            state["_todo_progress"] = active_todo.get_progress()
        
        return state

