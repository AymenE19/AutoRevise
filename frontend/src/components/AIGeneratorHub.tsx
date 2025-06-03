
import { motion } from 'framer-motion';
import { FileText, BookOpen, Map, MessageCircle, Send, Sparkles } from 'lucide-react';
import { useState } from 'react';

const AIGeneratorHub = () => {
  const [selectedTool, setSelectedTool] = useState<string | null>(null);
  const [chatMessage, setChatMessage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const aiTools = [
    {
      id: 'summarize',
      icon: FileText,
      title: 'SUMMARIZE',
      description: 'Extract key concepts and main points',
      color: 'from-blue-500 to-purple-600'
    },
    {
      id: 'quiz',
      icon: BookOpen,
      title: 'QUIZ ME',
      description: 'Generate interactive quizzes',
      color: 'from-purple-500 to-pink-600'
    },
    {
      id: 'mindmap',
      icon: Map,
      title: 'MIND MAP',
      description: 'Create visual knowledge maps',
      color: 'from-green-500 to-blue-600'
    }
  ];

  const handleGenerate = async (toolId: string) => {
    setIsGenerating(true);
    setSelectedTool(toolId);
    
    // Simulate AI generation
    setTimeout(() => {
      setIsGenerating(false);
      console.log(`Generated content for ${toolId}`);
    }, 2000);
  };

  const handleSendMessage = () => {
    if (chatMessage.trim()) {
      console.log('Sending message:', chatMessage);
      setChatMessage('');
    }
  };

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h2 className="text-3xl font-bold gradient-text mb-4">AI Content Generator Hub</h2>
        <p className="text-text-light">Transform your learning with AI-powered tools</p>
      </motion.div>

      {/* AI Tools */}
      <div className="grid md:grid-cols-3 gap-6">
        {aiTools.map((tool, index) => (
          <motion.div
            key={tool.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.05 }}
            className={`glass-effect rounded-xl p-6 cursor-pointer group ${
              selectedTool === tool.id ? 'ring-2 ring-primary' : ''
            }`}
            onClick={() => handleGenerate(tool.id)}
          >
            <div className={`w-16 h-16 bg-gradient-to-r ${tool.color} rounded-lg flex items-center justify-center mb-4 group-hover:animate-glow`}>
              <tool.icon className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">{tool.title}</h3>
            <p className="text-text-light text-sm mb-4">{tool.description}</p>
            
            {isGenerating && selectedTool === tool.id ? (
              <div className="flex items-center justify-center py-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
              </div>
            ) : (
              <div className="flex items-center text-primary group-hover:text-white transition-colors">
                <Sparkles className="w-4 h-4 mr-2" />
                <span className="text-sm font-medium">Generate</span>
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Chatbot Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass-effect rounded-xl p-6"
      >
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-12 h-12 bg-gradient-to-r from-electric-blue to-deep-purple rounded-lg flex items-center justify-center">
            <MessageCircle className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">AI Learning Assistant</h3>
            <p className="text-text-light text-sm">Ask questions about your courses</p>
          </div>
        </div>

        <div className="flex space-x-4">
          <input
            type="text"
            value={chatMessage}
            onChange={(e) => setChatMessage(e.target.value)}
            placeholder="Ask me anything about your courses..."
            className="flex-1 bg-surface-dark/50 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200"
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleSendMessage}
            className="bg-gradient-to-r from-electric-blue to-deep-purple px-6 py-3 rounded-lg text-white font-medium hover:shadow-lg transition-all duration-200"
          >
            <Send className="w-5 h-5" />
          </motion.button>
        </div>
      </motion.div>
    </div>
  );
};

export default AIGeneratorHub;
