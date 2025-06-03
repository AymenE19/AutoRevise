
import React from 'react';
import { motion } from 'framer-motion';
import { ChevronRight, ChevronDown } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface MindmapNode {
  name: string;
  children?: MindmapNode[];
}

interface MindmapViewerProps {
  data: MindmapNode;
}

const MindmapNodeComponent: React.FC<{ node: MindmapNode; level: number }> = ({ node, level }) => {
  const [isExpanded, setIsExpanded] = React.useState(level < 2);

  const hasChildren = node.children && node.children.length > 0;

  return (
    <motion.div 
      className={`ml-${level * 4} mb-2`}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, delay: level * 0.1 }}
    >
      <div 
        className={`flex items-center cursor-pointer p-2 rounded-lg transition-colors ${
          level === 0 ? 'bg-gradient-to-r from-electric-blue/20 to-deep-purple/20 text-lg font-bold' :
          level === 1 ? 'bg-surface-dark/50 text-base font-semibold' :
          'bg-surface-dark/30 text-sm hover:bg-surface-dark/50'
        }`}
        onClick={() => hasChildren && setIsExpanded(!isExpanded)}
      >
        {hasChildren && (
          <motion.div
            animate={{ rotate: isExpanded ? 90 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronRight className="w-4 h-4 mr-2" />
          </motion.div>
        )}
        {!hasChildren && <div className="w-6 h-4 mr-2" />}
        <span className="text-white">{node.name}</span>
      </div>
      
      {hasChildren && isExpanded && (
        <motion.div 
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.3 }}
          className="mt-2"
        >
          {node.children!.map((child, index) => (
            <MindmapNodeComponent key={index} node={child} level={level + 1} />
          ))}
        </motion.div>
      )}
    </motion.div>
  );
};

const MindmapViewer: React.FC<MindmapViewerProps> = ({ data }) => {
  return (
    <Card className="glass-effect">
      <CardHeader>
        <CardTitle className="gradient-text">Mindmap du cours</CardTitle>
      </CardHeader>
      <CardContent>
        <MindmapNodeComponent node={data} level={0} />
      </CardContent>
    </Card>
  );
};

export default MindmapViewer;
