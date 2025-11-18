import React, { useRef, useState, useEffect } from 'react';

interface ResizablePanelsProps {
  leftPanel: React.ReactNode;
  centerPanel: React.ReactNode;
  rightPanel: React.ReactNode;
  leftPanelVisible: boolean;
  rightPanelVisible: boolean;
  defaultLeftWidth?: number;
  defaultRightWidth?: number;
  minWidth?: number;
  maxWidth?: number;
}

export default function ResizablePanels({
  leftPanel,
  centerPanel,
  rightPanel,
  leftPanelVisible,
  rightPanelVisible,
  defaultLeftWidth = 320,
  defaultRightWidth = 380,
  minWidth = 200,
  maxWidth = 600
}: ResizablePanelsProps) {
  const [leftWidth, setLeftWidth] = useState(defaultLeftWidth);
  const [rightWidth, setRightWidth] = useState(defaultRightWidth);
  const [isDraggingLeft, setIsDraggingLeft] = useState(false);
  const [isDraggingRight, setIsDraggingRight] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Handle left resizer drag
  const handleLeftMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDraggingLeft(true);
  };

  // Handle right resizer drag
  const handleRightMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDraggingRight(true);
  };

  // Mouse move handler
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;

      const containerRect = containerRef.current.getBoundingClientRect();

      if (isDraggingLeft) {
        const newWidth = e.clientX - containerRect.left;
        setLeftWidth(Math.max(minWidth, Math.min(maxWidth, newWidth)));
      }

      if (isDraggingRight) {
        const newWidth = containerRect.right - e.clientX;
        setRightWidth(Math.max(minWidth, Math.min(maxWidth, newWidth)));
      }
    };

    const handleMouseUp = () => {
      setIsDraggingLeft(false);
      setIsDraggingRight(false);
    };

    if (isDraggingLeft || isDraggingRight) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);

      // Prevent text selection while dragging
      document.body.style.userSelect = 'none';
      document.body.style.cursor = 'col-resize';

      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
        document.body.style.userSelect = '';
        document.body.style.cursor = '';
      };
    }
  }, [isDraggingLeft, isDraggingRight, minWidth, maxWidth]);

  return (
    <div ref={containerRef} className="flex-1 flex overflow-hidden h-full">
      {/* LEFT PANEL */}
      {leftPanelVisible && (
        <>
          <div
            style={{ width: `${leftWidth}px` }}
            className="flex-shrink-0 h-full overflow-hidden"
          >
            {leftPanel}
          </div>

          {/* LEFT RESIZER */}
          <div
            onMouseDown={handleLeftMouseDown}
            className="w-1 bg-gray-800 hover:bg-purple-500 transition-colors cursor-col-resize flex-shrink-0 relative group"
          >
            <div className="absolute inset-y-0 left-1/2 -translate-x-1/2 w-5 flex items-center justify-center">
              <div className="w-0.5 h-8 bg-gray-600 group-hover:bg-purple-400 rounded-full transition-colors" />
            </div>
          </div>
        </>
      )}

      {/* CENTER PANEL */}
      <div className="flex-1 h-full overflow-hidden">
        {centerPanel}
      </div>

      {/* RIGHT PANEL */}
      {rightPanelVisible && (
        <>
          {/* RIGHT RESIZER */}
          <div
            onMouseDown={handleRightMouseDown}
            className="w-1 bg-gray-800 hover:bg-purple-500 transition-colors cursor-col-resize flex-shrink-0 relative group"
          >
            <div className="absolute inset-y-0 left-1/2 -translate-x-1/2 w-5 flex items-center justify-center">
              <div className="w-0.5 h-8 bg-gray-600 group-hover:bg-purple-400 rounded-full transition-colors" />
            </div>
          </div>

          <div
            style={{ width: `${rightWidth}px` }}
            className="flex-shrink-0 h-full overflow-hidden"
          >
            {rightPanel}
          </div>
        </>
      )}
    </div>
  );
}

