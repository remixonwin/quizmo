/**
 * Quiz Application Entry Point
 * Optimized with progressive loading, state management, and performance enhancements.
 */

import { config } from './utils/config.js';
import { fetchQuizData, submitQuizAnswers, fetchQuestionBatch } from './utils/api.js';
import { Timer } from './modules/Timer.js';
import { QuizUI } from './modules/QuizUI.js';
import { QuizState } from './modules/QuizState.js';
import { QuestionLoader } from './modules/QuestionLoader.js';

class QuizApp {
    constructor() {
        this.ui = new QuizUI();
        this.state = new QuizState();
        this.timer = null;
        this.questionLoader = null;
        this.batchSize = config.questionBatchSize || 5;
        this.isSubmitting = false;
        this.debounceTimeout = null;
    }

    /**
     * Initialize the quiz application with progressive loading
     */
    async init() {
        try {
            // Initialize state from IndexedDB if available
            await this.state.restore();

            // Load initial quiz data
            const data = await fetchQuizData(window.quizDataUrl);
            this.state.initialize(data.questions.length);
            
            // Initialize question loader
            this.questionLoader = new QuestionLoader(this.batchSize);
            await this.questionLoader.initialize(data.questions);

            // Initialize timer if time limit exists
            if (window.quizTimeLimit) {
                this.timer = new Timer(window.quizTimeLimit);
                this.timer.start(
                    this.handleTimerTick.bind(this),
                    this.handleTimeUp.bind(this)
                );
            }

            // Setup intersection observer for progressive loading
            this.setupIntersectionObserver();

            // Bind events
            this.bindEvents();

            // Load first batch of questions
            await this.loadNextQuestionBatch();

        } catch (error) {
            console.error('Failed to initialize quiz:', error);
            this.ui.showError('Failed to load quiz. Please try again.');
            
            // Attempt state recovery
            if (await this.state.hasStoredState()) {
                await this.attemptStateRecovery();
            }
        }
    }

    /**
     * Setup intersection observer for progressive loading
     */
    setupIntersectionObserver() {
        const options = {
            root: null,
            rootMargin: '100px',
            threshold: 0.1
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadNextQuestionBatch();
                }
            });
        }, options);

        // Observe the loading trigger element
        const trigger = this.ui.elements.loadingTrigger;
        if (trigger) observer.observe(trigger);
    }

    /**
     * Load next batch of questions
     */
    async loadNextQuestionBatch() {
        if (this.questionLoader.isLoading || this.questionLoader.isComplete) return;

        try {
            const batch = await this.questionLoader.loadNextBatch();
            if (batch.length > 0) {
                await this.ui.renderQuestionBatch(batch);
                this.bindQuestionEvents(batch);
            }
        } catch (error) {
            console.error('Failed to load question batch:', error);
            this.ui.showError('Failed to load more questions. Please refresh.');
        }
    }

    /**
     * Bind event listeners with debouncing
     */
    bindEvents() {
        // Form submission
        const form = this.ui.elements.form;
        if (form) {
            form.addEventListener('submit', (e) => this.handleSubmit(e));
        }

        // Save state periodically
        setInterval(() => this.state.persist(), config.statePersistInterval || 30000);

        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.state.persist();
            }
        });

        // Handle before unload
        window.addEventListener('beforeunload', () => {
            this.state.persist();
        });
    }

    /**
     * Bind events for a batch of questions
     */
    bindQuestionEvents(questions) {
        questions.forEach(question => {
            const inputs = this.ui.getQuestionInputs(question.id);
            inputs.forEach(input => {
                input.addEventListener('change', (e) => this.handleAnswerChange(e));
            });
        });
    }

    /**
     * Handle answer change with debouncing
     */
    handleAnswerChange(event) {
        const { name, value } = event.target;
        
        // Clear existing timeout
        if (this.debounceTimeout) {
            clearTimeout(this.debounceTimeout);
        }

        // Debounce state update
        this.debounceTimeout = setTimeout(async () => {
            this.state.recordAnswer(name, value);
            await this.state.persist();
            this.ui.updateProgress(this.state.getProgress());
        }, config.debounceDelay || 300);
    }

    /**
     * Handle timer tick
     */
    handleTimerTick(remainingTime) {
        this.ui.updateTimer(remainingTime);
        
        // Save state on regular intervals
        if (remainingTime % 30 === 0) {
            this.state.persist();
        }
    }

    /**
     * Handle form submission with optimistic updates
     */
    async handleSubmit(event) {
        event.preventDefault();

        if (this.isSubmitting) return;

        try {
            this.isSubmitting = true;
            this.ui.setLoading(true);
            this.ui.disableForm();

            // Prepare submission data
            const formData = new FormData(event.target);
            const answers = this.state.getAllAnswers();
            
            // Optimistic update
            this.ui.showSubmitting();

            // Submit answers in batches
            const result = await submitQuizAnswers(formData, answers);

            if (this.timer) {
                this.timer.stop();
            }

            // Clear persisted state after successful submission
            await this.state.clear();
            
            this.ui.showResult(result);

        } catch (error) {
            console.error('Failed to submit quiz:', error);
            this.ui.showError('Failed to submit quiz. Please try again.');
            this.state.setError(true);
            
            // Persist state in case of error
            await this.state.persist();
        } finally {
            this.isSubmitting = false;
            this.ui.setLoading(false);
            this.ui.enableForm();
        }
    }

    /**
     * Attempt state recovery
     */
    async attemptStateRecovery() {
        try {
            const recovered = await this.state.recover();
            if (recovered) {
                this.ui.showRecoveryMessage('Previous state recovered successfully.');
                this.ui.restoreAnswers(this.state.getAllAnswers());
            }
        } catch (error) {
            console.error('Failed to recover state:', error);
            this.ui.showError('Failed to recover previous state.');
        }
    }
}

// Initialize quiz when DOM is ready with error boundary
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const quiz = new QuizApp();
        await quiz.init();
    } catch (error) {
        console.error('Critical initialization error:', error);
        // Show fallback UI
        document.body.innerHTML = `
            <div class="error-boundary">
                <h2>Failed to load quiz</h2>
                <p>Please refresh the page or try again later.</p>
                <button onclick="location.reload()">Refresh Page</button>
            </div>
        `;
    }
});
