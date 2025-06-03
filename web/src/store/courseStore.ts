
import { create } from 'zustand';

export interface Session {
  id: string;
  title: string;
  content: string;
  completed: boolean;
  duration: number; // in minutes
}

export interface Course {
  id: string;
  title: string;
  description: string;
  thumbnail: string;
  sessions: Session[];
  progress: number; // 0-100
  rating: number;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  category: string;
}

interface CourseStore {
  courses: Course[];
  selectedCourse: Course | null;
  setSelectedCourse: (course: Course | null) => void;
  updateSessionProgress: (courseId: string, sessionId: string) => void;
  calculateCourseProgress: (courseId: string) => void;
}

const initialCourses: Course[] = [
  {
    id: '1',
    title: 'Python',
    description: 'Master Python programming from basics to advanced concepts',
    thumbnail: 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=400&h=250&fit=crop',
    rating: 4.8,
    difficulty: 'Beginner',
    category: 'Programming',
    progress: 0,
    sessions: [
      {
        id: '1-1',
        title: 'Introduction à Python',
        content: 'Présentation de Python et installation de l\'environnement (Anaconda, VS Code, Jupyter Notebook), Variables et types de données (entiers, flottants, chaînes, booléens), Opérateurs arithmétiques, logiques et de comparaison, Structures de contrôle : conditions (if-else) et boucles (for, while).',
        completed: false,
        duration: 120
      },
      {
        id: '1-2',
        title: 'Fonctions et Manipulation des Données',
        content: 'Définition et utilisation des fonctions (def, return), Passage de paramètres et valeurs de retour, Manipulation des chaînes de caractères et opérations sur les listes, Lecture et écriture dans des fichiers.',
        completed: false,
        duration: 135
      },
      {
        id: '1-3',
        title: 'Structures de Données et Algorithmes Fondamentaux',
        content: 'Listes et dictionnaires : création, modification et parcours, Tri et recherche : tri à bulles, tri rapide, recherche linéaire et dichotomique, Complexité algorithmique et optimisation des boucles.',
        completed: false,
        duration: 150
      },
      {
        id: '1-4',
        title: 'Programmation Orientée Objet (POO)',
        content: 'Définition des classes et des objets, Constructeur (__init__) et méthodes spéciales, Héritage et polymorphisme, Gestion des exceptions avec try-except.',
        completed: false,
        duration: 140
      },
      {
        id: '1-5',
        title: 'Bases de données et APIs',
        content: 'Introduction aux bases de données avec SQLite, Interaction avec des APIs et requêtes HTTP.',
        completed: false,
        duration: 130
      }
    ]
  },
  {
    id: '2',
    title: 'Java',
    description: 'Learn Java programming and object-oriented concepts',
    thumbnail: 'https://images.unsplash.com/photo-1517077304055-6e89abbf09b0?w=400&h=250&fit=crop',
    rating: 4.7,
    difficulty: 'Intermediate',
    category: 'Programming',
    progress: 0,
    sessions: [
      {
        id: '2-1',
        title: 'Introduction au langage Java',
        content: 'Syntaxe, variables, conditions, boucles. Installation d\'un IDE (Eclipse/IntelliJ). Opérateurs logiques et de comparaison, Structures de contrôle : conditions (if-else) et boucles (for, while).',
        completed: false,
        duration: 125
      },
      {
        id: '2-2',
        title: 'Programmation orientée objet (POO)',
        content: 'Concepts de classes, objets, constructeurs, getters, setters.',
        completed: false,
        duration: 140
      },
      {
        id: '2-3',
        title: 'Héritage et encapsulation',
        content: 'Héritage, encapsulation, interfaces.',
        completed: false,
        duration: 135
      },
      {
        id: '2-4',
        title: 'Collections et gestion des exceptions',
        content: 'ArrayList (Tri, recherche), HashMap, gestion des erreurs (try-catch).',
        completed: false,
        duration: 145
      },
      {
        id: '2-5',
        title: 'Bases de données et APIs',
        content: 'Introduction aux bases de données avec JDBC, Interaction avec des APIs et fichiers.',
        completed: false,
        duration: 130
      }
    ]
  },
  {
    id: '3',
    title: 'Base de données',
    description: 'Master database design and SQL queries',
    thumbnail: 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400&h=250&fit=crop',
    rating: 4.6,
    difficulty: 'Intermediate',
    category: 'Database',
    progress: 0,
    sessions: [
      {
        id: '3-1',
        title: 'Concepts de base et SQL',
        content: 'Modèle relationnel, introduction à SQL.',
        completed: false,
        duration: 120
      },
      {
        id: '3-2',
        title: 'Modélisation',
        content: 'Diagrammes E/A, normalisation.',
        completed: false,
        duration: 135
      },
      {
        id: '3-3',
        title: 'Requêtes SQL avancées',
        content: 'JOIN, GROUP BY, sous-requêtes.',
        completed: false,
        duration: 150
      },
      {
        id: '3-4',
        title: 'Transactions et sécurité',
        content: 'Gestion des transactions, introduction aux verrous.',
        completed: false,
        duration: 140
      },
      {
        id: '3-5',
        title: 'Connexion via langages',
        content: 'Connexion avec JDBC, PHP PDO.',
        completed: false,
        duration: 125
      }
    ]
  },
  {
    id: '4',
    title: 'Programmation Web',
    description: 'Build modern web applications with HTML, CSS, PHP',
    thumbnail: 'https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?w=400&h=250&fit=crop',
    rating: 4.5,
    difficulty: 'Beginner',
    category: 'Web Development',
    progress: 0,
    sessions: [
      {
        id: '4-1',
        title: 'Bases d\'HTML et CSS',
        content: 'Structure d\'une page web, introduction à CSS.',
        completed: false,
        duration: 110
      },
      {
        id: '4-2',
        title: 'Introduction à PHP',
        content: 'Syntaxe de base, variables, boucles, fonctions.',
        completed: false,
        duration: 130
      },
      {
        id: '4-3',
        title: 'Interaction avec les bases de données',
        content: 'Connexion à une base, exécution de requêtes SQL.',
        completed: false,
        duration: 145
      },
      {
        id: '4-4',
        title: 'Sessions et cookies',
        content: 'Gestion des utilisateurs avec sessions et cookies.',
        completed: false,
        duration: 125
      },
      {
        id: '4-5',
        title: 'AJAX et interactivité',
        content: 'Améliorer l\'expérience utilisateur avec AJAX.',
        completed: false,
        duration: 135
      }
    ]
  },
  {
    id: '5',
    title: 'Programmation Mobile Android',
    description: 'Create native Android applications',
    thumbnail: 'https://images.unsplash.com/photo-1607252650355-f7fd0460ccdb?w=400&h=250&fit=crop',
    rating: 4.7,
    difficulty: 'Advanced',
    category: 'Mobile Development',
    progress: 0,
    sessions: [
      {
        id: '5-1',
        title: 'Introduction à Android Studio',
        content: 'Installation, création d\'un premier projet, architecture d\'une application.',
        completed: false,
        duration: 140
      },
      {
        id: '5-2',
        title: 'Interfaces utilisateur',
        content: 'XML, vues, boutons, champs de texte.',
        completed: false,
        duration: 135
      },
      {
        id: '5-3',
        title: 'Navigation et fragments',
        content: 'Multi-écrans avec fragments et intents.',
        completed: false,
        duration: 150
      },
      {
        id: '5-4',
        title: 'Bases de données locales',
        content: 'SQLite, SharedPreferences.',
        completed: false,
        duration: 145
      },
      {
        id: '5-5',
        title: 'Fonctionnalités natives et déploiement',
        content: 'Localisation, caméra, génération d\'APK.',
        completed: false,
        duration: 130
      }
    ]
  },
  {
    id: '6',
    title: 'Framework PHP Laravel',
    description: 'Build powerful web applications with Laravel',
    thumbnail: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=400&h=250&fit=crop',
    rating: 4.8,
    difficulty: 'Advanced',
    category: 'Web Framework',
    progress: 0,
    sessions: [
      {
        id: '6-1',
        title: 'Introduction à Laravel',
        content: 'Installation, structure du projet.',
        completed: false,
        duration: 120
      },
      {
        id: '6-2',
        title: 'Routage et contrôleurs',
        content: 'Gestion des routes, création de contrôleurs.',
        completed: false,
        duration: 135
      },
      {
        id: '6-3',
        title: 'Modèles et bases de données',
        content: 'Migrations, ORM Eloquent.',
        completed: false,
        duration: 150
      },
      {
        id: '6-4',
        title: 'Formulaires et validation',
        content: 'Gestion des entrées utilisateur.',
        completed: false,
        duration: 140
      },
      {
        id: '6-5',
        title: 'API RESTful',
        content: 'Création d\'une API avec Laravel.',
        completed: false,
        duration: 145
      }
    ]
  },
  {
    id: '7',
    title: 'Programmation JS',
    description: 'Modern JavaScript development with React and Node.js',
    thumbnail: 'https://images.unsplash.com/photo-1579820010410-c10411aaaa88?w=400&h=250&fit=crop',
    rating: 4.9,
    difficulty: 'Intermediate',
    category: 'JavaScript',
    progress: 0,
    sessions: [
      {
        id: '7-1',
        title: 'Bases de JavaScript moderne',
        content: 'Syntaxe ES6, manipulation du DOM.',
        completed: false,
        duration: 125
      },
      {
        id: '7-2',
        title: 'Framework front-end (React.js)',
        content: 'Installation, composants, props.',
        completed: false,
        duration: 145
      },
      {
        id: '7-3',
        title: 'Node.js et Express.js',
        content: 'Introduction à Node.js, création d\'un serveur.',
        completed: false,
        duration: 140
      },
      {
        id: '7-4',
        title: 'Base de données avec Node.js',
        content: 'Connexion à une base via Mongoose.',
        completed: false,
        duration: 135
      },
      {
        id: '7-5',
        title: 'Application complète',
        content: 'Développement d\'une application full-stack.',
        completed: false,
        duration: 160
      }
    ]
  },
  {
    id: '8',
    title: 'Programmation mobile JS',
    description: 'Cross-platform mobile development with React Native',
    thumbnail: 'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400&h=250&fit=crop',
    rating: 4.6,
    difficulty: 'Advanced',
    category: 'Mobile Development',
    progress: 0,
    sessions: [
      {
        id: '8-1',
        title: 'Introduction à React Native/Ionic',
        content: 'Installation, création d\'un premier projet.',
        completed: false,
        duration: 130
      },
      {
        id: '8-2',
        title: 'Interfaces utilisateur',
        content: 'Composants de base, navigation.',
        completed: false,
        duration: 140
      },
      {
        id: '8-3',
        title: 'Gestion des données et API',
        content: 'Axios, connexion à une API REST.',
        completed: false,
        duration: 135
      },
      {
        id: '8-4',
        title: 'Fonctionnalités natives',
        content: 'Accès au GPS, caméra, stockage.',
        completed: false,
        duration: 150
      },
      {
        id: '8-5',
        title: 'Déploiement',
        content: 'Génération d\'APK/IPA, tests.',
        completed: false,
        duration: 145
      }
    ]
  }
];

export const useCourseStore = create<CourseStore>((set, get) => ({
  courses: initialCourses,
  selectedCourse: null,
  setSelectedCourse: (course) => set({ selectedCourse: course }),
  updateSessionProgress: (courseId, sessionId) => {
    const { courses } = get();
    const updatedCourses = courses.map(course => {
      if (course.id === courseId) {
        const updatedSessions = course.sessions.map(session => {
          if (session.id === sessionId) {
            return { ...session, completed: true };
          }
          return session;
        });
        return { ...course, sessions: updatedSessions };
      }
      return course;
    });
    set({ courses: updatedCourses });
    get().calculateCourseProgress(courseId);
  },
  calculateCourseProgress: (courseId) => {
    const { courses } = get();
    const updatedCourses = courses.map(course => {
      if (course.id === courseId) {
        const completedSessions = course.sessions.filter(session => session.completed).length;
        const progress = (completedSessions / course.sessions.length) * 100;
        return { ...course, progress };
      }
      return course;
    });
    set({ courses: updatedCourses });
  }
}));
