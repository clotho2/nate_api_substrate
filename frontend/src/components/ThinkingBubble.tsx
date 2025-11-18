import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, ChevronDown, ChevronUp } from 'lucide-react';

interface ThinkingBubbleProps {
  thinking: string;
  isStreaming?: boolean;
}

const ThinkingBubble: React.FC<ThinkingBubbleProps> = ({ thinking, isStreaming = false }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  
  return (
    <motion.div
      className="mb-2"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
    >
      {/* Thinking Header - Always visible, clickable to collapse/expand */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="w-full flex items-center gap-2 px-3 py-1.5 rounded-t-xl bg-gradient-to-r from-purple-900/40 to-pink-900/40 border border-purple-500/30 hover:border-purple-400/50 transition-all group"
      >
        {/* Brain Icon */}
        <Brain 
          size={14} 
          className={`text-purple-300 ${isStreaming ? 'animate-pulse' : ''}`}
        />
        
        {/* Label */}
        <span className="text-[11px] font-medium text-purple-200/90 uppercase tracking-wide flex-1 text-left">
          {isStreaming ? 'thinking...' : 'thought process'}
        </span>
        
        {/* Collapse/Expand Icon */}
        {isCollapsed ? (
          <ChevronDown size={14} className="text-purple-300 group-hover:text-purple-200 transition-colors" />
        ) : (
          <ChevronUp size={14} className="text-purple-300 group-hover:text-purple-200 transition-colors" />
        )}
      </button>
      
      {/* Thinking Content - Collapsible */}
      <AnimatePresence>
        {!isCollapsed && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-3 py-2 rounded-b-xl bg-purple-950/30 border-x border-b border-purple-500/20">
              <p className="text-xs text-purple-200/70 whitespace-pre-wrap break-words overflow-wrap-anywhere leading-relaxed font-mono">
                {thinking}
                {isStreaming && (
                  <motion.span
                    className="inline-block w-1.5 h-3 ml-1 bg-purple-400"
                    animate={{ opacity: [1, 0, 1] }}
                    transition={{ duration: 0.8, repeat: Infinity }}
                  />
                )}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default ThinkingBubble;

