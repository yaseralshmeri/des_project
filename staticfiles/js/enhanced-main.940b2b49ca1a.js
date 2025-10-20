/**
 * Enhanced Main JavaScript for University Management System
 * ملف الجافاسكريبت الرئيسي المحسن لنظام إدارة الجامعة
 * 
 * This file contains all the enhanced JavaScript functionality
 * with improved performance, error handling, and user experience.
 */

// Global variables and configurations
const UniversitySystem = {
    config: {
        apiBaseUrl: '/api/v1/',
        refreshInterval: 30000, // 30 seconds
        animationDuration: 300,
        debounceDelay: 500,
    },
    
    cache: new Map(),
    
    utils: {
        // Debounce function for search and other frequent operations
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        // Format numbers for Arabic locale
        formatNumber: function(number) {
            return new Intl.NumberFormat('ar-SA').format(number);
        },
        
        // Format dates for Arabic locale
        formatDate: function(date) {
            return new Intl.DateTimeFormat('ar-SA', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            }).format(new Date(date));
        },
        
        // Show loading state
        showLoading: function(element) {
            const loader = '<div class="d-flex justify-content-center py-3"><div class="loading"></div></div>';
            $(element).html(loader);
        },
        
        // Show toast notification
        showToast: function(message, type = 'info', duration = 5000) {
            const toastId = 'toast-' + Date.now();
            const toastHtml = `
                <div class="toast align-items-center text-white bg-${type} border-0" role="alert" id="${toastId}">
                    <div class="d-flex">
                        <div class="toast-body">${message}</div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                    </div>
                </div>
            `;
            
            // Create toast container if it doesn't exist
            if (!$('#toast-container').length) {
                $('body').append('<div id="toast-container" class="toast-container position-fixed top-0 end-0 p-3"></div>');
            }
            
            $('#toast-container').append(toastHtml);
            const toast = new bootstrap.Toast(document.getElementById(toastId), {
                delay: duration
            });
            toast.show();
            
            // Remove toast from DOM after it's hidden
            $('#' + toastId).on('hidden.bs.toast', function() {
                $(this).remove();
            });
        },
        
        // API request helper with error handling
        apiRequest: function(url, options = {}) {
            const defaultOptions = {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val() || '',
                },
            };
            
            const finalOptions = { ...defaultOptions, ...options };
            
            return fetch(url, finalOptions)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .catch(error => {
                    console.error('API Request Error:', error);
                    UniversitySystem.utils.showToast('حدث خطأ في الاتصال بالخادم', 'danger');
                    throw error;
                });
        }
    }
};

// DOM Ready initialization
$(document).ready(function() {
    initializeSystem();
});

/**
 * Initialize the system with all necessary components
 */
function initializeSystem() {
    setupNavigationEnhancements();
    setupNotificationSystem();
    setupSearchFunctionality();
    setupFormEnhancements();
    setupTableEnhancements();
    setupDashboardRefresh();
    setupAnimations();
    setupTooltips();
    setupResponsiveEnhancements();
}

/**
 * Navigation enhancements and interactions
 */
function setupNavigationEnhancements() {
    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(event) {
        const target = $(this.getAttribute('href'));
        if (target.length) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 80
            }, 800, 'easeInOutExpo');
        }
    });
    
    // Active navigation highlighting
    const currentPath = window.location.pathname;
    $('.nav-link').each(function() {
        const href = $(this).attr('href');
        if (href && currentPath.includes(href) && href !== '/') {
            $(this).addClass('active');
        }
    });
    
    // Navbar scroll effects
    let lastScrollTop = 0;
    $(window).scroll(function() {
        const scrollTop = $(this).scrollTop();
        const navbar = $('.navbar');
        
        if (scrollTop > 100) {
            navbar.addClass('navbar-scrolled');
        } else {
            navbar.removeClass('navbar-scrolled');
        }
        
        // Hide/show navbar on scroll (mobile optimization)
        if ($(window).width() <= 768) {
            if (scrollTop > lastScrollTop && scrollTop > 200) {
                navbar.addClass('navbar-hidden');
            } else {
                navbar.removeClass('navbar-hidden');
            }
        }
        
        lastScrollTop = scrollTop;
    });
}

/**
 * Real-time notification system
 */
function setupNotificationSystem() {
    // Load notifications on dropdown show
    $(document).on('show.bs.dropdown', '.notification-dropdown', function() {
        loadNotifications();
    });
    
    // Mark notification as read when clicked
    $(document).on('click', '.notification-item', function() {
        const notificationId = $(this).data('id');
        if (notificationId) {
            markNotificationAsRead(notificationId);
        }
    });
    
    // Auto-refresh notifications
    setInterval(refreshNotificationCount, UniversitySystem.config.refreshInterval);
}

