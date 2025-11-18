"""
Model Management Routes
Endpoints for listing and searching OpenRouter/Ollama models
"""

import os
import logging
import requests
from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)

models_bp = Blueprint('models', __name__)


# OpenRouter models cache (refresh every hour)
_openrouter_cache = None
_ollama_cache = None


@models_bp.route('/api/models/openrouter', methods=['GET'])
def list_openrouter_models():
    """
    List all available OpenRouter models
    Returns: [{id, name, context_length, pricing, ...}]
    """
    global _openrouter_cache
    
    try:
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            return jsonify({'error': 'OpenRouter API key not configured'}), 500
        
        # Fetch from OpenRouter API
        response = requests.get(
            'https://openrouter.ai/api/v1/models',
            headers={
                'Authorization': f'Bearer {api_key}',
                'HTTP-Referer': 'https://substrate-ai.local',
                'X-Title': 'Substrate AI'
            },
            timeout=10
        )
        
        if response.status_code != 200:
            logger.error(f"OpenRouter API error: {response.status_code}")
            return jsonify({'error': 'Failed to fetch models'}), 500
        
        data = response.json()
        models = data.get('data', [])
        
        # Transform to UI-friendly format
        ui_models = []
        for model in models:
            ui_models.append({
                'id': model.get('id'),
                'name': model.get('name', model.get('id')),
                'description': model.get('description', ''),
                'context_length': model.get('context_length', 0),
                'pricing': model.get('pricing', {}),
                'top_provider': model.get('top_provider', {}),
                'architecture': model.get('architecture', {}),
                'provider': 'openrouter'
            })
        
        # Cache result
        _openrouter_cache = ui_models
        
        logger.info(f"Fetched {len(ui_models)} OpenRouter models")
        return jsonify({'models': ui_models, 'count': len(ui_models)})
        
    except Exception as e:
        logger.error(f"Error fetching OpenRouter models: {e}")
        return jsonify({'error': str(e)}), 500


@models_bp.route('/api/models/ollama', methods=['GET'])
def list_ollama_models():
    """
    List all available Ollama models (local)
    Returns: [{name, size, modified_at, ...}]
    """
    global _ollama_cache
    
    try:
        ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        
        # Fetch from Ollama API
        response = requests.get(
            f'{ollama_url}/api/tags',
            timeout=5
        )
        
        if response.status_code != 200:
            logger.warning(f"Ollama not available: {response.status_code}")
            return jsonify({'models': [], 'count': 0})
        
        data = response.json()
        models = data.get('models', [])
        
        # Transform to UI-friendly format
        ui_models = []
        for model in models:
            ui_models.append({
                'id': model.get('name'),
                'name': model.get('name'),
                'size': model.get('size', 0),
                'modified_at': model.get('modified_at'),
                'details': model.get('details', {}),
                'provider': 'ollama'
            })
        
        # Cache result
        _ollama_cache = ui_models
        
        logger.info(f"Fetched {len(ui_models)} Ollama models")
        return jsonify({'models': ui_models, 'count': len(ui_models)})
        
    except requests.exceptions.ConnectionError:
        logger.warning("Ollama not running")
        return jsonify({'models': [], 'count': 0, 'error': 'Ollama not running'})
    except Exception as e:
        logger.error(f"Error fetching Ollama models: {e}")
        return jsonify({'error': str(e)}), 500


