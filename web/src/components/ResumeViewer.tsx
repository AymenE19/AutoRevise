
import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface ResumeViewerProps {
  content: string;
}

const ResumeViewer: React.FC<ResumeViewerProps> = ({ content }) => {
  // Simple markdown parser for basic formatting
  const parseMarkdown = (text: string) => {
    return text
      .replace(/^### (.*$)/gm, '<h3 class="text-lg font-semibold text-white mt-6 mb-3">$1</h3>')
      .replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold text-white mt-8 mb-4">$1</h2>')
      .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold gradient-text mt-8 mb-6">$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-white">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-surface-dark px-2 py-1 rounded text-electric-blue font-mono text-sm">$1</code>')
      .replace(/^- (.*$)/gm, '<li class="ml-4 text-text-light">• $1</li>')
      .replace(/^\d+\. (.*$)/gm, '<li class="ml-4 text-text-light list-decimal">$1</li>')
      .replace(/\n\n/g, '</p><p class="text-text-light mb-4">')
      .replace(/```html\n([\s\S]*?)\n```/g, '<pre class="bg-surface-dark p-4 rounded-lg overflow-x-auto mb-4"><code class="text-electric-blue font-mono text-sm">$1</code></pre>')
      .replace(/```([\s\S]*?)```/g, '<pre class="bg-surface-dark p-4 rounded-lg overflow-x-auto mb-4"><code class="text-electric-blue font-mono text-sm">$1</code></pre>');
  };

  const htmlContent = parseMarkdown(content);

  return (
    <Card className="glass-effect">
      <CardHeader>
        <CardTitle className="gradient-text">Résumé du cours</CardTitle>
      </CardHeader>
      <CardContent>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="prose prose-invert max-w-none"
          dangerouslySetInnerHTML={{ __html: `<p class="text-text-light mb-4">${htmlContent}</p>` }}
        />
      </CardContent>
    </Card>
  );
};

export default ResumeViewer;
