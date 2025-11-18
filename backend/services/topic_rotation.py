"""
Topic Rotation Manager
Handles cycling through topics, tracking which have been used
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional


class TopicRotationManager:
    """Manages rotation through topics"""
    
    def __init__(self, state_file: str = "topic_rotation_state.json"):
        """
        Initialize the rotation manager
        
        Args:
            state_file: Path to JSON file storing rotation state
        """
        self.state_file = Path(state_file)
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        """Load rotation state from file"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "current_index": 0,
                "topics_queue": [],
                "last_run": None,
                "cycle_count": 0
            }
    
    def _save_state(self):
        """Save rotation state to file"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def initialize_topics(self, topics: list):
        """
        Initialize or reset the topics queue
        
        Args:
            topics: List of topic names to cycle through
        """
        if not self.state["topics_queue"] or set(topics) != set(self.state["topics_queue"]):
            self.state["topics_queue"] = topics.copy()
            self.state["current_index"] = 0
            self._save_state()
    
    def get_next_topic(self) -> Optional[str]:
        """
        Get the next topic in rotation
        
        Returns:
            Topic name, or None if no topics available
        """
        if not self.state["topics_queue"]:
            return None
        
        # Get current topic
        topic = self.state["topics_queue"][self.state["current_index"]]
        
        # Move to next index
        self.state["current_index"] += 1
        
        # Reset if we've gone through all topics
        if self.state["current_index"] >= len(self.state["topics_queue"]):
            self.state["current_index"] = 0
            self.state["cycle_count"] += 1
        
        # Update last run time
        self.state["last_run"] = datetime.now().isoformat()
        
        self._save_state()
        
        return topic
    
    def get_current_state(self) -> dict:
        """Get current rotation state"""
        return {
            "current_topic": self.state["topics_queue"][self.state["current_index"]] 
                           if self.state["topics_queue"] else None,
            "topics_remaining": len(self.state["topics_queue"]) - self.state["current_index"],
            "total_topics": len(self.state["topics_queue"]),
            "cycle_count": self.state["cycle_count"],
            "last_run": self.state["last_run"]
        }
    
    def reset(self):
        """Reset rotation to beginning"""
        self.state["current_index"] = 0
        self.state["cycle_count"] = 0
        self._save_state()