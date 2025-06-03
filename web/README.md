
# EduAI - Advanced Educational Learning Platform

Welcome to EduAI, a sophisticated React-based educational platform that transforms course content into interactive learning experiences with AI-powered tools.

## Project Overview

EduAI is a modern learning platform featuring:
- **8 Programming Courses** with 5 sessions each (20% progress per session)
- **AI Content Generation** (Summarize, Quiz Me, Mind Maps, Chatbot)
- **Interactive Dashboard** with progress tracking
- **Glassmorphism Design** with purple and white theme
- **Smooth Animations** using Framer Motion

## Features

### 🎯 Core Functionality
- **Course Browser**: Browse through 8 programming courses (Python, Java, Database, Web Dev, Android, Laravel, JavaScript, React Native)
- **Progress Tracking**: Each course has 5 sessions worth 20% progress each
- **AI Generator Hub**: Four AI tools for enhanced learning
- **User Dashboard**: Visual progress tracking and analytics

### 🎨 Design Features
- **Dark Theme** with purple (#8B5CF6) and electric blue (#0066FF) gradients
- **Glassmorphism Effects** with backdrop blur and transparency
- **Smooth Animations** and micro-interactions
- **Responsive Design** for all devices

### 🤖 AI Tools
1. **SUMMARIZE**: Extract key concepts from course content
2. **QUIZ ME**: Generate interactive quizzes and assessments  
3. **MIND MAP**: Create visual knowledge maps
4. **CHATBOT**: AI learning assistant for course questions

## Course Structure

Each of the 8 courses contains:
- **5 Sessions** (Introduction → Advanced concepts)
- **Progress Tracking** (20% per completed session)
- **Detailed Content** for each session
- **Duration Estimates** and difficulty levels

### Available Courses:
1. **Python** - Introduction to Python programming
2. **Java** - Object-oriented programming with Java
3. **Database** - SQL and database design
4. **Web Programming** - HTML, CSS, PHP development
5. **Android Development** - Native Android apps
6. **Laravel Framework** - PHP Laravel development
7. **JavaScript** - Modern JS with React and Node.js
8. **Mobile JS** - React Native/Ionic development

## Technical Stack

- **Frontend**: React 18+ with TypeScript
- **Styling**: Tailwind CSS with custom purple theme
- **Animations**: Framer Motion for smooth transitions
- **State Management**: Zustand for client state
- **Data Fetching**: React Query for server state
- **Icons**: Lucide React
- **Build Tool**: Vite

## Installation & Setup

```bash
# Clone the repository
git clone <YOUR_GIT_URL>

# Navigate to project
cd <YOUR_PROJECT_NAME>

# Install dependencies
npm install

# Start development server
npm run dev
```

## Chatbot Integration

**For Chatbot Script Integration:**

The chatbot script should be added to the AI Generator Hub component located at:
```
src/components/AIGeneratorHub.tsx
```

**Specific Integration Points:**

1. **Main Chatbot Section** (lines 85-120): The chatbot interface with input field and send button
2. **Message Handling** (handleSendMessage function): Where chatbot responses should be processed
3. **Chat State Management**: Update the chatMessage state and add conversation history

**Recommended Script Placement:**
- Add your chatbot initialization script in the `index.html` file in the `<head>` section
- Import chatbot functions in `AIGeneratorHub.tsx` for integration
- Use the existing message input field and send functionality

**Example Integration:**
```javascript
// In AIGeneratorHub.tsx - handleSendMessage function
const handleSendMessage = () => {
  if (chatMessage.trim()) {
    // Your chatbot API call here
    sendToChatbot(chatMessage);
    setChatMessage('');
  }
};
```

## Project Structure

```
src/
├── components/           # React components
│   ├── Header.tsx       # Navigation header
│   ├── CourseCard.tsx   # Course display cards
│   ├── CourseModal.tsx  # Course details modal
│   ├── AIGeneratorHub.tsx # AI tools interface (CHATBOT HERE)
│   └── Dashboard.tsx    # Analytics dashboard
├── store/               # State management
│   └── courseStore.ts   # Course data and progress
├── pages/               # Page components
│   └── Index.tsx        # Main application page
└── styles/              # Styling configuration
    └── index.css        # Global styles and theme
```

## Deployment

Deploy your application using:

```bash
npm run build
```

Then upload the `dist` folder to your hosting provider.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

---

**EduAI Platform** - Transforming education through AI-powered interactive learning experiences.
