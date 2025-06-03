
import { motion } from 'framer-motion';
import { Clock, User, BookOpen } from 'lucide-react';
import { Course } from '../store/courseStore';

interface CourseCardProps {
  course: Course;
  onClick: () => void;
}

const CourseCard = ({ course, onClick }: CourseCardProps) => {
  const totalDuration = course.sessions.reduce((acc, session) => acc + session.duration, 0);
  const completedSessions = course.sessions.filter(session => session.completed).length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02, y: -5 }}
      className="glass-effect rounded-xl overflow-hidden cursor-pointer group hover-scale"
      onClick={onClick}
    >
      <div className="relative h-48 overflow-hidden">
        <img 
          src={course.thumbnail} 
          alt={course.title}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
        <div className="absolute bottom-4 left-4 right-4">
          <div className="flex items-center justify-between text-white">
            <span className="bg-primary/20 backdrop-blur-sm px-2 py-1 rounded-md text-xs font-medium">
              {course.difficulty}
            </span>
            <span className="text-xs">★ {course.rating}</span>
          </div>
        </div>
      </div>

      <div className="p-6">
        <h3 className="text-xl font-bold text-white mb-2 group-hover:gradient-text transition-all duration-300">
          {course.title}
        </h3>
        <p className="text-text-light text-sm mb-4 line-clamp-2">
          {course.description}
        </p>

        <div className="flex items-center justify-between text-sm text-text-light mb-4">
          <div className="flex items-center space-x-1">
            <BookOpen className="w-4 h-4" />
            <span>{course.sessions.length} sessions</span>
          </div>
          <div className="flex items-center space-x-1">
            <Clock className="w-4 h-4" />
            <span>{Math.round(totalDuration / 60)}h</span>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-text-light">Progress</span>
            <span className="text-white font-medium">{Math.round(course.progress)}%</span>
          </div>
          <div className="w-full bg-surface-dark rounded-full h-2">
            <motion.div 
              className="bg-gradient-to-r from-electric-blue to-deep-purple h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${course.progress}%` }}
              transition={{ duration: 1, delay: 0.2 }}
            />
          </div>
          <p className="text-xs text-text-light">
            {completedSessions} of {course.sessions.length} sessions completed
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default CourseCard;