/**
 * Load and display notifications
 */
function loadNotifications() {
    const container = $('#notifications-list');
    UniversitySystem.utils.showLoading(container);
    
    UniversitySystem.utils.apiRequest('/api/notifications/')
        .then(data => {
            if (data.success) {
                displayNotifications(data.notifications);
            } else {
                container.html('<div class="text-center text-muted py-3">لا توجد إشعارات</div>');
            }
        })
        .catch(error => {
            container.html('<div class="text-center text-danger py-3">خطأ في تحميل الإشعارات</div>');
        });
}

/**
 * Display notifications in the dropdown
 */
function displayNotifications(notifications) {
    const container = $('#notifications-list');
    
    if (!notifications || notifications.length === 0) {
        container.html('<div class="text-center text-muted py-3">لا توجد إشعارات جديدة</div>');
        return;
    }
    
    let html = '';
    notifications.forEach(notification => {
        const timeAgo = getTimeAgo(notification.created_at);
        const iconClass = getNotificationIcon(notification.type);
        
        html += `
            <div class="notification-item border-bottom py-2" data-id="${notification.id}">
                <div class="d-flex">
                    <div class="flex-shrink-0">
                        <i class="fas ${iconClass} text-primary"></i>
                    </div>
                    <div class="flex-grow-1 ms-2">
                        <small class="text-muted">${timeAgo}</small>
                        <p class="mb-1">${notification.message}</p>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.html(html);
}

/**
 * Mark notification as read
 */
function markNotificationAsRead(notificationId) {
    UniversitySystem.utils.apiRequest(`/api/notifications/${notificationId}/read/`, {
        method: 'POST'
    }).then(data => {
        if (data.success) {
            updateNotificationCount();
        }
    });
}

/**
 * Refresh notification count
 */
function refreshNotificationCount() {
    UniversitySystem.utils.apiRequest('/api/notifications/count/')
        .then(data => {
            if (data.success) {
                $('#notification-count').text(data.count);
                if (data.count > 0) {
                    $('#notification-count').show();
                } else {
                    $('#notification-count').hide();
                }
            }
        })
        .catch(error => {
            console.error('Failed to refresh notification count:', error);
        });
}

/**
 * Global search functionality
 */
function setupSearchFunctionality() {
    const searchInput = $('#global-search');
    const searchResults = $('#search-results');
    
    if (searchInput.length) {
        // Debounced search function
        const debouncedSearch = UniversitySystem.utils.debounce(performSearch, UniversitySystem.config.debounceDelay);
        
        searchInput.on('input', function() {
            const query = $(this).val().trim();
            if (query.length >= 2) {
                debouncedSearch(query);
            } else {
                hideSearchResults();
            }
        });
        
        // Hide search results when clicking outside
        $(document).on('click', function(e) {
            if (!$(e.target).closest('#search-container').length) {
                hideSearchResults();
            }
        });
    }
}

/**
 * Perform search and display results
 */
function performSearch(query) {
    const searchResults = $('#search-results');
    searchResults.show();
    UniversitySystem.utils.showLoading(searchResults);
    
    UniversitySystem.utils.apiRequest(`/api/search/?q=${encodeURIComponent(query)}`)
        .then(data => {
            if (data.success) {
                displaySearchResults(data.results);
            } else {
                searchResults.html('<div class="text-center text-muted py-3">لا توجد نتائج</div>');
            }
        })
        .catch(error => {
            searchResults.html('<div class="text-center text-danger py-3">خطأ في البحث</div>');
        });
}

/**
 * Display search results
 */
function displaySearchResults(results) {
    const container = $('#search-results');
    
    if (!results || results.length === 0) {
        container.html('<div class="text-center text-muted py-3">لا توجد نتائج</div>');
        return;
    }
    
    let html = '<div class="list-group list-group-flush">';
    results.forEach(result => {
        const iconClass = getResultIcon(result.type);
        html += `
            <a href="${result.url}" class="list-group-item list-group-item-action">
                <div class="d-flex align-items-center">
                    <i class="fas ${iconClass} me-2 text-primary"></i>
                    <div>
                        <div class="fw-bold">${result.title}</div>
                        <small class="text-muted">${result.subtitle}</small>
                    </div>
                </div>
            </a>
        `;
    });
    html += '</div>';
    
    container.html(html);
}

/**
 * Hide search results
 */
function hideSearchResults() {
    $('#search-results').hide();
}

/**
 * Form enhancements and validation
 */
function setupFormEnhancements() {
    // Real-time form validation
    $('.form-control').on('blur', function() {
        validateField($(this));
    });
    
    // Enhanced form submission with loading states
    $('form').on('submit', function() {
        const submitBtn = $(this).find('button[type="submit"]');
        const originalText = submitBtn.html();
        
        submitBtn.prop('disabled', true)
                 .html('<i class="fas fa-spinner fa-spin me-2"></i>جاري المعالجة...');
        
        // Reset button after 30 seconds if form hasn't completed
        setTimeout(() => {
            submitBtn.prop('disabled', false).html(originalText);
        }, 30000);
    });
    
    // Auto-save functionality for long forms
    $('form[data-autosave]').each(function() {
        setupAutoSave($(this));
    });
    
    // Password strength indicator
    $('input[type="password"]').on('input', function() {
        const password = $(this).val();
        const strength = calculatePasswordStrength(password);
        displayPasswordStrength($(this), strength);
    });
}

/**
 * Validate individual form field
 */
function validateField(field) {
    const value = field.val().trim();
    const rules = field.data('validate');
    
    if (!rules) return;
    
    let isValid = true;
    let errorMessage = '';
    
    // Required validation
    if (rules.includes('required') && !value) {
        isValid = false;
        errorMessage = 'هذا الحقل مطلوب';
    }
    
    // Email validation
    if (rules.includes('email') && value && !isValidEmail(value)) {
        isValid = false;
        errorMessage = 'يرجى إدخال بريد إلكتروني صحيح';
    }
    
    // Phone validation
    if (rules.includes('phone') && value && !isValidPhone(value)) {
        isValid = false;
        errorMessage = 'يرجى إدخال رقم هاتف صحيح';
    }
    
    // Display validation result
    displayFieldValidation(field, isValid, errorMessage);
}

/**
 * Display field validation result
 */
function displayFieldValidation(field, isValid, errorMessage) {
    field.removeClass('is-valid is-invalid');
    field.siblings('.invalid-feedback').remove();
    
    if (isValid) {
        field.addClass('is-valid');
    } else {
        field.addClass('is-invalid');
        field.after(`<div class="invalid-feedback">${errorMessage}</div>`);
    }
}

/**
 * Table enhancements
 */
function setupTableEnhancements() {
    // Sortable tables
    $('.table-sortable th[data-sort]').on('click', function() {
        const column = $(this).data('sort');
        const table = $(this).closest('table');
        sortTable(table, column);
    });
    
    // Row selection
    $('.table-selectable').each(function() {
        setupTableSelection($(this));
    });
    
    // Responsive table enhancements
    $('.table-responsive').each(function() {
        enhanceResponsiveTable($(this));
    });
    
    // Export functionality
    $('.btn-export').on('click', function() {
        const format = $(this).data('format');
        const table = $(this).data('table');
        exportTable(table, format);
    });
}

/**
 * Dashboard auto-refresh
 */
function setupDashboardRefresh() {
    if ($('.dashboard-stat').length) {
        // Refresh dashboard stats every 5 minutes
        setInterval(refreshDashboardStats, 300000);
        
        // Initial animation for statistics
        animateDashboardStats();
    }
}

/**
 * Refresh dashboard statistics
 */
function refreshDashboardStats() {
    UniversitySystem.utils.apiRequest('/api/dashboard-stats/')
        .then(data => {
            if (data.success) {
                updateDashboardStats(data.stats);
            }
        })
        .catch(error => {
            console.error('Failed to refresh dashboard stats:', error);
        });
}

/**
 * Update dashboard statistics display
 */
function updateDashboardStats(stats) {
    Object.keys(stats).forEach(key => {
        const element = $(`#${key}`);
        if (element.length) {
            const currentValue = parseInt(element.text().replace(/[^\d]/g, ''));
            const newValue = stats[key];
            
            if (currentValue !== newValue) {
                animateNumber(element, newValue);
            }
        }
    });
}

