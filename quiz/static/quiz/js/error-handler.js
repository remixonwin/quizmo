// Error handling and reporting
class ErrorHandler {
    constructor() {
        this.setupGlobalErrorHandler();
        this.setupPromiseErrorHandler();
        this.setupConsoleOverride();
        this.setupNotifications();
    }

    setupGlobalErrorHandler() {
        window.onerror = (message, url, line, column, error) => {
            this.handleError({
                type: 'Global Error',
                message: message,
                url: url,
                line: line,
                column: column,
                stack: error ? error.stack : 'No stack trace available'
            });
            return false; // Let the error propagate
        };
    }

    setupPromiseErrorHandler() {
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError({
                type: 'Unhandled Promise Rejection',
                message: `${event.reason}`,
                url: window.location.href,
                stack: event.reason.stack || 'No stack trace available'
            });
        });
    }

    setupConsoleOverride() {
        const originalError = console.error;
        console.error = (...args) => {
            this.handleError({
                type: 'Console Error',
                message: args.map(arg => String(arg)).join(' '),
                url: window.location.href,
                stack: new Error().stack
            });
            originalError.apply(console, args);
        };
    }

    setupNotifications() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('error-notifications')) {
            const container = document.createElement('div');
            container.id = 'error-notifications';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 350px;
            `;
            document.body.appendChild(container);
        }
    }

    showNotification(message, type = 'error') {
        const container = document.getElementById('error-notifications');
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : 'warning'} alert-dismissible fade show`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        container.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 150);
        }, 5000);
    }

    async handleError(errorData) {
        // Show notification
        this.showNotification(`${errorData.type}: ${errorData.message}`);

        // Log to server
        try {
            const response = await fetch('/quiz/log-browser-error/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(errorData)
            });

            if (!response.ok) {
                console.warn('Failed to log error:', await response.text());
            }
        } catch (e) {
            console.warn('Error while logging error:', e);
        }
    }
}

// Initialize error handler
document.addEventListener('DOMContentLoaded', () => {
    window.errorHandler = new ErrorHandler();
    console.log('Error handler initialized with notifications');
});
