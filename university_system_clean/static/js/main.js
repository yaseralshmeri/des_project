/**
 * University Management System - Main JavaScript
 * Enhanced with Arabic language support and modern UX features
 */

class UniversitySystemApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.setupFormValidation();
        this.setupNotifications();
        this.setupLoadingStates();
        this.setupAccessibility();
    }

    /**
     * Setup main event listeners
     */
    setupEventListeners() {
        // DOM Content Loaded
        document.addEventListener('DOMContentLoaded', () => {
            this.onDOMReady();
        });

        // Page Load
        window.addEventListener('load', () => {
            this.onPageLoad();
        });

        // Resize
        window.addEventListener('resize', this.debounce(() => {
            this.onWindowResize();
        }, 300));

        // Before Unload
        window.addEventListener('beforeunload', (e) => {
            this.onBeforeUnload(e);
        });
    }

    /**
     * Initialize components when DOM is ready
     */
    onDOMReady() {
        this.initializeSidebar();
        this.initializeTooltips();
        this.initializePopovers();
        this.initializeModals();
        this.initializeTables();
        this.initializeCharts();
        this.animateElements();
    }

    /**
     * Handle page load completion
     */
    onPageLoad() {
        this.hideLoadingSpinner();
        this.initializeRealTimeUpdates();
        this.setupPerformanceOptimizations();
    }

    /**
     * Handle window resize
     */
    onWindowResize() {
        this.adjustSidebarForMobile();
        this.resizeCharts();
    }

    /**
     * Handle before page unload
     */
    onBeforeUnload(e) {
        const hasUnsavedChanges = this.checkUnsavedChanges();
        if (hasUnsavedChanges) {
            e.preventDefault();
            e.returnValue = 'لديك تغييرات غير محفوظة. هل أنت متأكد من المغادرة؟';
            return e.returnValue;
        }
    }

    /**
     * Initialize sidebar functionality
     */
    initializeSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('overlay');
        const navbarToggler = document.querySelector('.navbar-toggler');

        if (!sidebar || !overlay || !navbarToggler) return;

        // Toggle sidebar on mobile
        navbarToggler.addEventListener('click', () => {
            sidebar.classList.toggle('show');
            overlay.classList.toggle('show');
            document.body.classList.toggle('sidebar-open');
        });

        // Close sidebar when clicking overlay
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
            document.body.classList.remove('sidebar-open');
        });

        // Active link highlighting
        this.highlightActiveNavLink();
    }

    /**
     * Highlight active navigation link
     */
    highlightActiveNavLink() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.sidebar .nav-link');

        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath.startsWith(href)) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    /**
     * Initialize Bootstrap tooltips
     */
    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(tooltipTriggerEl => {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                placement: 'top',
                trigger: 'hover focus'
            });
        });
    }

    /**
     * Initialize Bootstrap popovers
     */
    initializePopovers() {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(popoverTriggerEl => {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    /**
     * Initialize modals with custom behaviors
     */
    initializeModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('show.bs.modal', (e) => {
                this.onModalShow(e);
            });

            modal.addEventListener('hidden.bs.modal', (e) => {
                this.onModalHide(e);
            });
        });
    }

    /**
     * Handle modal show event
     */
    onModalShow(e) {
        const modal = e.target;
        const firstInput = modal.querySelector('input, select, textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }

    /**
     * Handle modal hide event
     */
    onModalHide(e) {
        const modal = e.target;
        const forms = modal.querySelectorAll('form');
        forms.forEach(form => {
            if (!form.classList.contains('keep-data')) {
                form.reset();
            }
        });
    }

    /**
     * Initialize enhanced table functionality
     */
    initializeTables() {
        const tables = document.querySelectorAll('.table');
        tables.forEach(table => {
            this.enhanceTable(table);
        });
    }

    /**
     * Enhance table with additional functionality
     */
    enhanceTable(table) {
        // Add row hover effects
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('mouseenter', () => {
                row.style.transform = 'scale(1.02)';
            });

            row.addEventListener('mouseleave', () => {
                row.style.transform = 'scale(1)';
            });
        });

        // Add sorting functionality
        this.addTableSorting(table);
    }

    /**
     * Add table sorting functionality
     */
    addTableSorting(table) {
        const headers = table.querySelectorAll('thead th[data-sortable]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.innerHTML += ' <i class="bi bi-arrow-down-up text-muted"></i>';

            header.addEventListener('click', () => {
                this.sortTable(table, header);
            });
        });
    }

    /**
     * Sort table by column
     */
    sortTable(table, header) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const columnIndex = Array.from(header.parentNode.children).indexOf(header);
        const isAscending = !header.classList.contains('sort-asc');

        rows.sort((a, b) => {
            const aVal = a.children[columnIndex].textContent.trim();
            const bVal = b.children[columnIndex].textContent.trim();

            if (isAscending) {
                return aVal.localeCompare(bVal, 'ar');
            } else {
                return bVal.localeCompare(aVal, 'ar');
            }
        });

        // Update header classes
        table.querySelectorAll('thead th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });

        header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');

        // Re-append sorted rows
        rows.forEach(row => tbody.appendChild(row));
    }

    /**
     * Initialize charts if Chart.js is available
     */
    initializeCharts() {
        if (typeof Chart === 'undefined') return;

        // Set Chart.js defaults for Arabic
        Chart.defaults.font.family = 'Cairo, Noto Sans Arabic, sans-serif';
        Chart.defaults.font.size = 12;
        Chart.defaults.plugins.legend.rtl = true;
        Chart.defaults.plugins.legend.textDirection = 'rtl';
    }

    /**
     * Resize charts on window resize
     */
    resizeCharts() {
        if (typeof Chart === 'undefined') return;

        Chart.helpers.each(Chart.instances, (instance) => {
            instance.resize();
        });
    }

    /**
     * Setup form validation
     */
    setupFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(form => {
            this.enhanceForm(form);
        });
    }

    /**
     * Enhance form with validation and UX improvements
     */
    enhanceForm(form) {
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });

            input.addEventListener('input', () => {
                this.clearFieldError(input);
            });
        });

        // Form submission
        form.addEventListener('submit', (e) => {
            if (!this.validateForm(form)) {
                e.preventDefault();
                e.stopPropagation();
            } else {
                this.showLoadingSpinner();
            }
        });
    }

    /**
     * Validate individual field
     */
    validateField(field) {
        const value = field.value.trim();
        const required = field.hasAttribute('required');
        const type = field.getAttribute('type');
        let isValid = true;
        let errorMessage = '';

        // Required validation
        if (required && !value) {
            isValid = false;
            errorMessage = 'هذا الحقل مطلوب';
        }

        // Email validation
        if (type === 'email' && value && !this.isValidEmail(value)) {
            isValid = false;
            errorMessage = 'يرجى إدخال عنوان بريد إلكتروني صحيح';
        }

        // Phone validation
        if (type === 'tel' && value && !this.isValidPhone(value)) {
            isValid = false;
            errorMessage = 'يرجى إدخال رقم هاتف صحيح';
        }

        // Custom validation
        const customValidator = field.getAttribute('data-validator');
        if (customValidator && window[customValidator]) {
            const result = window[customValidator](value);
            if (!result.valid) {
                isValid = false;
                errorMessage = result.message;
            }
        }

        this.setFieldValidationState(field, isValid, errorMessage);
        return isValid;
    }

    /**
     * Set field validation state
     */
    setFieldValidationState(field, isValid, errorMessage = '') {
        const fieldGroup = field.closest('.form-group') || field.parentNode;
        
        field.classList.remove('is-valid', 'is-invalid');
        field.classList.add(isValid ? 'is-valid' : 'is-invalid');

        // Remove existing error message
        const existingError = fieldGroup.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        // Add error message if invalid
        if (!isValid && errorMessage) {
            const errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            errorElement.textContent = errorMessage;
            fieldGroup.appendChild(errorElement);
        }
    }

    /**
     * Clear field error state
     */
    clearFieldError(field) {
        field.classList.remove('is-invalid');
        const fieldGroup = field.closest('.form-group') || field.parentNode;
        const errorElement = fieldGroup.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.remove();
        }
    }

    /**
     * Validate entire form
     */
    validateForm(form) {
        const fields = form.querySelectorAll('input, select, textarea');
        let isValid = true;

        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    /**
     * Email validation
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Phone validation (Saudi format)
     */
    isValidPhone(phone) {
        const phoneRegex = /^(\+966|0)?[5-9]\d{8}$/;
        return phoneRegex.test(phone.replace(/\s+/g, ''));
    }

    /**
     * Setup notification system
     */
    setupNotifications() {
        this.notifications = [];
        this.createNotificationContainer();
        this.setupAutoHideAlerts();
    }

    /**
     * Create notification container
     */
    createNotificationContainer() {
        if (document.getElementById('notification-container')) return;

        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'position-fixed top-0 start-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info', duration = 5000) {
        const notification = this.createNotificationElement(message, type);
        const container = document.getElementById('notification-container');
        
        container.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        // Auto hide
        if (duration > 0) {
            setTimeout(() => {
                this.hideNotification(notification);
            }, duration);
        }

        return notification;
    }

    /**
     * Create notification element
     */
    createNotificationElement(message, type) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade`;
        notification.setAttribute('role', 'alert');
        
        const icons = {
            success: 'check-circle-fill',
            danger: 'exclamation-triangle-fill',
            warning: 'exclamation-circle-fill',
            info: 'info-circle-fill'
        };

        notification.innerHTML = `
            <i class="bi bi-${icons[type] || icons.info} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        return notification;
    }

    /**
     * Hide notification
     */
    hideNotification(notification) {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 150);
    }

    /**
     * Setup auto-hide for existing alerts
     */
    setupAutoHideAlerts() {
        const alerts = document.querySelectorAll('.alert:not(.alert-danger)');
        alerts.forEach(alert => {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.classList.remove('show');
                    setTimeout(() => alert.remove(), 150);
                }
            }, 5000);
        });
    }

    /**
     * Setup loading states
     */
    setupLoadingStates() {
        this.loadingSpinner = document.getElementById('loadingSpinner');
        this.setupFormLoadingStates();
    }

    /**
     * Show loading spinner
     */
    showLoadingSpinner() {
        if (this.loadingSpinner) {
            this.loadingSpinner.classList.add('show');
        }
    }

    /**
     * Hide loading spinner
     */
    hideLoadingSpinner() {
        if (this.loadingSpinner) {
            this.loadingSpinner.classList.remove('show');
        }
    }

    /**
     * Setup form loading states
     */
    setupFormLoadingStates() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', () => {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>جاري المعالجة...';
                }
            });
        });
    }

    /**
     * Animate elements on scroll
     */
    animateElements() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in-up');
                }
            });
        });

        const animatedElements = document.querySelectorAll('.card, .stats-card, .table');
        animatedElements.forEach(el => observer.observe(el));
    }

    /**
     * Setup accessibility features
     */
    setupAccessibility() {
        this.setupKeyboardNavigation();
        this.setupFocusManagement();
        this.setupScreenReaderSupport();
    }

    /**
     * Setup keyboard navigation
     */
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Escape key to close modals and sidebars
            if (e.key === 'Escape') {
                const openModal = document.querySelector('.modal.show');
                if (openModal) {
                    const modalInstance = bootstrap.Modal.getInstance(openModal);
                    modalInstance.hide();
                }

                const sidebar = document.getElementById('sidebar');
                if (sidebar && sidebar.classList.contains('show')) {
                    sidebar.classList.remove('show');
                    document.getElementById('overlay').classList.remove('show');
                }
            }
        });
    }

    /**
     * Setup focus management
     */
    setupFocusManagement() {
        // Focus trap for modals
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('shown.bs.modal', () => {
                this.trapFocus(modal);
            });
        });
    }

    /**
     * Trap focus within element
     */
    trapFocus(element) {
        const focusableElements = element.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        element.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        lastElement.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        firstElement.focus();
                        e.preventDefault();
                    }
                }
            }
        });
    }

    /**
     * Setup screen reader support
     */
    setupScreenReaderSupport() {
        // Announce page changes
        const pageTitle = document.title;
        this.announceToScreenReader(`تم تحميل صفحة ${pageTitle}`);
    }

    /**
     * Announce message to screen reader
     */
    announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;

        document.body.appendChild(announcement);

        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }

    /**
     * Initialize real-time updates
     */
    initializeRealTimeUpdates() {
        // Simulated real-time updates
        setInterval(() => {
            this.updateNotificationsBadge();
            this.updateSystemStatus();
        }, 30000); // Every 30 seconds
    }

    /**
     * Update notifications badge
     */
    updateNotificationsBadge() {
        const badge = document.querySelector('.sidebar .nav-link .badge');
        if (badge) {
            // Simulate new notifications
            const currentCount = parseInt(badge.textContent) || 0;
            if (Math.random() > 0.8) { // 20% chance of new notification
                badge.textContent = currentCount + 1;
                badge.classList.add('pulse');
                setTimeout(() => badge.classList.remove('pulse'), 2000);
            }
        }
    }

    /**
     * Update system status
     */
    updateSystemStatus() {
        const statusBadges = document.querySelectorAll('.badge:contains("النظام يعمل")');
        statusBadges.forEach(badge => {
            badge.classList.add('pulse');
            setTimeout(() => badge.classList.remove('pulse'), 1000);
        });
    }

    /**
     * Setup performance optimizations
     */
    setupPerformanceOptimizations() {
        // Lazy load images
        this.lazyLoadImages();
        
        // Debounce resize events
        this.debounceResizeEvents();
    }

    /**
     * Lazy load images
     */
    lazyLoadImages() {
        const images = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    }

    /**
     * Debounce resize events
     */
    debounceResizeEvents() {
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                this.onWindowResize();
            }, 250);
        });
    }

    /**
     * Adjust sidebar for mobile
     */
    adjustSidebarForMobile() {
        const sidebar = document.getElementById('sidebar');
        if (window.innerWidth >= 768) {
            sidebar.classList.remove('show');
            document.getElementById('overlay').classList.remove('show');
        }
    }

    /**
     * Check for unsaved changes
     */
    checkUnsavedChanges() {
        const forms = document.querySelectorAll('form[data-check-changes]');
        return Array.from(forms).some(form => {
            const formData = new FormData(form);
            return Array.from(formData.entries()).length > 0;
        });
    }

    /**
     * Utility: Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize the application
const app = new UniversitySystemApp();

// Export for global access
window.UniversitySystem = app;