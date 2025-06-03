
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Book, Brain, FileText } from 'lucide-react';
import MindmapViewer from './MindmapViewer';
import QuizViewer from './QuizViewer';
import ResumeViewer from './ResumeViewer';

// Import des données
import mindmapData from '../data/mindmap_Seance_1.json';
import quizData from '../data/Quiz.json';
import resumeContent from '../data/resume_Seance_1.md?raw';

const SessionContent = () => {
  const [activeTab, setActiveTab] = useState<'mindmap' | 'quiz' | 'resume'>('mindmap');

  const tabs = [
    { id: 'mindmap' as const, label: 'Mindmap', icon: Brain },
    { id: 'quiz' as const, label: 'Quiz', icon: Book },
    { id: 'resume' as const, label: 'Résumé', icon: FileText }
  ];

  return (
    <div className="space-y-6">
      {/* Navigation Tabs */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-effect rounded-xl p-2 inline-flex"
      >
        {tabs.map((tab) => (
          <motion.button
            key={tab.id}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
              activeTab === tab.id
                ? 'bg-gradient-to-r from-electric-blue to-deep-purple text-white shadow-lg'
                : 'text-text-light hover:text-white hover:bg-white/5'
            }`}
          >
            <tab.icon className="w-5 h-5" />
            <span>{tab.label}</span>
          </motion.button>
        ))}
      </motion.div>

      {/* Content */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
      >
        {activeTab === 'mindmap' && <MindmapViewer data={mindmapData} />}
        {activeTab === 'quiz' && <QuizViewer data={quizData} />}
        {activeTab === 'resume' && <ResumeViewer content={resumeContent} />}
      </motion.div>
    </div>
  );
};

export default SessionContent;
