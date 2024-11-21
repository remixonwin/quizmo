/**
 * Quiz State Module
 * Manages quiz state with optimized data structures and performance.
 */

export class QuizState {
    constructor() {
        // Use Map for O(1) access to answers
        this.answers = new Map();
        this.totalQuestions = 0;
        this.submitting = false;
        this.error = false;
        this.startTime = performance.now();

        // Cache DOM queries
        this._progressElement = document.getElementById('quiz-progress');
        this._submitButton = document.querySelector('button[type="submit"]');
    }

    /**
     * Initialize quiz state
     * @param {number} totalQuestions - Total number of questions
     */
    initialize(totalQuestions) {
        this.totalQuestions = totalQuestions;
        this.startTime = performance.now();
        this.updateProgress();
    }

    /**
     * Record an answer
     * @param {string} questionId - Question identifier
     * @param {string} answer - Selected answer
     */
    recordAnswer(questionId, answer) {
        this.answers.set(questionId, answer);
        this.updateProgress();

        // Auto-save to localStorage
        this._saveToLocalStorage();
    }

    /**
     * Get quiz progress
     * @returns {Object} Progress information
     */
    getProgress() {
        const answered = this.answers.size;
        const total = this.totalQuestions;
        const percentage = total ? Math.round((answered / total) * 100) : 0;

        return {
            answered,
            total,
            percentage,
            remaining: total - answered,
        };
    }

    /**
     * Update progress display
     */
    updateProgress() {
        if (!this._progressElement) return;

        const { answered, total, percentage } = this.getProgress();
        this._progressElement.textContent = `${answered}/${total} (${percentage}%)`;

        // Update submit button state
        if (this._submitButton) {
            this._submitButton.disabled = answered < total;
        }
    }

    /**
     * Get quiz duration in seconds
     * @returns {number} Quiz duration in seconds
     */
    getDuration() {
        return Math.floor((performance.now() - this.startTime) / 1000);
    }

    /**
     * Get all answers
     * @returns {Object} Answer map
     */
    getAnswers() {
        return Object.fromEntries(this.answers);
    }

    /**
     * Set submitting state
     * @param {boolean} state - New submitting state
     */
    setSubmitting(state) {
        this.submitting = state;
        if (this._submitButton) {
            this._submitButton.disabled = state;
        }
    }

    /**
     * Check if quiz is being submitted
     * @returns {boolean} Submitting state
     */
    isSubmitting() {
        return this.submitting;
    }

    /**
     * Set error state
     * @param {boolean} state - New error state
     */
    setError(state) {
        this.error = state;
    }

    /**
     * Check if quiz has error
     * @returns {boolean} Error state
     */
    hasError() {
        return this.error;
    }

    /**
     * Save current state to localStorage
     * @private
     */
    _saveToLocalStorage() {
        try {
            const state = {
                answers: Object.fromEntries(this.answers),
                timestamp: Date.now()
            };
            localStorage.setItem('quizState', JSON.stringify(state));
        } catch (error) {
            console.warn('Failed to save quiz state:', error);
        }
    }

    /**
     * Restore state from localStorage
     * @returns {boolean} True if state was restored
     */
    restoreFromLocalStorage() {
        try {
            const saved = localStorage.getItem('quizState');
            if (!saved) return false;

            const state = JSON.parse(saved);
            const timestamp = state.timestamp || 0;
            const maxAge = 30 * 60 * 1000; // 30 minutes

            // Clear expired state
            if (Date.now() - timestamp > maxAge) {
                localStorage.removeItem('quizState');
                return false;
            }

            // Restore answers
            this.answers = new Map(Object.entries(state.answers));
            this.updateProgress();
            return true;

        } catch (error) {
            console.warn('Failed to restore quiz state:', error);
            return false;
        }
    }

    /**
     * Clear quiz state
     */
    clear() {
        this.answers.clear();
        this.error = false;
        this.submitting = false;
        localStorage.removeItem('quizState');
        this.updateProgress();
    }
}
