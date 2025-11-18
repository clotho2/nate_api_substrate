import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Wrench, ChevronDown, ChevronUp, Check, X } from 'lucide-react';

interface ToolCall {
  name: string;
  arguments: Record<string, any>;
  result?: {
    status: string;
    message?: string;
    [key: string]: any;
  };
}

interface ToolCallsDisplayProps {
  toolCalls: ToolCall[];
}

const ToolCallsDisplay: React.FC<ToolCallsDisplayProps> = ({ toolCalls }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  
  if (!toolCalls || toolCalls.length === 0) {
    return null;
  }
  
  return (
    <motion.div
      className="mb-2"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
    >
      {/* Tool Calls Header */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="w-full flex items-center gap-2 px-3 py-1.5 rounded-t-xl bg-gradient-to-r from-blue-900/40 to-cyan-900/40 border border-blue-500/30 hover:border-blue-400/50 transition-all group"
      >
        {/* Wrench Icon */}
        <Wrench 
          size={14} 
          className="text-blue-300"
        />
        
        {/* Label */}
        <span className="text-[11px] font-medium text-blue-200/90 uppercase tracking-wide flex-1 text-left">
          Tool Calls ({toolCalls.length})
        </span>
        
        {/* Collapse/Expand Icon */}
        {isCollapsed ? (
          <ChevronDown size={14} className="text-blue-300 group-hover:text-blue-200 transition-colors" />
        ) : (
          <ChevronUp size={14} className="text-blue-300 group-hover:text-blue-200 transition-colors" />
        )}
      </button>
      
      {/* Tool Calls Content */}
      <AnimatePresence>
        {!isCollapsed && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-3 py-2 rounded-b-xl bg-blue-950/30 border-x border-b border-blue-500/20 space-y-2">
              {toolCalls.map((call, index) => (
                <div key={index} className="text-xs text-blue-200/70 font-mono">
                  {/* Tool Name */}
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-blue-300 font-semibold">{call.name}</span>
                    {call.result && (
                      call.result.status === 'OK' ? (
                        <Check size={12} className="text-green-400" />
                      ) : (
                        <X size={12} className="text-red-400" />
                      )
                    )}
                  </div>
                  
                  {/* Arguments */}
                  {Object.keys(call.arguments).length > 0 && (
                    <div className="pl-4 border-l-2 border-blue-500/20 ml-1 mb-1">
                      {Object.entries(call.arguments).map(([key, value]) => (
                        <div key={key} className="text-blue-200/60">
                          <span className="text-blue-300/80">{key}:</span>{' '}
                          {typeof value === 'string' && value.length > 50 
                            ? `${value.substring(0, 50)}...`
                            : JSON.stringify(value)
                          }
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {/* Result */}
                  {call.result && (
                    <div className="pl-4 border-l-2 border-green-500/20 ml-1 mt-1">
                      <span className={call.result.status === 'OK' ? 'text-green-400' : 'text-red-400'}>
                        {call.result.message || call.result.status}
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default ToolCallsDisplay;

