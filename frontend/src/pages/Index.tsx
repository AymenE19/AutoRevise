
import { useState } from 'react';
import { motion } from 'framer-motion';
import Header from '../components/Header';
import CourseCard from '../components/CourseCard';
import CourseModal from '../components/CourseModal';
import AIGeneratorHub from '../components/AIGeneratorHub';
import Dashboard from '../components/Dashboard';
import SessionContent from '../components/SessionContent';
import { useCourseStore, Course } from '../store/courseStore';
import { Grid, List, BarChart3, Sparkles, BookOpen } from 'lucide-react';

const Index = () => {
  const { courses, selectedCourse, setSelectedCourse } = useCourseStore();
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [activeTab, setActiveTab] = useState<'courses' | 'ai' | 'dashboard' | 'session'>('courses');
  const [modalOpen, setModalOpen] = useState(false);

  const handleCourseClick = (course: Course) => {
    setSelectedCourse(course);
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setSelectedCourse(null);
  };

  const tabs = [
    { id: 'courses' as const, label: 'Courses', icon: Grid },
    { id: 'session' as const, label: 'Séance 1', icon: BookOpen },
    { id: 'ai' as const, label: 'AI Generator', icon: Sparkles },
    { id: 'dashboard' as const, label: 'Dashboard', icon: BarChart3 }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-bg via-surface-dark to-dark-bg">
      <Header />
      
      <main className="container mx-auto px-6 py-8">
        {/* Navigation Tabs */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-effect rounded-xl p-2 mb-8 inline-flex"
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
        {activeTab === 'courses' && (
          <div>
            {/* View Controls */}
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-3xl font-bold gradient-text mb-2">Course Library</h2>
                <p className="text-text-light">Choose from {courses.length} programming courses</p>
              </div>
              <div className="flex space-x-2">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setViewMode('grid')}
                  className={`p-3 rounded-lg transition-all duration-200 ${
                    viewMode === 'grid'
                      ? 'bg-primary text-white'
                      : 'bg-surface-dark text-text-light hover:text-white'
                  }`}
                >
                  <Grid className="w-5 h-5" />
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setViewMode('list')}
                  className={`p-3 rounded-lg transition-all duration-200 ${
                    viewMode === 'list'
                      ? 'bg-primary text-white'
                      : 'bg-surface-dark text-text-light hover:text-white'
                  }`}
                >
                  <List className="w-5 h-5" />
                </motion.button>
              </div>
            </div>

            {/* Courses Grid */}
            <motion.div 
              layout
              className={`grid gap-6 ${
                viewMode === 'grid' 
                  ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' 
                  : 'grid-cols-1 max-w-4xl mx-auto'
              }`}
            >
              {courses.map((course) => (
                <CourseCard
                  key={course.id}
                  course={course}
                  onClick={() => handleCourseClick(course)}
                />
              ))}
            </motion.div>
          </div>
        )}

        {activeTab === 'session' && <SessionContent />}
        {activeTab === 'ai' && <AIGeneratorHub />}
        {activeTab === 'dashboard' && <Dashboard />}
      </main>

      {/* Course Modal */}
      <CourseModal
        course={selectedCourse}
        isOpen={modalOpen}
        onClose={handleCloseModal}
      />
    </div>
  );
};

export default Index;
