import React from 'react';

const RadialBackground: React.FC = () => {
  return (
    <div className="radial-background">
      <div className="absolute top-0 left-0 w-1/3 h-1/3 bg-gradient-radial from-limeGlow/10 to-transparent opacity-30" />
      <div className="absolute bottom-0 right-0 w-1/3 h-1/3 bg-gradient-radial from-aquaGlow/10 to-transparent opacity-30" />
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-1/2 h-1/2 bg-gradient-radial from-violetGlow/5 to-transparent opacity-20" />
    </div>
  );
};

export default RadialBackground;