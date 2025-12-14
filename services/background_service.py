"""
Background Task Service for NexusAI.
Handles non-blocking heavy operations like file processing and embedding generation.
"""

import logging
import threading
import queue
from typing import Callable, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import streamlit as st

logger = logging.getLogger("NexusAI.BackgroundTasks")


class TaskStatus(Enum):
    """Status of a background task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BackgroundTask:
    """Represents a background task."""
    task_id: str
    name: str
    status: TaskStatus
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Any = None
    error: Optional[str] = None
    progress: float = 0.0


class BackgroundTaskService:
    """
    Service for managing background tasks.
    Uses threading for non-blocking execution.
    """
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self._tasks: Dict[str, BackgroundTask] = {}
        self._task_queue = queue.Queue()
        self._workers = []
        self._running = False
    
    def start(self):
        """Start the background worker threads."""
        if self._running:
            return
        
        self._running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()
            self._workers.append(worker)
        
        logger.info(f"Started {self.max_workers} background workers")
    
    def stop(self):
        """Stop all background workers."""
        self._running = False
        for _ in self._workers:
            self._task_queue.put(None)  # Signal workers to stop
    
    def _worker_loop(self):
        """Main loop for worker threads."""
        while self._running:
            try:
                item = self._task_queue.get(timeout=1.0)
                if item is None:
                    break
                
                task_id, func, args, kwargs = item
                self._execute_task(task_id, func, args, kwargs)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}")
    
    def _execute_task(self, task_id: str, func: Callable, args: tuple, kwargs: dict):
        """Execute a background task."""
        task = self._tasks.get(task_id)
        if not task:
            return
        
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now().isoformat()
        
        try:
            result = func(*args, **kwargs)
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.progress = 1.0
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            logger.error(f"Task {task_id} failed: {e}")
        
        finally:
            task.completed_at = datetime.now().isoformat()
    
    def submit(
        self,
        task_id: str,
        name: str,
        func: Callable,
        *args,
        **kwargs
    ) -> BackgroundTask:
        """Submit a task for background execution."""
        task = BackgroundTask(
            task_id=task_id,
            name=name,
            status=TaskStatus.PENDING
        )
        
        self._tasks[task_id] = task
        self._task_queue.put((task_id, func, args, kwargs))
        
        logger.info(f"Submitted task: {task_id} ({name})")
        return task
    
    def get_task(self, task_id: str) -> Optional[BackgroundTask]:
        """Get a task by ID."""
        return self._tasks.get(task_id)
    
    def is_completed(self, task_id: str) -> bool:
        """Check if a task is completed."""
        task = self._tasks.get(task_id)
        return task and task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED)
    
    def get_all_tasks(self) -> Dict[str, BackgroundTask]:
        """Get all tasks."""
        return self._tasks.copy()
    
    def clear_completed(self):
        """Remove completed tasks from memory."""
        self._tasks = {
            k: v for k, v in self._tasks.items()
            if v.status not in (TaskStatus.COMPLETED, TaskStatus.FAILED)
        }


# =============================================================================
# HIGH-LEVEL TASK FUNCTIONS
# =============================================================================

def process_files_background(files: list, rag_service) -> int:
    """
    Process files for RAG indexing in background.
    
    Args:
        files: List of file dicts with name and content
        rag_service: RAG service for indexing
        
    Returns:
        Number of chunks indexed
    """
    if not files or not rag_service:
        return 0
    
    try:
        return rag_service.index_uploaded_files(files)
    except Exception as e:
        logger.error(f"Background file processing failed: {e}")
        return 0


def generate_embeddings_background(texts: list, embedding_service) -> list:
    """
    Generate embeddings in background.
    
    Args:
        texts: List of texts to embed
        embedding_service: Embedding service
        
    Returns:
        List of embeddings
    """
    if not texts or not embedding_service:
        return []
    
    try:
        return embedding_service.embed_texts(texts).tolist()
    except Exception as e:
        logger.error(f"Background embedding generation failed: {e}")
        return []


# =============================================================================
# SINGLETON & FACTORY
# =============================================================================

_background_service = None


def get_background_service() -> BackgroundTaskService:
    """Get or create the background task service singleton."""
    global _background_service
    
    if _background_service is None:
        _background_service = BackgroundTaskService(max_workers=2)
        _background_service.start()
    
    return _background_service
