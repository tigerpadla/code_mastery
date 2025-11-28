/**
 * Code Mastery - Main JavaScript
*/

(function() {
    "use strict";

    /**
     * Easy selector helper function
     */
    const select = (el, all = false) => {
        el = el.trim();
        if (all) {
            return [...document.querySelectorAll(el)];
        } else {
            return document.querySelector(el);
        }
    };

    /**
     * Easy event listener function
     */
    const on = (type, el, listener, all = false) => {
        let selectEl = select(el, all);
        if (selectEl) {
            if (all) {
                selectEl.forEach(e => e.addEventListener(type, listener));
            } else {
                selectEl.addEventListener(type, listener);
            }
        }
    };

    /**
     * Easy on scroll event listener
     */
    const onscroll = (el, listener) => {
        el.addEventListener('scroll', listener);
    };

    /**
     * Header scroll class toggle
     */
    let selectHeader = select('.header');
    if (selectHeader) {
        const headerScrolled = () => {
            if (window.scrollY > 100) {
                selectHeader.classList.add('scrolled');
            } else {
                selectHeader.classList.remove('scrolled');
            }
        };
        window.addEventListener('load', headerScrolled);
        onscroll(document, headerScrolled);
    }

    /**
     * Mobile nav toggle
     */
    on('click', '.mobile-nav-toggle', function(e) {
        const navmenu = select('.navmenu');
        const header = select('.header');
        
        navmenu.classList.toggle('mobile-nav-active');
        this.classList.toggle('bi-list');
        this.classList.toggle('bi-x');
        
        // Toggle body scroll
        document.body.classList.toggle('mobile-nav-active');
    });

    /**
     * Close mobile nav on same-page link click
     */
    on('click', '.navmenu a', function(e) {
        const navmenu = select('.navmenu');
        if (navmenu.classList.contains('mobile-nav-active')) {
            navmenu.classList.remove('mobile-nav-active');
            select('.mobile-nav-toggle').classList.toggle('bi-list');
            select('.mobile-nav-toggle').classList.toggle('bi-x');
            document.body.classList.remove('mobile-nav-active');
        }
    }, true);

    /**
     * Scroll top button
     */
    let scrollTop = select('.back-to-top');
    if (scrollTop) {
        const toggleScrollTop = () => {
            if (window.scrollY > 100) {
                scrollTop.classList.add('active');
                scrollTop.style.display = 'flex';
            } else {
                scrollTop.classList.remove('active');
                scrollTop.style.display = 'none';
            }
        };
        window.addEventListener('load', toggleScrollTop);
        onscroll(document, toggleScrollTop);
        
        scrollTop.addEventListener('click', (e) => {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    /**
     * Auto-hide alerts after delay
     */
    const alerts = select('.alert-dismissible', true);
    if (alerts.length) {
        alerts.forEach(alert => {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        });
    }

    /**
     * Smooth scroll for anchor links
     */
    on('click', 'a[href^="#"]:not([href="#"])', function(e) {
        const target = select(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }, true);

    /**
     * Quiz Option Selection (for quiz pages)
     */
    on('click', '.quiz-option', function(e) {
        // Remove selected class from siblings
        const parent = this.closest('.quiz-options');
        if (parent) {
            parent.querySelectorAll('.quiz-option').forEach(opt => {
                opt.classList.remove('selected');
            });
        }
        // Add selected class to clicked option
        this.classList.add('selected');
        
        // Update hidden input if exists
        const input = this.querySelector('input[type="radio"]');
        if (input) {
            input.checked = true;
        }
    }, true);

    /**
     * Tooltip initialization
     */
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length) {
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }

    /**
     * Popover initialization
     */
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    if (popoverTriggerList.length) {
        const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    }

    /**
     * Form validation styles
     */
    const forms = document.querySelectorAll('.needs-validation');
    if (forms.length) {
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }

    /**
     * Copy to clipboard functionality
     */
    on('click', '.btn-copy', function(e) {
        e.preventDefault();
        const textToCopy = this.getAttribute('data-copy') || this.previousElementSibling?.textContent;
        if (textToCopy) {
            navigator.clipboard.writeText(textToCopy).then(() => {
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 2000);
            });
        }
    }, true);

})();
