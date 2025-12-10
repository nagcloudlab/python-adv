"""
Simple In-Memory Database
=========================
For testing purposes, we use a simple dict-based database.
This makes it easy to reset between tests.
"""

from typing import Dict, Optional
from datetime import datetime


class Database:
    """
    Simple in-memory database class
    
    Can be easily reset for testing
    """
    
    def __init__(self):
        self.tasks: Dict[int, dict] = {}
        self.users: Dict[str, dict] = {}
        self._task_counter = 0
        self._initialize_data()
    
    def _initialize_data(self):
        """Initialize with sample data"""
        # Sample users
        self.users = {
            "admin": {
                "username": "admin",
                "api_key": "admin-key-123",
                "role": "admin"
            },
            "user1": {
                "username": "user1",
                "api_key": "user1-key-456",
                "role": "user"
            }
        }
        
        # Sample tasks
        self.create_task("Learn FastAPI", "Complete the tutorial", 1, 5)
        self.create_task("Write Tests", "Add pytest tests", 1, 4)
    
    def reset(self):
        """Reset database to initial state"""
        self.tasks = {}
        self._task_counter = 0
        self._initialize_data()
    
    def clear(self):
        """Clear all data"""
        self.tasks = {}
        self.users = {}
        self._task_counter = 0
    
    # Task operations
    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        owner_id: int = 1,
        priority: int = 1
    ) -> dict:
        """Create a new task"""
        self._task_counter += 1
        task = {
            "id": self._task_counter,
            "title": title,
            "description": description,
            "status": "pending",
            "priority": priority,
            "owner_id": owner_id,
            "created_at": datetime.now().isoformat()
        }
        self.tasks[self._task_counter] = task
        return task
    
    def get_task(self, task_id: int) -> Optional[dict]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> list:
        """Get all tasks"""
        return list(self.tasks.values())
    
    def update_task(self, task_id: int, data: dict) -> Optional[dict]:
        """Update a task"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        for key, value in data.items():
            if value is not None:
                task[key] = value
        
        return task
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False
    
    # User operations
    def get_user_by_api_key(self, api_key: str) -> Optional[dict]:
        """Get user by API key"""
        for user in self.users.values():
            if user["api_key"] == api_key:
                return user
        return None


# Global database instance
db = Database()


def get_database() -> Database:
    """Dependency to get database instance"""
    return db
