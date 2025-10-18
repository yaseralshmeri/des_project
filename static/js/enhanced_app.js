/**
 * Enhanced University Management System JavaScript
 * تحسينات شاملة لواجهة نظام إدارة الجامعة
 */

class UniversityApp {
    constructor() {
        this.initializeApp();
        this.bindEvents();
        this.setupNotifications();
        this.setupTheme();
        this.setupAnalytics();
    }

    /**
     * Initialize the application
     */
    initializeApp() {
        console.log('🎓 University Management System - Enhanced Version');
        
        // Set up CSRF token for AJAX requests
        this.setupCSRF();
        
        // Initialize tooltips and popovers
        this.initializeBootstrapComponents();
        
        // Set up real-time features
        this.setupRealTimeFeatures();
        
        // Initialize performance monitoring
        this.initializePerformanceMonitoring();
    }

    /**
     * Set up CSRF token for AJAX requests
     */
    setupCSRF() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (csrfToken) {
            // Set default CSRF token for all AJAX requests
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrfToken);
                    }
                }
            });
        }
    }

    /**
     * Initialize Bootstrap components
     */
    initializeBootstrapComponents() {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Initialize popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });

        // Initialize modals with enhanced features
        const modalElements = document.querySelectorAll('.modal');
        modalElements.forEach(modal => {
            modal.addEventListener('show.bs.modal', this.handleModalShow.bind(this));
            modal.addEventListener('hidden.bs.modal', this.handleModalHidden.bind(this));
        });
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Enhanced search functionality
        this.setupEnhancedSearch();
        
        // Form validation and submission
        this.setupFormHandling();
        
        // Table enhancements
        this.setupTableEnhancements();
        
        // Navigation enhancements
        this.setupNavigationEnhancements();
        
        // File upload enhancements
        this.setupFileUploadEnhancements();
    }

    /**
     * Setup enhanced search functionality
     */
    setupEnhancedSearch() {
        const searchInputs = document.querySelectorAll('.search-enhanced');
        
        searchInputs.forEach(input => {
            let searchTimeout;
            
            input.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.performSearch(e.target.value, e.target.dataset.searchTarget);
                }, 300);
            });
            
            // Add search suggestions
            this.setupSearchSuggestions(input);
        });
    }

    /**
     * Perform enhanced search with filters
     */
    performSearch(query, target) {
        if (!query || query.length < 2) {
            this.clearSearchResults(target);
            return;
        }

        const searchData = {
            query: query,
            target: target,
        };

        this.showSearchLoading(target);

        fetch('/api/v1/search/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify(searchData)
        })
        .then(response => response.json())
        .then(data => {
            this.displaySearchResults(data, target);
        })
        .catch(error => {
            console.error('Search error:', error);
            this.showSearchError(target);
        })
        .finally(() => {
            this.hideSearchLoading(target);
        });
    }

    /**
     * Setup form handling with enhanced validation
     */
    setupFormHandling() {
        const forms = document.querySelectorAll('.form-enhanced');
        
        forms.forEach(form => {
            // Real-time validation
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('blur', (e) => {
                    this.validateField(e.target);
                });
                
                input.addEventListener('input', (e) => {
                    this.clearFieldError(e.target);
                });
            });
            
            // Enhanced form submission
            form.addEventListener('submit', (e) => {
                this.handleFormSubmission(e);
            });
        });
    }

    /**
     * Validate individual form field
     */
    validateField(field) {
        const value = field.value.trim();
        const fieldType = field.type;
        const isRequired = field.hasAttribute('required');
        
        let isValid = true;
        let errorMessage = '';
        
        // Required field validation
        if (isRequired && !value) {
            isValid = false;
            errorMessage = 'هذا الحقل مطلوب';
        }
        
        // Email validation
        if (fieldType === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'يرجى إدخال بريد إلكتروني صحيح';
            }
        }
        
        // Phone validation
        if (field.classList.contains('phone-input') && value) {
            const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
            if (!phoneRegex.test(value)) {
                isValid = false;
                errorMessage = 'يرجى إدخال رقم هاتف صحيح';
            }
        }
        
        // Password strength validation
        if (fieldType === 'password' && value) {
            const strength = this.calculatePasswordStrength(value);
            if (strength < 3) {
                isValid = false;
                errorMessage = 'كلمة المرور ضعيفة. يرجى استخدام 8 أحرف على الأقل مع أحرف كبيرة وصغيرة وأرقام';
            }
            this.updatePasswordStrengthIndicator(field, strength);
        }
        
        if (isValid) {
            this.showFieldSuccess(field);
        } else {
            this.showFieldError(field, errorMessage);
        }
        
        return isValid;
    }

    /**
     * Calculate password strength
     */
    calculatePasswordStrength(password) {
        let strength = 0;
        
        if (password.length >= 8) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^A-Za-z0-9]/.test(password)) strength++;
        
        return strength;
    }

    /**
     * Enhanced form submission with loading states
     */
    handleFormSubmission(e) {
        const form = e.target;
        const submitButton = form.querySelector('button[type="submit"]');
        
        // Validate all fields
        const fields = form.querySelectorAll('input, select, textarea');
        let isFormValid = true;
        
        fields.forEach(field => {
            if (!this.validateField(field)) {
                isFormValid = false;
            }
        });
        
        if (!isFormValid) {
            e.preventDefault();
            this.showFormError(form, 'يرجى تصحيح الأخطاء المعلمة أدناه');
            return;
        }
        
        // Show loading state
        this.showButtonLoading(submitButton);
        
        // If it's an AJAX form
        if (form.classList.contains('ajax-form')) {
            e.preventDefault();
            this.submitFormAjax(form);
        }
    }

    /**
     * Submit form via AJAX
     */
    submitFormAjax(form) {
        const formData = new FormData(form);
        const submitButton = form.querySelector('button[type="submit"]');
        
        fetch(form.action || window.location.href, {
            method: form.method || 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showFormSuccess(form, data.message || 'تم الحفظ بنجاح');
                if (data.redirect) {
                    setTimeout(() => {
                        window.location.href = data.redirect;
                    }, 1500);
                }
            } else {
                this.showFormError(form, data.message || 'حدث خطأ أثناء المعالجة');
                if (data.errors) {
                    this.displayFormErrors(form, data.errors);
                }
            }
        })
        .catch(error => {
            console.error('Form submission error:', error);
            this.showFormError(form, 'حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى');
        })
        .finally(() => {
            this.hideButtonLoading(submitButton);
        });
    }

    /**
     * Setup table enhancements
     */
    setupTableEnhancements() {
        const tables = document.querySelectorAll('.table-enhanced');
        
        tables.forEach(table => {
            // Add sorting functionality
            this.setupTableSorting(table);
            
            // Add filtering functionality
            this.setupTableFiltering(table);
            
            // Add row selection functionality
            this.setupTableRowSelection(table);
            
            // Add export functionality
            this.setupTableExport(table);
        });
    }

    /**
     * Setup table sorting
     */
    setupTableSorting(table) {
        const headers = table.querySelectorAll('th[data-sortable="true"]');
        
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                this.sortTable(table, header);
            });
            
            // Add sort indicators
            const indicator = document.createElement('i');
            indicator.className = 'fas fa-sort ms-2';
            header.appendChild(indicator);
        });
    }

    /**
     * Sort table by column
     */
    sortTable(table, header) {
        const columnIndex = Array.from(header.parentNode.children).indexOf(header);
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        const isAscending = !header.classList.contains('sort-asc');
        
        // Remove previous sort classes
        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
            const icon = th.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-sort ms-2';
            }
        });
        
        // Add current sort class
        header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
        const icon = header.querySelector('i');
        if (icon) {
            icon.className = `fas fa-sort-${isAscending ? 'up' : 'down'} ms-2`;
        }
        
        // Sort rows
        rows.sort((a, b) => {
            const aValue = a.children[columnIndex].textContent.trim();
            const bValue = b.children[columnIndex].textContent.trim();
            
            let comparison = 0;
            if (!isNaN(aValue) && !isNaN(bValue)) {
                comparison = parseFloat(aValue) - parseFloat(bValue);
            } else {
                comparison = aValue.localeCompare(bValue, 'ar');
            }
            
            return isAscending ? comparison : -comparison;
        });
        
        // Reorder rows in DOM
        rows.forEach(row => tbody.appendChild(row));
    }

    /**
     * Setup notifications system
     */
    setupNotifications() {
        this.notificationContainer = this.createNotificationContainer();
        
        // Setup WebSocket for real-time notifications
        this.setupWebSocketNotifications();
        
        // Setup notification sound
        this.notificationSound = new Audio('/static/sounds/notification.mp3');
        this.notificationSound.volume = 0.3;
        
        // Load notification preferences
        this.loadNotificationPreferences();
    }

    /**
     * Create notification container
     */
    createNotificationContainer() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        return container;
    }

    /**
     * Show notification
     */
    showNotification(title, message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `toast align-items-center text-white bg-${type} border-0 fade show`;
        notification.setAttribute('role', 'alert');
        notification.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}</strong><br>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        this.notificationContainer.appendChild(notification);
        
        // Auto-remove after duration
        setTimeout(() => {
            notification.remove();
        }, duration);
        
        // Play notification sound
        if (this.notificationPreferences.soundEnabled) {
            this.notificationSound.play().catch(() => {
                // Ignore audio play errors
            });
        }
        
        // Trigger animation
        setTimeout(() => {
            notification.classList.add('slide-in-right');
        }, 100);
    }

    /**
     * Setup WebSocket notifications
     */
    setupWebSocketNotifications() {
        if (!window.WebSocket) {
            console.warn('WebSocket not supported');
            return;
        }
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/notifications/`;
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected for notifications');
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketNotification(data);
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected, attempting to reconnect...');
                setTimeout(() => {
                    this.setupWebSocketNotifications();
                }, 5000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        } catch (error) {
            console.error('Failed to setup WebSocket:', error);
        }
    }

    /**
     * Handle WebSocket notification
     */
    handleWebSocketNotification(data) {
        const { title, message, type, priority } = data;
        
        // Show notification
        this.showNotification(title, message, type);
        
        // Update notification badge
        this.updateNotificationBadge();
        
        // Show desktop notification if permitted
        if (this.notificationPreferences.desktopEnabled && 'Notification' in window) {
            new Notification(title, {
                body: message,
                icon: '/static/images/logo.png'
            });
        }
        
        // Handle high priority notifications
        if (priority === 'HIGH' || priority === 'URGENT') {
            this.handleHighPriorityNotification(data);
        }
    }

    /**
     * Setup theme management
     */
    setupTheme() {
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.applyTheme(this.currentTheme);
        
        // Theme toggle button
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
        
        // Auto theme based on system preference
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addListener(() => {
                if (!localStorage.getItem('theme')) {
                    this.applyTheme(mediaQuery.matches ? 'dark' : 'light');
                }
            });
        }
    }

    /**
     * Toggle theme
     */
    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(this.currentTheme);
        localStorage.setItem('theme', this.currentTheme);
    }

    /**
     * Apply theme
     */
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        
        // Update theme toggle button
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            if (icon) {
                icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        }
    }

    /**
     * Setup analytics tracking
     */
    setupAnalytics() {
        // Track page views
        this.trackPageView();
        
        // Track user interactions
        this.setupInteractionTracking();
        
        // Track performance metrics
        this.trackPerformanceMetrics();
    }

    /**
     * Track page view
     */
    trackPageView() {
        const pageData = {
            url: window.location.href,
            title: document.title,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            referrer: document.referrer
        };
        
        this.sendAnalytics('page_view', pageData);
    }

    /**
     * Send analytics data
     */
    sendAnalytics(event, data) {
        // Only send analytics if user has consented
        if (!this.hasAnalyticsConsent()) {
            return;
        }
        
        fetch('/api/v1/analytics/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({
                event: event,
                data: data
            })
        }).catch(error => {
            console.error('Analytics error:', error);
        });
    }

    /**
     * Utility methods
     */
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    showButtonLoading(button) {
        button.disabled = true;
        const originalText = button.innerHTML;
        button.dataset.originalText = originalText;
        button.innerHTML = '<span class="loading-spinner"></span> جاري المعالجة...';
    }

    hideButtonLoading(button) {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || button.innerHTML;
    }

    showFieldError(field, message) {
        field.classList.add('is-invalid');
        
        let errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            field.parentNode.appendChild(errorDiv);
        }
        errorDiv.textContent = message;
    }

    clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    showFieldSuccess(field) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    }

    showFormError(form, message) {
        this.showAlert(form, message, 'danger');
    }

    showFormSuccess(form, message) {
        this.showAlert(form, message, 'success');
    }

    showAlert(container, message, type) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-enhanced fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        container.insertBefore(alert, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    hasAnalyticsConsent() {
        return localStorage.getItem('analytics_consent') === 'true';
    }

    initializePerformanceMonitoring() {
        // Monitor page load time
        window.addEventListener('load', () => {
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            this.sendAnalytics('page_load_time', { loadTime });
        });
        
        // Monitor JavaScript errors
        window.addEventListener('error', (event) => {
            this.sendAnalytics('javascript_error', {
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno
            });
        });
    }

    setupRealTimeFeatures() {
        // Auto-refresh certain elements
        this.setupAutoRefresh();
        
        // Setup live search
        this.setupLiveSearch();
        
        // Setup real-time status updates
        this.setupStatusUpdates();
    }

    setupAutoRefresh() {
        const autoRefreshElements = document.querySelectorAll('[data-auto-refresh]');
        
        autoRefreshElements.forEach(element => {
            const interval = parseInt(element.dataset.autoRefresh) * 1000;
            const url = element.dataset.refreshUrl;
            
            if (url && interval > 0) {
                setInterval(() => {
                    this.refreshElement(element, url);
                }, interval);
            }
        });
    }

    refreshElement(element, url) {
        fetch(url)
            .then(response => response.text())
            .then(html => {
                element.innerHTML = html;
                // Re-initialize any components in the refreshed content
                this.initializeBootstrapComponents();
            })
            .catch(error => {
                console.error('Auto-refresh error:', error);
            });
    }

    loadNotificationPreferences() {
        this.notificationPreferences = {
            soundEnabled: localStorage.getItem('notification_sound') !== 'false',
            desktopEnabled: localStorage.getItem('notification_desktop') === 'true'
        };
        
        // Request desktop notification permission
        if (this.notificationPreferences.desktopEnabled && 'Notification' in window) {
            if (Notification.permission === 'default') {
                Notification.requestPermission();
            }
        }
    }

    updateNotificationBadge() {
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            const currentCount = parseInt(badge.textContent) || 0;
            badge.textContent = currentCount + 1;
            badge.style.display = 'inline-block';
        }
    }

    handleHighPriorityNotification(data) {
        // Show modal for urgent notifications
        if (data.priority === 'URGENT') {
            this.showUrgentNotificationModal(data);
        }
    }

    showUrgentNotificationModal(data) {
        const modal = document.getElementById('urgent-notification-modal');
        if (modal) {
            const titleElement = modal.querySelector('.modal-title');
            const bodyElement = modal.querySelector('.modal-body');
            
            if (titleElement) titleElement.textContent = data.title;
            if (bodyElement) bodyElement.textContent = data.message;
            
            const modalInstance = new bootstrap.Modal(modal);
            modalInstance.show();
        }
    }

    handleModalShow(event) {
        const modal = event.target;
        modal.classList.add('fade-in');
    }

    handleModalHidden(event) {
        const modal = event.target;
        modal.classList.remove('fade-in');
    }

    setupSearchSuggestions(input) {
        // Implementation for search suggestions
        // This would typically involve showing a dropdown with suggestions
    }

    setupNavigationEnhancements() {
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    setupFileUploadEnhancements() {
        const fileInputs = document.querySelectorAll('input[type="file"]');
        
        fileInputs.forEach(input => {
            this.enhanceFileInput(input);
        });
    }

    enhanceFileInput(input) {
        // Create enhanced file input with drag & drop
        const wrapper = document.createElement('div');
        wrapper.className = 'file-upload-enhanced';
        
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);
        
        // Add drag & drop functionality
        wrapper.addEventListener('dragover', (e) => {
            e.preventDefault();
            wrapper.classList.add('dragover');
        });
        
        wrapper.addEventListener('dragleave', () => {
            wrapper.classList.remove('dragover');
        });
        
        wrapper.addEventListener('drop', (e) => {
            e.preventDefault();
            wrapper.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                this.handleFileSelection(input, files);
            }
        });
        
        input.addEventListener('change', (e) => {
            this.handleFileSelection(input, e.target.files);
        });
    }

    handleFileSelection(input, files) {
        // Validate file types and sizes
        const allowedTypes = input.dataset.allowedTypes?.split(',') || [];
        const maxSize = parseInt(input.dataset.maxSize) || 10485760; // 10MB default
        
        Array.from(files).forEach(file => {
            if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
                this.showNotification('خطأ في الملف', `نوع الملف ${file.type} غير مسموح`, 'danger');
                return;
            }
            
            if (file.size > maxSize) {
                this.showNotification('خطأ في حجم الملف', `حجم الملف ${file.name} كبير جداً`, 'danger');
                return;
            }
        });
    }

    setupInteractionTracking() {
        // Track button clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('button, .btn')) {
                this.sendAnalytics('button_click', {
                    buttonText: e.target.textContent.trim(),
                    buttonClass: e.target.className
                });
            }
        });
        
        // Track form submissions
        document.addEventListener('submit', (e) => {
            this.sendAnalytics('form_submit', {
                formId: e.target.id,
                formClass: e.target.className
            });
        });
    }

    trackPerformanceMetrics() {
        // Track Core Web Vitals
        if ('web-vital' in window) {
            // This would require the web-vitals library
            // getCLS, getFID, getFCP, getLCP, getTTFB
        }
    }

    setupTableFiltering(table) {
        const filterInputs = table.querySelectorAll('[data-filter-column]');
        
        filterInputs.forEach(input => {
            input.addEventListener('input', () => {
                this.filterTable(table);
            });
        });
    }

    filterTable(table) {
        const filterInputs = table.querySelectorAll('[data-filter-column]');
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            let shouldShow = true;
            
            filterInputs.forEach(input => {
                const columnIndex = parseInt(input.dataset.filterColumn);
                const filterValue = input.value.toLowerCase();
                const cellValue = row.children[columnIndex]?.textContent.toLowerCase() || '';
                
                if (filterValue && !cellValue.includes(filterValue)) {
                    shouldShow = false;
                }
            });
            
            row.style.display = shouldShow ? '' : 'none';
        });
    }

    setupTableRowSelection(table) {
        const selectAll = table.querySelector('thead input[type="checkbox"]');
        const rowCheckboxes = table.querySelectorAll('tbody input[type="checkbox"]');
        
        if (selectAll) {
            selectAll.addEventListener('change', () => {
                rowCheckboxes.forEach(checkbox => {
                    checkbox.checked = selectAll.checked;
                });
                this.updateBulkActions(table);
            });
        }
        
        rowCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateBulkActions(table);
            });
        });
    }

    updateBulkActions(table) {
        const selectedRows = table.querySelectorAll('tbody input[type="checkbox"]:checked');
        const bulkActions = document.querySelector('.bulk-actions');
        
        if (bulkActions) {
            if (selectedRows.length > 0) {
                bulkActions.style.display = 'block';
                bulkActions.querySelector('.selected-count').textContent = selectedRows.length;
            } else {
                bulkActions.style.display = 'none';
            }
        }
    }

    setupTableExport(table) {
        const exportButton = table.querySelector('[data-export]');
        
        if (exportButton) {
            exportButton.addEventListener('click', () => {
                const format = exportButton.dataset.export;
                this.exportTable(table, format);
            });
        }
    }

    exportTable(table, format) {
        const tableData = this.extractTableData(table);
        
        switch (format) {
            case 'csv':
                this.exportToCSV(tableData, 'table-export.csv');
                break;
            case 'excel':
                this.exportToExcel(tableData, 'table-export.xlsx');
                break;
            case 'pdf':
                this.exportToPDF(tableData, 'table-export.pdf');
                break;
        }
    }

    extractTableData(table) {
        const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
        const rows = Array.from(table.querySelectorAll('tbody tr')).map(tr => 
            Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim())
        );
        
        return { headers, rows };
    }

    exportToCSV(data, filename) {
        const csv = [
            data.headers.join(','),
            ...data.rows.map(row => row.map(cell => `"${cell}"`).join(','))
        ].join('\n');
        
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        
        window.URL.revokeObjectURL(url);
    }

    setupLiveSearch() {
        const liveSearchInputs = document.querySelectorAll('[data-live-search]');
        
        liveSearchInputs.forEach(input => {
            let searchTimeout;
            
            input.addEventListener('input', () => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.performLiveSearch(input);
                }, 300);
            });
        });
    }

    performLiveSearch(input) {
        const searchTerm = input.value.toLowerCase();
        const targetSelector = input.dataset.liveSearch;
        const targets = document.querySelectorAll(targetSelector);
        
        targets.forEach(target => {
            const text = target.textContent.toLowerCase();
            const shouldShow = !searchTerm || text.includes(searchTerm);
            target.style.display = shouldShow ? '' : 'none';
        });
    }

    setupStatusUpdates() {
        const statusElements = document.querySelectorAll('[data-status-update]');
        
        statusElements.forEach(element => {
            const updateInterval = parseInt(element.dataset.statusUpdate) * 1000;
            const statusUrl = element.dataset.statusUrl;
            
            if (statusUrl && updateInterval > 0) {
                setInterval(() => {
                    this.updateStatus(element, statusUrl);
                }, updateInterval);
            }
        });
    }

    updateStatus(element, url) {
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.status) {
                    element.textContent = data.status;
                    element.className = `status-badge status-${data.status.toLowerCase()}`;
                }
            })
            .catch(error => {
                console.error('Status update error:', error);
            });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.universityApp = new UniversityApp();
});

// Service Worker Registration for PWA features
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}