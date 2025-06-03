
import { motion, AnimatePresence } from 'framer-motion';
import { X, Play, CheckCircle, Clock } from 'lucide-react';
import { Course, useCourseStore } from '../store/courseStore';

interface CourseModalProps {
  course: Course | null;
  isOpen: boolean;
  onClose: () => void;
}

const CourseModal = ({ course, isOpen, onClose }: CourseModalProps) => {
  const { updateSessionProgress } = useCourseStore();

  if (!course) return null;

  const handleSessionComplete = (sessionId: string) => {
    updateSessionProgress(course.id, sessionId);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="glass-effect rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="relative h-64 overflow-hidden">
              <img 
                src={course.thumbnail} 
                alt={course.title}
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
              <button
                onClick={onClose}
                className="absolute top-4 right-4 w-10 h-10 bg-black/50 backdrop-blur-sm rounded-full flex items-center justify-center text-white hover:bg-black/70 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
              <div className="absolute bottom-6 left-6 right-6">
                <h2 className="text-3xl font-bold text-white mb-2">{course.title}</h2>
                <p className="text-text-light">{course.description}</p>
                <div className="flex items-center space-x-4 mt-4">
                  <span className="bg-primary/20 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-medium text-white">
                    {course.difficulty}
                  </span>
                  <span className="text-white text-sm">★ {course.rating}</span>
                  <span className="text-white text-sm">{course.sessions.length} sessions</span>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 max-h-96 overflow-y-auto">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-white">Course Sessions</h3>
                <div className="text-sm text-text-light">
                  Progress: {Math.round(course.progress)}%
                </div>
              </div>

              <div className="space-y-4">
                {course.sessions.map((session, index) => (
                  <motion.div
                    key={session.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`glass-effect rounded-lg p-4 border-2 transition-all duration-200 ${
                      session.completed 
                        ? 'border-success/50 bg-success/10' 
                        : 'border-white/10 hover:border-primary/50'
                    }`}
                  >
                    <div className="flex items-start space-x-4">
                      <div className="flex-shrink-0">
                        {session.completed ? (
                          <CheckCircle className="w-6 h-6 text-success" />
                        ) : (
                          <Play className="w-6 h-6 text-primary" />
                        )}
                      </div>
                      <div className="flex-1">
                        <h4 className="text-white font-medium mb-2">
                          Session {index + 1}: {session.title}
                        </h4>
                        <p className="text-text-light text-sm mb-3">
                          {session.content}
                        </p>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center text-sm text-text-light">
                            <Clock className="w-4 h-4 mr-1" />
                            <span>{session.duration} min</span>
                          </div>
                          {!session.completed && (
                            <motion.button
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => handleSessionComplete(session.id)}
                              className="bg-gradient-to-r from-electric-blue to-deep-purple px-4 py-2 rounded-lg text-white text-sm font-medium hover:shadow-lg transition-all duration-200"
                            >
                              Mark Complete
                            </motion.button>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default CourseModal;
