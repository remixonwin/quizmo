/**
 * Timer Module
 * Handles quiz timing with high-precision and performance optimizations.
 */

import { config } from '../utils/config.js';

export class Timer {
    constructor(duration) {
        this.duration = duration * 1000; // Convert to milliseconds
        this.startTime = null;
        this.remaining = this.duration;
        this.rafId = null;
        this.lastTick = null;
        this.onTick = null;
        this.onTimeUp = null;
        this.isRunning = false;
        this.timerElement = document.querySelector(config.selectors.timer);
    }

    /**
     * Start the timer
     * @param {Function} onTick - Callback for each tick
     * @param {Function} onTimeUp - Callback when time is up
     */
    start(onTick, onTimeUp) {
        if (this.isRunning) return;

        this.onTick = onTick;
        this.onTimeUp = onTimeUp;
        this.startTime = performance.now();
        this.lastTick = this.startTime;
        this.isRunning = true;

        // Use performance.now() for high-precision timing
        this.tick();
    }

    /**
     * Stop the timer
     */
    stop() {
        if (!this.isRunning) return;

        this.isRunning = false;
        if (this.rafId) {
            cancelAnimationFrame(this.rafId);
            this.rafId = null;
        }
    }

    /**
     * Pause the timer
     */
    pause() {
        if (!this.isRunning) return;

        this.stop();
        this.remaining = Math.max(0, this.remaining - (performance.now() - this.lastTick));
    }

    /**
     * Resume the timer
     */
    resume() {
        if (this.isRunning) return;

        this.startTime = performance.now() - (this.duration - this.remaining);
        this.isRunning = true;
        this.tick();
    }

    /**
     * Get remaining time in seconds
     * @returns {number} Remaining time in seconds
     */
    getRemainingTime() {
        if (!this.isRunning) return this.remaining / 1000;
        
        const elapsed = performance.now() - this.startTime;
        return Math.max(0, (this.duration - elapsed) / 1000);
    }

    /**
     * Get elapsed time in seconds
     * @returns {number} Elapsed time in seconds
     */
    getElapsedTime() {
        if (!this.isRunning) return (this.duration - this.remaining) / 1000;
        
        return (performance.now() - this.startTime) / 1000;
    }

    /**
     * Update timer display
     */
    updateDisplay() {
        if (!this.timerElement) return;

        const minutes = Math.floor(this.getRemainingTime() / 60);
        const seconds = this.getRemainingTime() % 60;
        this.timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

        // Add warning class when less than a minute remains
        if (this.getRemainingTime() <= 60) {
            this.timerElement.classList.add(config.classes.warning);
        } else {
            this.timerElement.classList.remove(config.classes.warning);
        }
    }

    /**
     * Internal tick function using requestAnimationFrame
     * @private
     */
    tick() {
        if (!this.isRunning) return;

        const now = performance.now();
        const elapsed = now - this.startTime;
        this.lastTick = now;

        if (elapsed >= this.duration) {
            this.stop();
            this.remaining = 0;
            if (this.onTimeUp) {
                this.onTimeUp();
            }
            return;
        }

        // Throttle updates to once per second for performance
        if (Math.floor(elapsed / 1000) > Math.floor((elapsed - 16.67) / 1000)) {
            this.updateDisplay();
            if (this.onTick) {
                this.onTick(this.getRemainingTime());
            }
        }

        this.rafId = requestAnimationFrame(() => this.tick());
    }
}
