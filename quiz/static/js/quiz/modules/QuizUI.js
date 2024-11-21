/**
 * Quiz UI Module
 * Handles all UI interactions and updates
 */

export class QuizUI {
    constructor() {
        this.elements = {
            form: document.querySelector('#quiz-form'),
            progress: document.querySelector('#quiz-progress'),
            timer: document.querySelector('#quiz-timer'),
            submitBtn: document.querySelector('#submit-btn'),
            loadingTrigger: document.querySelector('#loading-trigger'),
            questionContainer: document.querySelector('#question-container'),
            messageContainer: document.querySelector('#message-container')
        };
        this.questionTemplate = document.querySelector('#question-template');
    }

    /**
     * Render a batch of questions
     */
    async renderQuestionBatch(questions) {
        const fragment = document.createDocumentFragment();
        
        questions.forEach(question => {
            const element = this.createQuestionElement(question);
            if (element) fragment.appendChild(element);
        });

        // Use requestAnimationFrame for smooth rendering
        requestAnimationFrame(() => {
            this.elements.questionContainer.appendChild(fragment);
            this.updateLayout();
        });
    }

    /**
     * Create question element from template
     */
    createQuestionElement(question) {
        if (!this.questionTemplate) return null;

        const element = this.questionTemplate.content.cloneNode(true);
        const container = element.querySelector('.question');
        
        if (container) {
            container.id = `question-${question.id}`;
            container.querySelector('.question-text').textContent = question.text;
            
            const choicesContainer = container.querySelector('.choices');
            if (choicesContainer && question.choices) {
                question.choices.forEach(choice => {
                    const choiceElement = this.createChoiceElement(question.id, choice);
                    choicesContainer.appendChild(choiceElement);
                });
            }
        }

        return container;
    }

    /**
     * Create choice element
     */
    createChoiceElement(questionId, choice) {
        const label = document.createElement('label');
        label.className = 'choice';

        const input = document.createElement('input');
        input.type = 'radio';
        input.name = `question_${questionId}`;
        input.value = choice.id;
        input.required = true;

        const text = document.createElement('span');
        text.textContent = choice.text;

        label.appendChild(input);
        label.appendChild(text);

        return label;
    }

    /**
     * Get question inputs
     */
    getQuestionInputs(questionId) {
        return Array.from(
            document.querySelectorAll(`input[name="question_${questionId}"]`)
        );
    }

    /**
     * Update quiz progress
     */
    updateProgress(progress) {
        if (this.elements.progress) {
            const percentage = Math.round((progress.answered / progress.total) * 100);
            this.elements.progress.textContent = `Progress: ${percentage}%`;
            this.elements.progress.style.width = `${percentage}%`;
        }
    }

    /**
     * Update timer display
     */
    updateTimer(remainingTime) {
        if (this.elements.timer) {
            const minutes = Math.floor(remainingTime / 60);
            const seconds = remainingTime % 60;
            this.elements.timer.textContent = 
                `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
    }

    /**
     * Show submitting state
     */
    showSubmitting() {
        if (this.elements.submitBtn) {
            this.elements.submitBtn.textContent = 'Submitting...';
            this.elements.submitBtn.disabled = true;
        }
    }

    /**
     * Show quiz results
     */
    showResult(result, isTimeout = false) {
        const message = isTimeout ? 
            'Time\'s up! Your answers have been submitted.' :
            'Quiz submitted successfully!';
            
        this.showMessage(message, 'success');
        
        if (result.score !== undefined) {
            this.showScore(result.score);
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        this.showMessage(message, 'error');
    }

    /**
     * Show recovery message
     */
    showRecoveryMessage(message) {
        this.showMessage(message, 'info');
    }

    /**
     * Show message with type
     */
    showMessage(message, type = 'info') {
        if (this.elements.messageContainer) {
            const element = document.createElement('div');
            element.className = `message message-${type}`;
            element.textContent = message;

            this.elements.messageContainer.innerHTML = '';
            this.elements.messageContainer.appendChild(element);

            // Auto-hide info messages
            if (type === 'info') {
                setTimeout(() => {
                    element.remove();
                }, 5000);
            }
        }
    }

    /**
     * Show score
     */
    showScore(score) {
        const element = document.createElement('div');
        element.className = 'score';
        element.textContent = `Your score: ${score}%`;
        
        if (this.elements.messageContainer) {
            this.elements.messageContainer.appendChild(element);
        }
    }

    /**
     * Restore previous answers
     */
    restoreAnswers(answers) {
        Object.entries(answers).forEach(([questionId, choiceId]) => {
            const input = document.querySelector(
                `input[name="question_${questionId}"][value="${choiceId}"]`
            );
            if (input) input.checked = true;
        });
    }

    /**
     * Set loading state
     */
    setLoading(isLoading) {
        if (this.elements.form) {
            this.elements.form.classList.toggle('loading', isLoading);
        }
    }

    /**
     * Enable form
     */
    enableForm() {
        if (this.elements.form) {
            this.elements.form.querySelectorAll('input').forEach(input => {
                input.disabled = false;
            });
            if (this.elements.submitBtn) {
                this.elements.submitBtn.disabled = false;
                this.elements.submitBtn.textContent = 'Submit Quiz';
            }
        }
    }

    /**
     * Disable form
     */
    disableForm() {
        if (this.elements.form) {
            this.elements.form.querySelectorAll('input').forEach(input => {
                input.disabled = true;
            });
            if (this.elements.submitBtn) {
                this.elements.submitBtn.disabled = true;
            }
        }
    }

    /**
     * Update layout
     */
    updateLayout() {
        // Force layout recalculation for smooth animations
        if (this.elements.questionContainer) {
            this.elements.questionContainer.style.display = 'none';
            this.elements.questionContainer.offsetHeight; // Force reflow
            this.elements.questionContainer.style.display = '';
        }
    }
}