/**
 * Animate dashboard statistics on load
 */
function animateDashboardStats() {
    $('.dashboard-stat h3').each(function() {
        const element = $(this);
        const finalValue = parseInt(element.text().replace(/[^\d]/g, ''));
        
        if (finalValue) {
            element.text('0');
            animateNumber(element, finalValue, 2000);
        }
    });
}

/**
 * Animate number counter
 */
function animateNumber(element, targetNumber, duration = 1000) {
    $({ counter: 0 }).animate({ counter: targetNumber }, {
        duration: duration,
        easing: 'swing',
        step: function() {
            element.text(UniversitySystem.utils.formatNumber(Math.ceil(this.counter)));
        },
        complete: function() {
            element.text(UniversitySystem.utils.formatNumber(targetNumber));
        }
    });
}

/**
 * Setup animations and transitions
 */
function setupAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe all elements with animation classes
    document.querySelectorAll('.fade-up, .slide-in-left, .slide-in-right').forEach(el => {
        observer.observe(el);
    });
    
    // Card hover effects
    $('.card').hover(
        function() { $(this).addClass('card-hover'); },
        function() { $(this).removeClass('card-hover'); }
    );
    
    // Button ripple effect
    $('.btn').on('click', function(e) {
        const btn = $(this);
        const ripple = $('<span class="btn-ripple"></span>');
        
        btn.append(ripple);
        
        const x = e.pageX - btn.offset().left;
        const y = e.pageY - btn.offset().top;
        
        ripple.css({
            left: x + 'px',
            top: y + 'px'
        }).addClass('ripple-animate');
        
        setTimeout(() => ripple.remove(), 600);
    });
}

