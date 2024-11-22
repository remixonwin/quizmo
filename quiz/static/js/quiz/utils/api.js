/**
 * API Utilities
 * Optimized API interactions with caching, retries, and error handling
 */

import { config } from './config.js';

// Cache configuration
const CACHE_PREFIX = 'quiz_cache_';
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

/**
 * API request wrapper with caching and retries
 */
async function apiRequest(url, options = {}, useCache = true) {
    const cacheKey = `${CACHE_PREFIX}${url}`;
    
    // Check cache first if enabled
    if (useCache && options.method === 'GET') {
        const cachedData = await getCachedData(cacheKey);
        if (cachedData) return cachedData;
    }

    // Prepare request options with CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const requestOptions = {
        ...options,
        headers: {
            'X-CSRFToken': csrfToken,
            ...options.headers
        },
        credentials: 'same-origin'
    };

    // Implement retry logic
    let lastError;
    for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
        try {
            const response = await fetch(url, requestOptions);
            
            // Handle redirects
            if (response.redirected) {
                window.location.href = response.url;
                return;
            }
            
            // Handle JSON responses
            if (response.headers.get('content-type')?.includes('application/json')) {
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.error || `HTTP error! status: ${response.status}`);
                }
                return data;
            }
            
            // Handle non-JSON responses
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return response;
            
        } catch (error) {
            console.error(`Attempt ${attempt + 1} failed:`, error);
            lastError = error;
            if (attempt < MAX_RETRIES - 1) {
                await delay(RETRY_DELAY * Math.pow(2, attempt));
            }
        }
    }
    
    throw lastError;
}

/**
 * Cache data in localStorage with TTL
 */
async function cacheData(key, data) {
    try {
        const cacheEntry = {
            data,
            timestamp: Date.now(),
            ttl: CACHE_TTL
        };
        localStorage.setItem(key, JSON.stringify(cacheEntry));
    } catch (error) {
        console.warn('Failed to cache data:', error);
    }
}

/**
 * Get cached data if valid
 */
async function getCachedData(key) {
    try {
        const cached = localStorage.getItem(key);
        if (!cached) return null;

        const entry = JSON.parse(cached);
        const age = Date.now() - entry.timestamp;

        if (age < entry.ttl) {
            return entry.data;
        } else {
            localStorage.removeItem(key);
            return null;
        }
    } catch (error) {
        console.warn('Failed to retrieve cached data:', error);
        return null;
    }
}

/**
 * Clear expired cache entries
 */
function clearExpiredCache() {
    try {
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key.startsWith(CACHE_PREFIX)) {
                const cached = localStorage.getItem(key);
                if (cached) {
                    const entry = JSON.parse(cached);
                    const age = Date.now() - entry.timestamp;
                    if (age >= entry.ttl) {
                        localStorage.removeItem(key);
                    }
                }
            }
        }
    } catch (error) {
        console.warn('Failed to clear expired cache:', error);
    }
}

/**
 * Submit quiz answers
 */
export async function submitQuizAnswers(formData) {
    const form = formData.target;
    const quizId = form.dataset.quizId;
    
    // Convert form data to array of answers
    const answers = [];
    for (const [key, value] of new FormData(form).entries()) {
        if (key.startsWith('question_')) {
            const questionId = parseInt(key.replace('question_', ''));
            answers.push({
                question_id: questionId,
                choice_id: parseInt(value)
            });
        }
    }

    // Submit answers using form data
    const submitUrl = form.action;
    const submitData = new FormData();
    
    // Add CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    submitData.append('csrfmiddlewaretoken', csrfToken);
    
    // Add answers as form data
    answers.forEach((answer, index) => {
        submitData.append(`question_${answer.question_id}`, answer.choice_id);
    });

    return apiRequest(submitUrl, {
        method: 'POST',
        body: submitData
    }, false);
}

/**
 * Fetch quiz data with caching
 */
export async function fetchQuizData(url) {
    return apiRequest(url, { method: 'GET' });
}

/**
 * Fetch question batch
 */
export async function fetchQuestionBatch(url, batchNumber, batchSize) {
    const params = new URLSearchParams({
        batch: batchNumber,
        size: batchSize
    });
    
    return apiRequest(`${url}?${params}`, { 
        method: 'GET',
        headers: {
            'X-Batch-Request': 'true'
        }
    });
}

/**
 * Initialize API module
 */
export function initApi() {
    // Clear expired cache entries periodically
    setInterval(clearExpiredCache, 60000); // Every minute
    
    // Clear expired cache on load
    clearExpiredCache();
}

// Helper functions
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Export functions
export { apiRequest, getCsrfToken };

// Initialize API module
initApi();
