/**
 * Question Loader Module
 * Handles progressive loading of quiz questions
 */

export class QuestionLoader {
    constructor(batchSize = 5) {
        this.batchSize = batchSize;
        this.questions = [];
        this.currentIndex = 0;
        this.isLoading = false;
        this.isComplete = false;
        this.loadedQuestions = new Set();
    }

    /**
     * Initialize the loader with questions
     */
    async initialize(questions) {
        this.questions = questions;
        this.currentIndex = 0;
        this.isComplete = false;
        this.loadedQuestions.clear();
    }

    /**
     * Load next batch of questions
     */
    async loadNextBatch() {
        if (this.isLoading || this.isComplete) {
            return [];
        }

        try {
            this.isLoading = true;

            const batch = [];
            const endIndex = Math.min(this.currentIndex + this.batchSize, this.questions.length);

            for (let i = this.currentIndex; i < endIndex; i++) {
                const question = this.questions[i];
                if (!this.loadedQuestions.has(question.id)) {
                    batch.push(question);
                    this.loadedQuestions.add(question.id);
                }
            }

            this.currentIndex = endIndex;
            this.isComplete = this.currentIndex >= this.questions.length;

            return batch;

        } catch (error) {
            console.error('Error loading question batch:', error);
            throw error;
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Check if all questions are loaded
     */
    isAllQuestionsLoaded() {
        return this.loadedQuestions.size === this.questions.length;
    }

    /**
     * Get loading progress
     */
    getProgress() {
        return {
            loaded: this.loadedQuestions.size,
            total: this.questions.length,
            percentage: (this.loadedQuestions.size / this.questions.length) * 100
        };
    }

    /**
     * Reset loader state
     */
    reset() {
        this.currentIndex = 0;
        this.isComplete = false;
        this.isLoading = false;
        this.loadedQuestions.clear();
    }
}