/**
 * Setup tooltips and popovers
 */
function setupTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Responsive enhancements
 */
function setupResponsiveEnhancements() {
    // Mobile menu enhancements
    $('.navbar-toggler').on('click', function() {
        $(this).toggleClass('active');
    });
    
    // Responsive table handling
    $(window).on('resize', function() {
        handleResponsiveTables();
    });
    
    // Touch gestures for mobile
    if ('ontouchstart' in window) {
        setupTouchGestures();
    }
    
    // Initial responsive setup
    handleResponsiveTables();
}

/**
 * Handle responsive table behavior
 */
function handleResponsiveTables() {
    $('.table-responsive').each(function() {
        const table = $(this);
        const windowWidth = $(window).width();
        
        if (windowWidth < 768) {
            table.addClass('table-mobile');
        } else {
            table.removeClass('table-mobile');
        }
    });
}

/**
 * Utility functions
 */

// Get time ago string
function getTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'منذ لحظات';
    if (diffInSeconds < 3600) return `منذ ${Math.floor(diffInSeconds / 60)} دقيقة`;
    if (diffInSeconds < 86400) return `منذ ${Math.floor(diffInSeconds / 3600)} ساعة`;
    return `منذ ${Math.floor(diffInSeconds / 86400)} يوم`;
}

// Get notification icon based on type
function getNotificationIcon(type) {
    const icons = {
        'info': 'fa-info-circle',
        'success': 'fa-check-circle',
        'warning': 'fa-exclamation-triangle',
        'error': 'fa-times-circle',
        'grade': 'fa-chart-bar',
        'payment': 'fa-credit-card',
        'assignment': 'fa-tasks'
    };
    return icons[type] || 'fa-bell';
}

// Get search result icon based on type
function getResultIcon(type) {
    const icons = {
        'user': 'fa-user',
        'course': 'fa-book',
        'department': 'fa-building',
        'payment': 'fa-credit-card'
    };
    return icons[type] || 'fa-search';
}

// Email validation
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Phone validation (Saudi format)
function isValidPhone(phone) {
    const phoneRegex = /^(\+966|966|0)?[5][0-9]{8}$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
}

// Password strength calculation
function calculatePasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength += 1;
    if (/[a-z]/.test(password)) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[0-9]/.test(password)) strength += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;
    
    return strength;
}

// Display password strength indicator
function displayPasswordStrength(field, strength) {
    const strengthLabels = ['ضعيف جداً', 'ضعيف', 'متوسط', 'قوي', 'قوي جداً'];
    const strengthColors = ['danger', 'warning', 'info', 'success', 'success'];
    
    let indicator = field.siblings('.password-strength');
    if (!indicator.length) {
        field.after('<div class="password-strength mt-1"></div>');
        indicator = field.siblings('.password-strength');
    }
    
    const strengthClass = strengthColors[strength - 1] || 'secondary';
    const strengthLabel = strengthLabels[strength - 1] || '';
    
    indicator.html(`
        <div class="progress" style="height: 5px;">
            <div class="progress-bar bg-${strengthClass}" style="width: ${(strength / 5) * 100}%"></div>
        </div>
        <small class="text-${strengthClass}">${strengthLabel}</small>
    `);
}

// jQuery easing functions
$.easing.easeInOutExpo = function (x, t, b, c, d) {
    if (t==0) return b;
    if (t==d) return b+c;
    if ((t/=d/2) < 1) return c/2 * Math.pow(2, 10 * (t - 1)) + b;
    return c/2 * (-Math.pow(2, -10 * --t) + 2) + b;
};

// Export to global scope for external access
window.UniversitySystem = UniversitySystem;