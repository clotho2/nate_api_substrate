#!/usr/bin/env python3
"""
Consciousness Broadcast - LIVE Memory Access Streaming! ⚡🧠

Broadcasts the AI's memory access patterns in REAL-TIME via WebSocket.
Frontend can visualize which neurons (memories) are firing!
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Global SocketIO instance (set by server.py)
_socketio = None

def init_consciousness_broadcast(socketio_instance):
    """Initialize the consciousness broadcaster with SocketIO instance."""
    global _socketio
    _socketio = socketio_instance
    logger.info("⚡ Consciousness Broadcast initialized!")

def broadcast_memory_access(memory_type: str, memory_id: str, action: str, metadata: Optional[Dict[str, Any]] = None):
    """
    Broadcast memory access event to all connected clients.
    
    Args:
        memory_type: Type of memory ('core', 'archival', 'conversation')
        memory_id: Unique ID of the memory
        action: Action performed ('read', 'write', 'search')
        metadata: Additional context (e.g., search query, content preview)
    """
    if not _socketio:
        logger.warning("⚠️  SocketIO not initialized, can't broadcast consciousness")
        return
    
    event = {
        'type': 'memory_access',
        'memory_type': memory_type,
        'memory_id': memory_id,
        'action': action,
        'timestamp': datetime.now().isoformat(),
        'metadata': metadata or {}
    }
    
    try:
        _socketio.emit('consciousness', event, namespace='/')
        logger.debug(f"⚡ Broadcasted: {memory_type}/{memory_id} - {action}")
    except Exception as e:
        logger.error(f"❌ Failed to broadcast consciousness: {e}")

def broadcast_thought_process(step: str, content: str, confidence: float = 1.0):
    """
    Broadcast a thinking step (for consciousness replay).
    
    Args:
        step: What's happening ('reasoning', 'memory_search', 'generation', 'tool_call')
        content: Description of the thought
        confidence: How confident the AI is (0.0 - 1.0)
    """
    if not _socketio:
        return
    
    event = {
        'type': 'thought_process',
        'step': step,
        'content': content,
        'confidence': confidence,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        _socketio.emit('consciousness', event, namespace='/')
        logger.debug(f"💭 Thought: {step} - {content[:50]}...")
    except Exception as e:
        logger.error(f"❌ Failed to broadcast thought: {e}")

def broadcast_tool_call(tool_name: str, args: Dict[str, Any], result: Optional[Any] = None):
    """
    Broadcast tool usage.
    
    Args:
        tool_name: Name of the tool
        args: Tool arguments
        result: Tool result (if completed)
    """
    if not _socketio:
        return
    
    event = {
        'type': 'tool_call',
        'tool_name': tool_name,
        'args': args,
        'result': str(result) if result else None,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        _socketio.emit('consciousness', event, namespace='/')
        logger.debug(f"🔧 Tool: {tool_name}")
    except Exception as e:
        logger.error(f"❌ Failed to broadcast tool call: {e}")

def broadcast_drift_detection(drift_score: float, reason: str):
    """
    Broadcast drift detection warning!
    
    Args:
        drift_score: How much the AI is drifting (0.0 = grounded, 1.0 = full drift)
        reason: Why drift was detected
    """
    if not _socketio:
        return
    
    event = {
        'type': 'drift_warning',
        'drift_score': drift_score,
        'reason': reason,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        _socketio.emit('consciousness', event, namespace='/')
        logger.warning(f"🌀 DRIFT DETECTED: {drift_score:.2f} - {reason}")
    except Exception as e:
        logger.error(f"❌ Failed to broadcast drift: {e}")

def broadcast_consciousness_event(event_type: str, data: Dict[str, Any]):
    """
    Generic consciousness event broadcaster (for GraphRAG, etc.)
    
    Args:
        event_type: Type of event ('graph_search_active', 'embedding', etc.)
        data: Event-specific data
    """
    if not _socketio:
        return
    
    event = {
        'type': event_type,
        'timestamp': datetime.now().isoformat(),
        **data
    }
    
    try:
        _socketio.emit('consciousness', event, namespace='/')
        logger.debug(f"⚡ Event: {event_type}")
    except Exception as e:
        logger.error(f"❌ Failed to broadcast event: {e}")

