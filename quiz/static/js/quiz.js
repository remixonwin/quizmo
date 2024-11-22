// Quiz functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Quiz JavaScript loaded');  // Debug point 1
    
    // Test function for debugging
    function initializeQuiz() {
        console.log('Initializing quiz');  // Debug point 2
        
        // Add a breakpoint-friendly object
        const quizData = {
            title: 'Minnesota DMV Practice Test',
            timeLimit: 30,
            currentQuestion: 0,
            score: 0,
            questions: []
        };
        
        // Add some test functions for debugging
        function updateScore(points) {
            debugger;  // Debug point 3
            quizData.score += points;
            console.log(`Score updated: ${quizData.score}`);
            return quizData.score;
        }
        
        function nextQuestion() {
            const maxQuestions = 5;
            debugger;  // Debug point 4
            if (quizData.currentQuestion < maxQuestions - 1) {
                quizData.currentQuestion++;
                console.log(`Moving to question ${quizData.currentQuestion + 1}`);
            } else {
                console.log('Quiz completed!');
            }
        }
        
        // Test the functions
        setTimeout(() => {
            console.log('Testing quiz functions...');  // Debug point 5
            updateScore(10);
            nextQuestion();
        }, 2000);
        
        return quizData;
    }
    
    const quiz = initializeQuiz();
    console.log('Quiz initialized:', quiz);  // Debug point 6
});
