import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { History, RotateCcw, Clock, FileText, ChevronDown, ChevronRight } from 'lucide-react';

interface Version {
  version_id: string;
  timestamp: string;
  change_description: string;
  config: {
    model: string;
    temperature: number;
    max_tokens?: number;
  };
  system_prompt_length: number;
  parent_version?: string;
}

interface VersionHistoryProps {
  agentId?: string;
}

export default function VersionHistory({ agentId = 'default' }: VersionHistoryProps) {
  const [versions, setVersions] = useState<Version[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);
  const [selectedVersion, setSelectedVersion] = useState<string | null>(null);
  const [rolling, setRolling] = useState(false);

  useEffect(() => {
    if (expanded) {
      fetchVersions();
    }
  }, [expanded, agentId]);

  const fetchVersions = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8284/api/agents/${agentId}/versions?limit=20`);
      const data = await response.json();
      setVersions(data.versions || []);
    } catch (error) {
      console.error('Failed to fetch versions:', error);
    } finally {
      setLoading(false);
    }
  };

  const rollbackToVersion = async (versionId: string) => {
    if (!confirm(`Rollback to this version?\n\nThis will create a new version based on the selected one.`)) {
      return;
    }

    setRolling(true);
    try {
      const response = await fetch(
        `http://localhost:8284/api/agents/${agentId}/versions/${versionId}/rollback`,
        { method: 'POST' }
      );
      
      if (!response.ok) {
        throw new Error('Rollback failed');
      }

      const data = await response.json();
      console.log('✅ Rolled back to version:', data);
      
      // Refresh versions
      await fetchVersions();
      
      // Notify parent to reload config
      window.location.reload(); // Simple reload for now
    } catch (error) {
      console.error('Rollback error:', error);
      alert('Failed to rollback. Check console for details.');
    } finally {
      setRolling(false);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'just now';
  };

  return (
    <div className="border-t border-gray-800 pt-6">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between text-xs font-medium text-gray-400 hover:text-gray-300 transition-colors mb-4"
      >
        <div className="flex items-center gap-2">
          <History className="w-4 h-4" />
          <span>Version History</span>
          {versions.length > 0 && !loading && (
            <span className="text-purple-400">({versions.length})</span>
          )}
        </div>
        {expanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
      </button>

      {/* Version List */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-2"
          >
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-6 h-6 border-2 border-purple-500/30 border-t-purple-500 rounded-full animate-spin" />
              </div>
            ) : versions.length === 0 ? (
              <div className="text-center py-8 text-gray-500 text-xs">
                No versions yet. Make changes to create versions!
              </div>
            ) : (
              versions.map((version, index) => (
                <motion.div
                  key={version.version_id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`
                    p-3 rounded-lg border transition-all
                    ${
                      selectedVersion === version.version_id
                        ? 'border-purple-500 bg-purple-500/10'
                        : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                    }
                  `}
                  onClick={() => setSelectedVersion(
                    selectedVersion === version.version_id ? null : version.version_id
                  )}
                >
                  {/* Version Header */}
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      {/* Timestamp & Version ID */}
                      <div className="flex items-center gap-2 mb-1">
                        <Clock className="w-3 h-3 text-gray-500 flex-shrink-0" />
                        <span className="text-xs text-gray-400">
                          {formatTimestamp(version.timestamp)}
                        </span>
                        {index === 0 && (
                          <span className="text-xs px-1.5 py-0.5 bg-green-500/20 text-green-400 rounded">
                            Current
                          </span>
                        )}
                      </div>

                      {/* Change Description */}
                      <p className="text-xs text-gray-300 mb-2 line-clamp-2">
                        {version.change_description}
                      </p>

                      {/* Config Preview */}
                      <div className="flex flex-wrap gap-2 text-xs">
                        <span className="px-2 py-0.5 bg-gray-700 rounded text-gray-400">
                          {version.config.model.split('/').pop()}
                        </span>
                        <span className="px-2 py-0.5 bg-gray-700 rounded text-gray-400">
                          T: {version.config.temperature}
                        </span>
                        <span className="px-2 py-0.5 bg-gray-700 rounded text-gray-400">
                          <FileText className="w-3 h-3 inline mr-1" />
                          {version.system_prompt_length} chars
                        </span>
                      </div>
                    </div>

                    {/* Rollback Button */}
                    {index !== 0 && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          rollbackToVersion(version.version_id);
                        }}
                        disabled={rolling}
                        className="
                          flex items-center gap-1 px-2 py-1 
                          bg-purple-600 hover:bg-purple-700 
                          disabled:bg-gray-700 disabled:text-gray-500
                          text-white rounded text-xs font-medium 
                          transition-colors flex-shrink-0
                        "
                      >
                        <RotateCcw className="w-3 h-3" />
                        {rolling ? 'Rolling...' : 'Rollback'}
                      </button>
                    )}
                  </div>

                  {/* Expanded Details */}
                  {selectedVersion === version.version_id && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="mt-3 pt-3 border-t border-gray-700 space-y-2"
                    >
                      <div className="text-xs">
                        <div className="text-gray-500 mb-1">Version ID:</div>
                        <code className="text-gray-400 font-mono text-xs">{version.version_id}</code>
                      </div>
                      <div className="text-xs">
                        <div className="text-gray-500 mb-1">Full Timestamp:</div>
                        <div className="text-gray-400">
                          {new Date(version.timestamp).toLocaleString()}
                        </div>
                      </div>
                      <div className="text-xs">
                        <div className="text-gray-500 mb-1">Model:</div>
                        <code className="text-gray-400 font-mono text-xs">{version.config.model}</code>
                      </div>
                    </motion.div>
                  )}
                </motion.div>
              ))
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}







