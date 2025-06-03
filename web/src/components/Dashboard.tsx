
import { motion } from 'framer-motion';
import { TrendingUp, Clock, Trophy, Target } from 'lucide-react';
import { useCourseStore } from '../store/courseStore';

const Dashboard = () => {
  const { courses } = useCourseStore();
  
  const totalCourses = courses.length;
  const completedCourses = courses.filter(course => course.progress === 100).length;
  const inProgressCourses = courses.filter(course => course.progress > 0 && course.progress < 100).length;
  const averageProgress = courses.reduce((acc, course) => acc + course.progress, 0) / totalCourses;
  
  const stats = [
    {
      icon: Target,
      label: 'Total Courses',
      value: totalCourses,
      color: 'from-blue-500 to-purple-600'
    },
    {
      icon: Trophy,
      label: 'Completed',
      value: completedCourses,
      color: 'from-green-500 to-blue-600'
    },
    {
      icon: Clock,
      label: 'In Progress',
      value: inProgressCourses,
      color: 'from-orange-500 to-red-600'
    },
    {
      icon: TrendingUp,
      label: 'Avg Progress',
      value: `${Math.round(averageProgress)}%`,
      color: 'from-purple-500 to-pink-600'
    }
  ];

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h2 className="text-3xl font-bold gradient-text mb-4">Learning Dashboard</h2>
        <p className="text-text-light">Track your progress and achievements</p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.05 }}
            className="glass-effect rounded-xl p-6 text-center"
          >
            <div className={`w-16 h-16 bg-gradient-to-r ${stat.color} rounded-lg flex items-center justify-center mx-auto mb-4`}>
              <stat.icon className="w-8 h-8 text-white" />
            </div>
            <div className="text-2xl font-bold text-white mb-2">{stat.value}</div>
            <div className="text-text-light text-sm">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Recent Progress */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="glass-effect rounded-xl p-6"
      >
        <h3 className="text-xl font-bold text-white mb-6">Course Progress</h3>
        <div className="space-y-4">
          {courses.slice(0, 5).map((course, index) => (
            <motion.div
              key={course.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center space-x-4"
            >
              <img 
                src={course.thumbnail} 
                alt={course.title}
                className="w-12 h-12 rounded-lg object-cover"
              />
              <div className="flex-1">
                <h4 className="text-white font-medium">{course.title}</h4>
                <div className="flex items-center space-x-4 mt-2">
                  <div className="flex-1 bg-surface-dark rounded-full h-2">
                    <motion.div 
                      className="bg-gradient-to-r from-electric-blue to-deep-purple h-2 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${course.progress}%` }}
                      transition={{ duration: 1, delay: 0.5 + index * 0.1 }}
                    />
                  </div>
                  <span className="text-sm text-text-light font-medium">
                    {Math.round(course.progress)}%
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;
