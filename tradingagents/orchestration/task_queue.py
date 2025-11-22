# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

import json
import redis
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TaskQueue:
    """
    Redis-based task queue for asynchronous agent execution.
    """
    
    def __init__(self, redis_host='localhost', redis_port=6379, db=0):
        try:
            self.redis = redis.Redis(host=redis_host, port=redis_port, db=db, decode_responses=True)
            self.redis.ping() # Check connection
            logger.info(f"✓ Connected to Redis at {redis_host}:{redis_port}")
            self.enabled = True
        except redis.ConnectionError:
            logger.warning(f"⚠ Could not connect to Redis at {redis_host}:{redis_port}. Async tasks disabled.")
            self.enabled = False
            
    def enqueue_task(self, task_type: str, payload: Dict[str, Any]) -> Optional[str]:
        """
        Enqueue a task for processing.
        
        Args:
            task_type: Type of task (e.g., 'analyze_stock', 'backtest')
            payload: Task arguments
            
        Returns:
            Task ID if successful, None otherwise
        """
        if not self.enabled:
            return None
            
        task_id = str(uuid.uuid4())
        task = {
            'id': task_id,
            'type': task_type,
            'payload': payload,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'result': None,
            'error': None
        }
        
        # Store task metadata
        self.redis.hset(f"task:{task_id}", mapping={k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in task.items()})
        
        # Push to queue
        self.redis.rpush("task_queue", task_id)
        
        logger.info(f"Enqueued task {task_id} ({task_type})")
        return task_id
        
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a task."""
        if not self.enabled:
            return {'status': 'failed', 'error': 'Redis not available'}
            
        task = self.redis.hgetall(f"task:{task_id}")
        if not task:
            return {'status': 'not_found'}
            
        # Parse JSON fields
        if 'payload' in task:
            task['payload'] = json.loads(task['payload'])
        if 'result' in task and task['result'] != 'None':
            task['result'] = json.loads(task['result'])
            
        return task
        
    def process_next_task(self, handler_func):
        """
        Process the next task in the queue using the provided handler.
        Blocking call (with timeout).
        """
        if not self.enabled:
            return
            
        # Pop from queue (blocking with 5s timeout)
        item = self.redis.blpop("task_queue", timeout=5)
        
        if not item:
            return # Queue empty
            
        _, task_id = item
        
        try:
            # Update status to running
            self.redis.hset(f"task:{task_id}", "status", "running")
            
            # Get task details
            task_data = self.get_task_status(task_id)
            
            logger.info(f"Processing task {task_id} ({task_data['type']})...")
            
            # Execute handler
            result = handler_func(task_data['type'], task_data['payload'])
            
            # Update status to completed
            self.redis.hset(f"task:{task_id}", mapping={
                "status": "completed",
                "result": json.dumps(result),
                "completed_at": datetime.now().isoformat()
            })
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            self.redis.hset(f"task:{task_id}", mapping={
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            })

# Global instance
_task_queue = None

def get_task_queue():
    global _task_queue
    if _task_queue is None:
        # In Docker, host is 'redis', locally it's 'localhost'
        import os
        host = os.getenv("REDIS_HOST", "localhost")
        _task_queue = TaskQueue(redis_host=host)
    return _task_queue
