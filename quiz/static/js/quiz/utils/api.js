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

    // Prepare request options
    const requestOptions = {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
            ...options.headers
        },
        credentials: 'same-origin'
    };

    // Implement retry logic
    let lastError;
    for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
        try {
            const response = await fetch(url, requestOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Cache successful GET requests
            if (useCache && options.method === 'GET') {
                await cacheData(cacheKey, data);
            }
            
            return data;
        } catch (error) {
            lastError = error;
            console.warn(`API request attempt ${attempt + 1} failed:`, error);
            
            if (attempt < MAX_RETRIES - 1) {
                await delay(RETRY_DELAY * Math.pow(2, attempt));
            }
        }
    }

    throw new Error(`API request failed after ${MAX_RETRIES} attempts: ${lastError.message}`);
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
 * Get CSRF token from cookie
 */
function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Delay helper for retry logic
 */
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
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
 * Submit quiz answers with optimistic updates
 */
export async function submitQuizAnswers(formData, answers) {
    const data = {
        answers: Object.fromEntries(formData),
        metadata: {
            submittedAt: new Date().toISOString(),
            timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            userAgent: navigator.userAgent
        }
    };

    return apiRequest(config.endpoints.submit, {
        method: 'POST',
        body: JSON.stringify(data)
    }, false);
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

// Initialize API module
initApi();
