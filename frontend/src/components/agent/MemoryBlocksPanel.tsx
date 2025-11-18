import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface MemoryBlock {
  label: string;
  value: string;
  limit: number;
  description: string;
  read_only: boolean;
  metadata?: Record<string, any>;
}

interface MemoryBlocksPanelProps {
  agentId?: string;
}

export default function MemoryBlocksPanel({ agentId = 'default' }: MemoryBlocksPanelProps) {
  const [blocks, setBlocks] = useState<MemoryBlock[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingBlock, setEditingBlock] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchBlocks();
  }, [agentId]);

  const fetchBlocks = async () => {
    try {
      const response = await fetch(`http://localhost:8284/api/agents/${agentId}/memory/blocks`);
      const data = await response.json();
      setBlocks(data.blocks || []);
    } catch (error) {
      console.error('Failed to fetch memory blocks:', error);
    } finally {
      setLoading(false);
    }
  };

  const startEditing = (block: MemoryBlock) => {
    if (block.read_only) return;
    setEditingBlock(block.label);
    setEditValue(block.value);
  };

  const cancelEditing = () => {
    setEditingBlock(null);
    setEditValue('');
  };

  const saveBlock = async (label: string) => {
    setSaving(true);
    try {
      await fetch(`http://localhost:8284/api/agents/${agentId}/memory/blocks/${label}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value: editValue })
      });

      // Update local state
      setBlocks(blocks.map(b => 
        b.label === label ? { ...b, value: editValue } : b
      ));

      setEditingBlock(null);
      setEditValue('');
    } catch (error) {
      console.error('Failed to save block:', error);
    } finally {
      setSaving(false);
    }
  };

  const getCharCount = (text: string) => text.length;

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-900 border-l border-gray-800">
        <div className="w-6 h-6 border-2 border-purple-500/30 border-t-purple-500 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="w-full h-full flex flex-col bg-gray-900 border-l border-gray-800">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-800 flex-shrink-0">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-300">Memory Blocks</h2>
          <span className="text-xs text-gray-500">{blocks.length} blocks</span>
        </div>
      </div>

      {/* Scrollable Blocks List */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        <AnimatePresence>
          {blocks.map((block) => {
            const isEditing = editingBlock === block.label;
            const charCount = getCharCount(isEditing ? editValue : block.value);
            const percentUsed = (charCount / block.limit) * 100;

            return (
              <motion.div
                key={block.label}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className={`
                  rounded-lg border overflow-hidden transition-colors
                  ${isEditing ? 'border-purple-500 bg-gray-800/50' : 'border-gray-800 bg-gray-800/30'}
                  ${block.read_only ? 'opacity-75' : ''}
                `}
              >
                {/* Block Header */}
                <div className="px-3 py-2 bg-gray-800/50 border-b border-gray-800/50 flex items-center justify-between">
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <span className="text-xs font-semibold text-gray-300 truncate">
                      {block.label}
                    </span>
                    {block.read_only && (
                      <svg className="w-3 h-3 text-gray-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                    )}
                  </div>

                  {!block.read_only && !isEditing && (
                    <button
                      onClick={() => startEditing(block)}
                      className="p-1 hover:bg-gray-700 rounded transition-colors"
                      title="Edit block"
                    >
                      <svg className="w-3 h-3 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                  )}
                </div>

                {/* Block Content */}
                <div className="px-3 py-2 space-y-2">
                  {/* Description */}
                  {block.description && (
                    <p className="text-xs text-gray-500 italic">
                      {block.description}
                    </p>
                  )}

                  {/* Value */}
                  {isEditing ? (
                    <textarea
                      value={editValue}
                      onChange={(e) => setEditValue(e.target.value)}
                      className="w-full px-2 py-1.5 bg-gray-900 border border-gray-700 rounded text-xs text-gray-200 focus:outline-none focus:border-purple-500 font-mono resize-none"
                      rows={6}
                      maxLength={block.limit}
                    />
                  ) : (
                    <div className="text-xs text-gray-300 whitespace-pre-wrap font-mono p-2 bg-gray-900/50 rounded border border-gray-800/50 max-h-32 overflow-y-auto">
                      {block.value || <span className="text-gray-600 italic">Empty</span>}
                    </div>
                  )}

                  {/* Character Count Bar */}
                  <div className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-500">
                        {charCount.toLocaleString()} / {block.limit.toLocaleString()} chars
                      </span>
                      <span className={`
                        font-medium
                        ${percentUsed > 90 ? 'text-red-400' : percentUsed > 75 ? 'text-yellow-400' : 'text-gray-500'}
                      `}>
                        {percentUsed.toFixed(0)}%
                      </span>
                    </div>
                    <div className="w-full h-1 bg-gray-800 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min(percentUsed, 100)}%` }}
                        className={`
                          h-full rounded-full transition-colors
                          ${percentUsed > 90 ? 'bg-red-500' : percentUsed > 75 ? 'bg-yellow-500' : 'bg-purple-500'}
                        `}
                      />
                    </div>
                  </div>

                  {/* Edit Actions */}
                  {isEditing && (
                    <div className="flex items-center gap-2 pt-2">
                      <button
                        onClick={() => saveBlock(block.label)}
                        disabled={saving}
                        className="flex-1 px-3 py-1.5 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 text-white rounded text-xs font-medium transition-colors"
                      >
                        {saving ? (
                          <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin mx-auto" />
                        ) : (
                          'Save'
                        )}
                      </button>
                      <button
                        onClick={cancelEditing}
                        disabled={saving}
                        className="flex-1 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 text-gray-300 rounded text-xs font-medium transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {blocks.length === 0 && (
          <div className="text-center py-12">
            <svg className="w-12 h-12 text-gray-700 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="text-sm text-gray-500">No memory blocks yet</p>
          </div>
        )}
      </div>
    </div>
  );
}

