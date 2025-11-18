"""
Cost Tracking Routes
Real-time OpenRouter API cost monitoring
"""

import logging
from flask import Blueprint, jsonify
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

costs_bp = Blueprint('costs', __name__)

# Will be initialized by server.py
_cost_tracker = None
_openrouter_monitor = None  # NEW: Real OpenRouter API monitor

def init_costs_routes(cost_tracker, openrouter_monitor=None):
    """Initialize routes with cost tracker instance"""
    global _cost_tracker, _openrouter_monitor
    _cost_tracker = cost_tracker
    _openrouter_monitor = openrouter_monitor


@costs_bp.route('/api/costs/total', methods=['GET'])
def get_total_cost():
    """
    Get total cost across all requests.
    Returns: {total_cost: float, currency: 'USD'}
    """
    try:
        if not _cost_tracker:
            return jsonify({'error': 'Cost tracker not initialized'}), 500
        
        total = _cost_tracker.get_total_cost()
        
        return jsonify({
            'total_cost': total,
            'currency': 'USD'
        })
        
    except Exception as e:
        logger.error(f"Error getting total cost: {e}")
        return jsonify({'error': str(e)}), 500


@costs_bp.route('/api/costs/today', methods=['GET'])
def get_today_cost():
    """
    Get today's cost (UTC timezone).
    Returns: {today_cost: float, date: str, currency: 'USD'}
    """
    try:
        if not _cost_tracker:
            return jsonify({'error': 'Cost tracker not initialized'}), 500
        
        # Today in UTC
        today_start = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        ).isoformat()
        
        today_cost = _cost_tracker.get_total_cost(since=today_start)
        
        return jsonify({
            'today_cost': today_cost,
            'date': today_start[:10],  # YYYY-MM-DD
            'currency': 'USD'
        })
        
    except Exception as e:
        logger.error(f"Error getting today's cost: {e}")
        return jsonify({'error': str(e)}), 500


@costs_bp.route('/api/costs/statistics', methods=['GET'])
def get_cost_statistics():
    """
    Get detailed cost statistics.
    Returns:
    {
        total_cost: float,
        total_tokens: int,
        total_requests: int,
        today: float,
        by_model: [{model, requests, tokens, cost}, ...]
    }
    """
    try:
        if not _cost_tracker:
            return jsonify({'error': 'Cost tracker not initialized'}), 500
        
        stats = _cost_tracker.get_statistics()
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting cost statistics: {e}")
        return jsonify({'error': str(e)}), 500


@costs_bp.route('/api/costs/recent', methods=['GET'])
def get_recent_requests():
    """
    Get recent API requests with costs.
    Returns: {requests: [{timestamp, model, tokens, cost}, ...]}
    """
    try:
        if not _cost_tracker:
            return jsonify({'error': 'Cost tracker not initialized'}), 500
        
        requests = _cost_tracker.get_recent_requests(limit=20)
        
        return jsonify({
            'requests': requests,
            'count': len(requests)
        })
        
    except Exception as e:
        logger.error(f"Error getting recent requests: {e}")
        return jsonify({'error': str(e)}), 500


@costs_bp.route('/api/costs/openrouter', methods=['GET'])
def get_openrouter_costs():
    """
    Get REAL costs from OpenRouter API (not estimates!).
    
    This is the GROUND TRUTH for costs.
    
    Returns:
    {
        'total': float,        # Total usage (USD)
        'daily': float,        # Today's usage (USD)
        'weekly': float,       # This week's usage (USD)
        'monthly': float,      # This month's usage (USD)
        'limit': float,        # Credit limit (or null)
        'remaining': float,    # Credits remaining (or null)
        'is_free': bool,       # Is this a free tier key?
        'timestamp': str,      # When this was fetched
        'status': str,         # 'ok' or 'error'
        'warning': str         # Budget warning (if any)
    }
    """
    try:
        if not _openrouter_monitor:
            return jsonify({'error': 'OpenRouter monitor not initialized'}), 500
        
        # Get real costs from OpenRouter API
        costs = _openrouter_monitor.get_real_costs()
        
        # Check for budget warnings
        warning = _openrouter_monitor.check_budget_warnings(
            daily_limit=5.0,    # $5/day
            monthly_limit=50.0  # $50/month
        )
        
        if warning:
            costs['warning'] = warning
            logger.warning(f"💸 Budget Warning: {warning}")
        
        return jsonify(costs)
        
    except Exception as e:
        logger.error(f"Error getting OpenRouter costs: {e}")
        return jsonify({'error': str(e)}), 500

