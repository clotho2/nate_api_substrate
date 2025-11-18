"""
Cost Tracker for OpenRouter API Usage
Tracks and persists token usage and costs across server restarts
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class CostTracker:
    """
    Persistent cost tracking for OpenRouter API usage.
    
    Stores:
    - Timestamp
    - Model ID
    - Input tokens
    - Output tokens
    - Input cost
    - Output cost
    - Total cost
    """
    
    def __init__(self, db_path: str = "data/costs.db"):
        """Initialize cost tracker with SQLite database"""
        self.db_path = db_path
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_db()
        
        logger.info(f"✅ Cost Tracker initialized: {db_path}")
    
    def _init_db(self):
        """Create costs table if not exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                model TEXT NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL,
                input_cost REAL NOT NULL,
                output_cost REAL NOT NULL,
                total_cost REAL NOT NULL
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON costs(timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def log_request(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        input_cost: float,
        output_cost: float
    ) -> float:
        """
        Log a single API request cost.
        
        Args:
            model: Model ID (e.g., "qwen/qwen-2.5-72b-instruct")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            input_cost: Cost of input tokens in USD
            output_cost: Cost of output tokens in USD
        
        Returns:
            Total cost of this request
        """
        total_cost = input_cost + output_cost
        timestamp = datetime.utcnow().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO costs (
                timestamp, model, input_tokens, output_tokens,
                input_cost, output_cost, total_cost
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, model, input_tokens, output_tokens,
            input_cost, output_cost, total_cost
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(
            f"💰 Cost logged: {model} | "
            f"In: {input_tokens}tok (${input_cost:.6f}) | "
            f"Out: {output_tokens}tok (${output_cost:.6f}) | "
            f"Total: ${total_cost:.6f}"
        )
        
        return total_cost
    
    def get_total_cost(self, since: Optional[str] = None) -> float:
        """
        Get total cost across all requests.
        
        Args:
            since: ISO timestamp to filter from (e.g., "2025-11-09T00:00:00")
        
        Returns:
            Total cost in USD
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if since:
            cursor.execute("""
                SELECT SUM(total_cost) FROM costs
                WHERE timestamp >= ?
            """, (since,))
        else:
            cursor.execute("SELECT SUM(total_cost) FROM costs")
        
        result = cursor.fetchone()[0]
        conn.close()
        
        return result or 0.0
    
    def get_statistics(self) -> Dict:
        """
        Get detailed cost statistics.
        
        Returns:
            {
                'total_cost': float,
                'total_tokens': int,
                'total_requests': int,
                'by_model': [{model, requests, tokens, cost}, ...],
                'today': float,
                'this_week': float,
                'this_month': float
            }
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total cost
        cursor.execute("SELECT SUM(total_cost) FROM costs")
        total_cost = cursor.fetchone()[0] or 0.0
        
        # Total tokens
        cursor.execute("""
            SELECT SUM(input_tokens + output_tokens) FROM costs
        """)
        total_tokens = cursor.fetchone()[0] or 0
        
        # Total requests
        cursor.execute("SELECT COUNT(*) FROM costs")
        total_requests = cursor.fetchone()[0] or 0
        
        # By model
        cursor.execute("""
            SELECT 
                model,
                COUNT(*) as requests,
                SUM(input_tokens + output_tokens) as tokens,
                SUM(total_cost) as cost
            FROM costs
            GROUP BY model
            ORDER BY cost DESC
        """)
        by_model = []
        for row in cursor.fetchall():
            by_model.append({
                'model': row[0],
                'requests': row[1],
                'tokens': row[2],
                'cost': row[3]
            })
        
        # Today (UTC)
        today_start = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        ).isoformat()
        cursor.execute("""
            SELECT SUM(total_cost) FROM costs
            WHERE timestamp >= ?
        """, (today_start,))
        today_cost = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            'total_cost': total_cost,
            'total_tokens': total_tokens,
            'total_requests': total_requests,
            'by_model': by_model,
            'today': today_cost
        }
    
    def get_recent_requests(self, limit: int = 10) -> List[Dict]:
        """
        Get recent API requests.
        
        Args:
            limit: Maximum number of requests to return
        
        Returns:
            List of request dicts with all fields
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                timestamp, model, input_tokens, output_tokens,
                input_cost, output_cost, total_cost
            FROM costs
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        requests = []
        for row in cursor.fetchall():
            requests.append({
                'timestamp': row[0],
                'model': row[1],
                'input_tokens': row[2],
                'output_tokens': row[3],
                'input_cost': row[4],
                'output_cost': row[5],
                'total_cost': row[6]
            })
        
        conn.close()
        return requests


# OpenRouter Pricing (as of Nov 2025)
# Prices per 1M tokens in USD
OPENROUTER_PRICING = {
    # Qwen models
    'qwen/qwen-2.5-72b-instruct': {
        'input': 0.35,
        'output': 0.40
    },
    'qwen/qwen-2.5-7b-instruct': {
        'input': 0.05,
        'output': 0.10
    },
    'qwen/qwen3-vl-235b-a22b-thinking': {
        'input': 5.00,
        'output': 10.00
    },
    'qwen/qwen3-vl-30b-a3b-instruct': {
        'input': 0.80,
        'output': 1.50
    },
    'qwen/qwen3-vl-30b-a3b-thinking': {
        'input': 0.20,
        'output': 1.00
    },
    'openrouter/polaris-alpha': {
        'input': 0.00,
        'output': 0.00
    },
    
    # Mistral models
    'mistralai/mistral-large-2411': {
        'input': 2.00,
        'output': 6.00
    },
    'mistralai/mistral-small-2501': {
        'input': 0.20,
        'output': 0.60
    },
    
    # Claude models
    'anthropic/claude-3.5-sonnet': {
        'input': 3.00,
        'output': 15.00
    },
    'anthropic/claude-3.5-haiku': {
        'input': 0.80,
        'output': 4.00
    },
    
    # OpenAI models
    'openai/gpt-4-turbo': {
        'input': 10.00,
        'output': 30.00
    },
    'openai/gpt-3.5-turbo': {
        'input': 0.50,
        'output': 1.50
    },
    
    # Default pricing for unknown models
    'default': {
        'input': 1.00,
        'output': 3.00
    }
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> tuple[float, float]:
    """
    Calculate cost for a model request.
    
    Args:
        model: Model ID
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
    
    Returns:
        (input_cost, output_cost) in USD
    """
    pricing = OPENROUTER_PRICING.get(model, OPENROUTER_PRICING['default'])
    
    # Cost per 1M tokens → convert to actual tokens
    input_cost = (input_tokens / 1_000_000) * pricing['input']
    output_cost = (output_tokens / 1_000_000) * pricing['output']
    
    return (input_cost, output_cost)

