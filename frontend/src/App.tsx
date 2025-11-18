import { useEffect } from 'react';
import ChatScreen from './screens/ChatScreen';
import { setupNotifications } from './lib/notify';
import { ChatProvider } from './contexts/ChatContext';
import RadialBackground from './components/ui/RadialBackground';

function App() {
  useEffect(() => {
    // Request notification permission and setup
    setupNotifications();
  }, []);

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <RadialBackground />
      
      <ChatProvider>
        <ChatScreen />
      </ChatProvider>
    </div>
  );
}

export default App;

