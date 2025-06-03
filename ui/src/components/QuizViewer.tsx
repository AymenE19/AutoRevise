
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, XCircle, RotateCcw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
  correctAnswer: number;
  explanation: string;
}

interface QuizData {
  title: string;
  questions: QuizQuestion[];
}

interface QuizViewerProps {
  data: QuizData;
}

const QuizViewer: React.FC<QuizViewerProps> = ({ data }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({});
  const [showResults, setShowResults] = useState(false);
  const [showExplanation, setShowExplanation] = useState<Record<number, boolean>>({});

  const handleAnswerSelect = (questionId: number, answerIndex: number) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionId]: answerIndex
    }));
    setShowExplanation(prev => ({
      ...prev,
      [questionId]: true
    }));
  };

  const calculateScore = () => {
    let correct = 0;
    data.questions.forEach(question => {
      if (selectedAnswers[question.id] === question.correctAnswer) {
        correct++;
      }
    });
    return correct;
  };

  const resetQuiz = () => {
    setCurrentQuestion(0);
    setSelectedAnswers({});
    setShowResults(false);
    setShowExplanation({});
  };

  const currentQ = data.questions[currentQuestion];
  const isAnswered = selectedAnswers[currentQ.id] !== undefined;
  const isCorrect = selectedAnswers[currentQ.id] === currentQ.correctAnswer;

  return (
    <Card className="glass-effect">
      <CardHeader>
        <CardTitle className="gradient-text">{data.title}</CardTitle>
        <p className="text-text-light">
          Question {currentQuestion + 1} sur {data.questions.length}
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {!showResults ? (
          <>
            <motion.div
              key={currentQuestion}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-4"
            >
              <h3 className="text-xl font-semibold text-white mb-4">
                {currentQ.question}
              </h3>
              
              <div className="space-y-3">
                {currentQ.options.map((option, index) => (
                  <motion.button
                    key={index}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleAnswerSelect(currentQ.id, index)}
                    disabled={isAnswered}
                    className={`w-full p-4 text-left rounded-lg border transition-all duration-200 ${
                      selectedAnswers[currentQ.id] === index
                        ? index === currentQ.correctAnswer
                          ? 'bg-success/20 border-success text-success'
                          : 'bg-destructive/20 border-destructive text-destructive'
                        : isAnswered && index === currentQ.correctAnswer
                        ? 'bg-success/20 border-success text-success'
                        : 'bg-surface-dark border-white/10 text-white hover:bg-surface-dark/80'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span>{option}</span>
                      {isAnswered && (
                        selectedAnswers[currentQ.id] === index ? (
                          index === currentQ.correctAnswer ? (
                            <CheckCircle className="w-5 h-5" />
                          ) : (
                            <XCircle className="w-5 h-5" />
                          )
                        ) : index === currentQ.correctAnswer ? (
                          <CheckCircle className="w-5 h-5" />
                        ) : null
                      )}
                    </div>
                  </motion.button>
                ))}
              </div>

              {showExplanation[currentQ.id] && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 p-4 bg-surface-dark/50 rounded-lg border border-white/10"
                >
                  <p className="text-text-light">
                    <strong>Explication :</strong> {currentQ.explanation}
                  </p>
                </motion.div>
              )}
            </motion.div>

            <div className="flex justify-between">
              <Button
                variant="outline"
                onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                disabled={currentQuestion === 0}
              >
                Précédent
              </Button>
              
              {currentQuestion === data.questions.length - 1 ? (
                <Button
                  onClick={() => setShowResults(true)}
                  disabled={Object.keys(selectedAnswers).length !== data.questions.length}
                  className="bg-gradient-to-r from-electric-blue to-deep-purple"
                >
                  Voir les résultats
                </Button>
              ) : (
                <Button
                  onClick={() => setCurrentQuestion(Math.min(data.questions.length - 1, currentQuestion + 1))}
                  disabled={!isAnswered}
                  className="bg-gradient-to-r from-electric-blue to-deep-purple"
                >
                  Suivant
                </Button>
              )}
            </div>
          </>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center space-y-6"
          >
            <div className="space-y-4">
              <h3 className="text-2xl font-bold gradient-text">
                Résultats du Quiz
              </h3>
              <div className="text-6xl font-bold text-white">
                {calculateScore()}/{data.questions.length}
              </div>
              <p className="text-text-light">
                {calculateScore() === data.questions.length
                  ? 'Parfait ! Vous maîtrisez tous les concepts.'
                  : calculateScore() >= data.questions.length * 0.7
                  ? 'Très bien ! Vous avez une bonne compréhension.'
                  : 'Continuez à étudier pour améliorer vos résultats.'}
              </p>
            </div>
            
            <Button
              onClick={resetQuiz}
              className="bg-gradient-to-r from-electric-blue to-deep-purple"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              Recommencer
            </Button>
          </motion.div>
        )}
      </CardContent>
    </Card>
  );
};

export default QuizViewer;