@models_bp.route('/api/models/all', methods=['GET'])
def list_all_models():
    """
    List all models from both OpenRouter and Ollama
    Combines both sources
    """
    try:
        # Get both model lists
        openrouter_resp = list_openrouter_models()
        ollama_resp = list_ollama_models()
        
        openrouter_data = openrouter_resp.get_json()
        ollama_data = ollama_resp.get_json()
        
        all_models = []
        
        # Add OpenRouter models
        if openrouter_data and 'models' in openrouter_data:
            all_models.extend(openrouter_data['models'])
        
        # Add Ollama models
        if ollama_data and 'models' in ollama_data:
            all_models.extend(ollama_data['models'])
        
        return jsonify({
            'models': all_models,
            'count': len(all_models),
            'sources': {
                'openrouter': openrouter_data.get('count', 0) if openrouter_data else 0,
                'ollama': ollama_data.get('count', 0) if ollama_data else 0
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching all models: {e}")
        return jsonify({'error': str(e)}), 500


@models_bp.route('/api/models/search', methods=['GET'])
def search_models():
    """
    Search models by query string
    Query params: q (search query), provider (openrouter|ollama|all)
    """
    try:
        query = request.args.get('q', '').lower().strip()
        provider = request.args.get('provider', 'all').lower()
        
        if not query:
            return jsonify({'error': 'Query parameter "q" is required'}), 400
        
        # Get models based on provider
        if provider == 'openrouter':
            models_resp = list_openrouter_models()
        elif provider == 'ollama':
            models_resp = list_ollama_models()
        else:
            models_resp = list_all_models()
        
        models_data = models_resp.get_json()
        all_models = models_data.get('models', [])
        
        # Search in model name, id, and description
        results = []
        for model in all_models:
            searchable_text = (
                f"{model.get('id', '')} "
                f"{model.get('name', '')} "
                f"{model.get('description', '')}"
            ).lower()
            
            if query in searchable_text:
                results.append(model)
        
        logger.info(f"Search '{query}' found {len(results)} models")
        return jsonify({
            'models': results,
            'count': len(results),
            'query': query
        })
        
    except Exception as e:
        logger.error(f"Error searching models: {e}")
        return jsonify({'error': str(e)}), 500


@models_bp.route('/api/models/popular', methods=['GET'])
def get_popular_models():
    """
    Return a curated list of popular/recommended models
    """
    try:
        popular = [
            # OpenRouter models
            {
                'id': 'anthropic/claude-3.5-sonnet',
                'name': 'Claude 3.5 Sonnet',
                'provider': 'openrouter',
                'description': 'Most intelligent Claude model',
                'context_length': 200000,
                'category': 'premium'
            },
            {
                'id': 'anthropic/claude-3-haiku',
                'name': 'Claude 3 Haiku',
                'provider': 'openrouter',
                'description': 'Fast and affordable',
                'context_length': 200000,
                'category': 'balanced'
            },
            {
                'id': 'qwen/qwen-2.5-72b-instruct',
                'name': 'Qwen 2.5 72B',
                'provider': 'openrouter',
                'description': 'Excellent performance, good price',
                'context_length': 128000,
                'category': 'balanced'
            },
            {
                'id': 'mistralai/mistral-large-2',
                'name': 'Mistral Large 2',
                'provider': 'openrouter',
                'description': 'European powerhouse',
                'context_length': 128000,
                'category': 'premium'
            },
            {
                'id': 'meta-llama/llama-3.1-70b-instruct',
                'name': 'Llama 3.1 70B',
                'provider': 'openrouter',
                'description': 'Open source champion',
                'context_length': 128000,
                'category': 'balanced'
            },
            # Add Ollama models if available
            {
                'id': 'llama3.1:8b',
                'name': 'Llama 3.1 8B (Local)',
                'provider': 'ollama',
                'description': 'Fast local model',
                'category': 'local'
            },
            {
                'id': 'qwen2.5:7b',
                'name': 'Qwen 2.5 7B (Local)',
                'provider': 'ollama',
                'description': 'Balanced local model',
                'category': 'local'
            }
        ]
        
        return jsonify({
            'models': popular,
            'count': len(popular),
            'categories': {
                'premium': 'Highest intelligence, higher cost',
                'balanced': 'Great performance, reasonable cost',
                'local': 'Run locally, free'
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting popular models: {e}")
        return jsonify({'error': str(e)}), 500

