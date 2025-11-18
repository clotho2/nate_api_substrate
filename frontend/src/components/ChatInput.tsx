import React, { useState, KeyboardEvent, useRef } from 'react';
import { Send, Mic, Image as ImageIcon, X } from 'lucide-react';
import { motion } from 'framer-motion';

interface ChatInputProps {
  onSendMessage: (message: string, mediaData?: string, mediaType?: string) => void;
}

interface MediaPreview {
  data: string;  // Base64
  type: string;  // MIME type
  name: string;  // File name
}

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage }) => {
  const [message, setMessage] = useState('');
  const [mediaPreview, setMediaPreview] = useState<MediaPreview | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const handleSubmit = () => {
    if (message.trim() || mediaPreview) {
      onSendMessage(
        message.trim() || "What do you think?",  // Default message if only media
        mediaPreview?.data,
        mediaPreview?.type
      );
      setMessage('');
      setMediaPreview(null);  // Clear media after sending
    }
  };
  
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    // Check file type (images only for now)
    if (!file.type.startsWith('image/')) {
      alert('Only images are supported at the moment! 🖼️');
      return;
    }
    
    // Check file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      alert('File is too large! Max 10MB. 📏');
      return;
    }
    
    // Convert to base64
    const reader = new FileReader();
    reader.onload = (event) => {
      const base64 = event.target?.result as string;
      // Remove data:image/jpeg;base64, prefix
      const base64Data = base64.split(',')[1];
      
      setMediaPreview({
        data: base64Data,
        type: file.type,
        name: file.name
      });
    };
    reader.readAsDataURL(file);
    
    // Clear input so same file can be selected again
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };
  
  const removeMedia = () => {
    setMediaPreview(null);
  };
  
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };
  
  return (
    <div className="bg-gray-900/95 backdrop-blur-md border-t border-gray-800 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Media Preview */}
        {mediaPreview && (
          <div className="mb-3 relative inline-block">
            <div className="relative rounded-lg overflow-hidden border border-purple-500/50 bg-gray-800">
              <img 
                src={`data:${mediaPreview.type};base64,${mediaPreview.data}`}
                alt={`Preview of uploaded image: ${mediaPreview.name}`}
                className="max-h-32 max-w-full object-contain"
              />
              <button
                onClick={removeMedia}
                className="absolute top-1 right-1 p-1 bg-red-500/80 hover:bg-red-500 rounded-full text-white transition-colors focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-offset-2 focus:ring-offset-gray-800"
                aria-label={`Remove image: ${mediaPreview.name}`}
              >
                <X size={16} aria-hidden="true" />
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-1 truncate max-w-xs">{mediaPreview.name}</p>
          </div>
        )}
        
        <div className="relative flex items-end gap-2">
          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
            id="file-upload-input"
            aria-label="Upload image file"
          />
          
          {/* Image Upload Button */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => fileInputRef.current?.click()}
            className="
              p-3 rounded-full bg-gray-800 border border-gray-700 text-gray-400
              hover:border-purple-500/50 hover:text-purple-400 transition-colors
              focus:outline-none focus:ring-2 focus:ring-purple-400 focus:ring-offset-2 focus:ring-offset-gray-900
            "
            aria-label="Upload image"
          >
            <ImageIcon size={20} aria-hidden="true" />
          </motion.button>
          
          <label htmlFor="message-input" className="sr-only">
            Message input
          </label>
          <textarea
            id="message-input"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            className="
              rounded-2xl py-3 pl-4 pr-12 w-full min-h-[52px] max-h-32 
              bg-gray-800 border border-gray-700 outline-none resize-none text-white
              focus:border-purple-500/50 focus:ring-2 focus:ring-purple-400 focus:ring-offset-2 focus:ring-offset-gray-900 transition-colors
            "
            placeholder={mediaPreview ? "Add a comment... (optional)" : "Message Assistant..."}
            rows={1}
            aria-label="Type your message"
          />
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="
              p-3 rounded-full bg-gradient-to-r from-limeGlow to-aquaGlow text-background
              disabled:opacity-50 disabled:cursor-not-allowed
              focus:outline-none focus:ring-2 focus:ring-limeGlow focus:ring-offset-2 focus:ring-offset-gray-900
            "
            onClick={handleSubmit}
            disabled={!message.trim() && !mediaPreview}
            aria-label="Send message"
          >
            <Send size={20} aria-hidden="true" />
          </motion.button>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;