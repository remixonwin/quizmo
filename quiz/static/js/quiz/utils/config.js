/**
 * Configuration Module
 * Environment-aware configuration with performance optimizations
 */

const ENV = process.env.NODE_ENV || 'development';

// Base configuration
const baseConfig = {
    // API endpoints
    endpoints: {
        quiz: '',
        submit: 'submit/',
        results: 'results/',
        batch: 'batch/'
    },

    // Cache settings
    cache: {
        ttl: 5 * 60 * 1000, // 5 minutes
        prefix: 'quiz_cache_',
        maxEntries: 100
    },

    // Performance settings
    performance: {
        questionBatchSize: 5,
        debounceDelay: 300,
        statePersistInterval: 30000,
        maxRetries: 3,
        retryDelay: 1000,
        loadingTriggerOffset: '100px'
    },

    // UI settings
    ui: {
        animations: {
            duration: 300,
            easing: 'ease-in-out'
        },
        classes: {
            active: 'active',
            loading: 'loading',
            error: 'error',
            success: 'success'
        },
        selectors: {
            form: '#quiz-form',
            progress: '#quiz-progress',
            timer: '#quiz-timer',
            submit: '#submit-btn',
            questions: '#question-container',
            loading: '#loading-trigger',
            message: '#message-container'
        }
    },

    // Timer settings
    timer: {
        updateInterval: 1000,
        warningThreshold: 60, // seconds
        criticalThreshold: 30 // seconds
    },

    // Storage settings
    storage: {
        prefix: 'quiz_state_',
        version: '1.0.0',
        compression: true
    }
};

// Environment-specific configurations
const envConfigs = {
    development: {
        debug: true,
        api: {
            baseUrl: 'http://localhost:8000',
            timeout: 10000
        },
        performance: {
            questionBatchSize: 3, // Smaller batch size for development
            debounceDelay: 100 // Faster debounce for development
        }
    },
    test: {
        debug: true,
        api: {
            baseUrl: 'http://test-api.example.com',
            timeout: 5000
        }
    },
    production: {
        debug: false,
        api: {
            baseUrl: 'https://api.example.com',
            timeout: 15000
        },
        cache: {
            ttl: 15 * 60 * 1000 // 15 minutes for production
        }
    }
};

// Merge configurations
const config = {
    ...baseConfig,
    ...envConfigs[ENV],
    env: ENV
};

// Freeze configuration to prevent modifications
Object.freeze(config);

/**
 * Get configuration value
 * @param {string} path - Dot-notation path to config value
 * @param {*} defaultValue - Default value if path doesn't exist
 */
export function get(path, defaultValue = null) {
    return path.split('.').reduce((obj, key) => 
        (obj && obj[key] !== undefined) ? obj[key] : defaultValue, 
        config
    );
}

/**
 * Check if running in development mode
 */
export function isDevelopment() {
    return ENV === 'development';
}

/**
 * Check if running in test mode
 */
export function isTest() {
    return ENV === 'test';
}

/**
 * Check if running in production mode
 */
export function isProduction() {
    return ENV === 'production';
}

/**
 * Get environment-specific API URL
 * @param {string} endpoint - API endpoint
 */
export function getApiUrl(endpoint) {
    const baseUrl = get('api.baseUrl').replace(/\/$/, '');
    const path = endpoint.replace(/^\//, '');
    return `${baseUrl}/${path}`;
}

/**
 * Get cache TTL for given key
 * @param {string} key - Cache key
 */
export function getCacheTTL(key) {
    // Allow for key-specific TTL overrides
    const overrides = {
        quiz_data: 10 * 60 * 1000, // 10 minutes for quiz data
        user_progress: 5 * 60 * 1000 // 5 minutes for user progress
    };
    return overrides[key] || get('cache.ttl');
}

// Export configuration
export { config as default };
