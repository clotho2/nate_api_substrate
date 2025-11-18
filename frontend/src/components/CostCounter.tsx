import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface OpenRouterCosts {
  total: number;
  daily: number;
  weekly: number;
  monthly: number;
  limit: number | null;
  remaining: number | null;
  is_free: boolean;
  timestamp: string;
  status: string;
  warning?: string;
}

interface LocalStats {
  total_cost: number;
  total_tokens: number;
  total_requests: number;
  by_model: Array<{
    model: string;
    requests: number;
    tokens: number;
    cost: number;
  }>;
}

interface RequestUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  cost: number;
}

export default function CostCounter() {
  const [openRouterCosts, setOpenRouterCosts] = useState<OpenRouterCosts | null>(null);
  const [localStats, setLocalStats] = useState<LocalStats | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [loading, setLoading] = useState(true);
  const [lastRequestUsage, setLastRequestUsage] = useState<RequestUsage | null>(null);

  const fetchCosts = async () => {
    try {
      // Fetch REAL costs from OpenRouter API (ground truth!)
      const openrouterResponse = await fetch('http://localhost:8284/api/costs/openrouter');
      const openrouterData = await openrouterResponse.json();
      
      if (openrouterData.status === 'ok') {
        setOpenRouterCosts(openrouterData);
      } else {
        console.error('OpenRouter API error:', openrouterData.error);
      }
      
      // ALSO fetch local statistics (for by_model breakdown!)
      const statsResponse = await fetch('http://localhost:8284/api/costs/statistics');
      const statsData = await statsResponse.json();
      setLocalStats(statsData);
      
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch costs:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCosts();
    // Update every 30 seconds (reduced from 5s!)
    const interval = setInterval(fetchCosts, 30000);
    return () => clearInterval(interval);
  }, []);

  // Listen for request completion events (from ChatContext)
  useEffect(() => {
    const handleRequestComplete = (event: CustomEvent<RequestUsage>) => {
      setLastRequestUsage(event.detail);
      // Refresh cost data after request
      fetchCosts();
    };

    window.addEventListener('request-complete', handleRequestComplete as EventListener);
    return () => window.removeEventListener('request-complete', handleRequestComplete as EventListener);
  }, []);

  if (loading || !openRouterCosts) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 rounded-lg border border-gray-700">
        <div className="w-3 h-3 border-2 border-gray-600/30 border-t-gray-600 rounded-full animate-spin" />
        <span className="text-xs text-gray-500">Loading...</span>
      </div>
    );
  }

  const todayCost = openRouterCosts.daily;
  const totalCost = openRouterCosts.total;
  const monthlyCost = openRouterCosts.monthly;
  const hasWarning = !!openRouterCosts.warning;

  return (
    <div className="relative">
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="flex flex-col gap-1 px-3 py-1.5 bg-gray-800 hover:bg-gray-750 rounded-lg border border-gray-700 hover:border-gray-600 transition-all text-left"
      >
        {/* Last Request Info (if available) */}
        {lastRequestUsage && lastRequestUsage.total_tokens > 0 && (
          <div className="flex items-center gap-2 text-xs">
            <span className="text-gray-500">
              {lastRequestUsage.prompt_tokens.toLocaleString()} in + {lastRequestUsage.completion_tokens.toLocaleString()} out
            </span>
            <span className="text-green-400 font-semibold">
              ${lastRequestUsage.cost.toFixed(6)}
            </span>
          </div>
        )}

        {/* Today's Total */}
        <div className="flex items-center gap-2">
          {/* Money Icon */}
          <svg className="w-4 h-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>

          {/* Cost Display */}
          <div className="flex items-baseline gap-1.5">
            <span className="text-xs text-gray-400">Today:</span>
            <span className={`text-sm font-semibold ${
              todayCost === 0 ? 'text-gray-400' :
              todayCost < 0.10 ? 'text-green-400' :
              todayCost < 0.50 ? 'text-yellow-400' :
              'text-red-400'
            }`}>
              ${todayCost.toFixed(4)}
            </span>
          </div>
        </div>

        {/* Dropdown Arrow */}
        <svg 
          className={`w-3 h-3 text-gray-500 transition-transform ${showDetails ? 'rotate-180' : ''}`} 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Details */}
      <AnimatePresence>
        {showDetails && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute right-0 top-full mt-2 w-80 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50 overflow-hidden"
          >
            {/* Header */}
            <div className="px-4 py-3 bg-gray-900 border-b border-gray-700">
              <h3 className="text-sm font-semibold text-gray-200">OpenRouter Costs (REAL)</h3>
              <p className="text-xs text-gray-500 mt-1">Live data from OpenRouter API</p>
            </div>

            {/* Budget Warning (if any) */}
            {hasWarning && (
              <div className="px-4 py-3 bg-red-900/30 border-b border-red-800/50">
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <span className="text-xs text-red-300 font-medium">{openRouterCosts.warning}</span>
                </div>
              </div>
            )}

            {/* Stats */}
            <div className="p-4 space-y-3">
              {/* Today */}
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-400">Today</span>
                <span className={`text-sm font-semibold ${
                  todayCost === 0 ? 'text-gray-400' :
                  todayCost < 0.10 ? 'text-green-400' :
                  todayCost < 0.50 ? 'text-yellow-400' :
                  todayCost < 5.00 ? 'text-orange-400' :
                  'text-red-400'
                }`}>
                  ${todayCost.toFixed(4)}
                </span>
              </div>

              {/* Weekly */}
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-400">This Week</span>
                <span className="text-sm font-semibold text-gray-200">
                  ${openRouterCosts.weekly.toFixed(4)}
                </span>
              </div>

              {/* Monthly */}
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-400">This Month</span>
                <span className="text-sm font-semibold text-gray-200">
                  ${monthlyCost.toFixed(4)}
                </span>
              </div>

              {/* Total */}
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-400">Total (All Time)</span>
                <span className="text-sm font-semibold text-gray-300">
                  ${totalCost.toFixed(4)}
                </span>
              </div>

              {/* Credit Info (if available) */}
              {openRouterCosts.limit !== null && (
                <>
                  <div className="border-t border-gray-700 my-2" />
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-400">Credit Limit</span>
                    <span className="text-xs font-mono text-gray-300">
                      ${openRouterCosts.limit.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-400">Remaining</span>
                    <span className={`text-xs font-mono ${
                      (openRouterCosts.remaining || 0) < 1 ? 'text-red-400' :
                      (openRouterCosts.remaining || 0) < 5 ? 'text-yellow-400' :
                      'text-green-400'
                    }`}>
                      ${(openRouterCosts.remaining || 0).toFixed(2)}
                    </span>
                  </div>
                </>
              )}

              {/* Free Tier Indicator */}
              {openRouterCosts.is_free && (
                <div className="mt-2 px-2 py-1 bg-green-900/30 border border-green-800/50 rounded text-xs text-green-400 text-center">
                  🎉 Free Tier Active
                </div>
              )}

              {/* By Model Breakdown (from local tracker) */}
              {localStats && localStats.by_model.length > 0 && (
                <>
                  <div className="border-t border-gray-700 my-2" />
                  <div className="space-y-2">
                    <h4 className="text-xs font-medium text-gray-400">By Model (Local Tracker)</h4>
                    {localStats.by_model.slice(0, 5).map((model) => (
                      <div key={model.model} className="flex items-center justify-between text-xs">
                        <div className="flex-1 min-w-0">
                          <div className="text-gray-300 truncate font-mono text-xs">
                            {model.model.split('/').pop()}
                          </div>
                          <div className="text-gray-600 text-xs">
                            {model.requests} req · {(model.tokens / 1000).toFixed(1)}K tok
                          </div>
                        </div>
                        <span className="text-gray-400 font-semibold ml-2">
                          ${model.cost.toFixed(4)}
                        </span>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>

            {/* Footer */}
            <div className="px-4 py-2 bg-gray-900 border-t border-gray-700 text-xs text-gray-500">
              <div className="flex items-center justify-between">
                <span>Updates every 30s</span>
                <span className="text-xs text-gray-600">
                  {new Date(openRouterCosts.timestamp).toLocaleTimeString()}
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

