/**
 * Quiz Detail Page JavaScript
 * Handles form validation and unanswered question highlighting
 */

document.addEventListener('DOMContentLoaded', function() {
    const quizForm = document.getElementById('quiz-form');
    
    if (!quizForm) return;
    
    quizForm.addEventListener('submit', function(e) {
        // Get all question cards
        const questionCards = document.querySelectorAll('.question-card');
        let firstUnanswered = null;
        let unansweredCount = 0;
        
        // Clear previous unanswered highlights
        questionCards.forEach(card => {
            card.classList.remove('unanswered');
        });
        
        // Check each question for an answer
        questionCards.forEach((card) => {
            const radioButtons = card.querySelectorAll('input[type="radio"]');
            const isAnswered = Array.from(radioButtons).some(radio => radio.checked);
            
            if (!isAnswered) {
                unansweredCount++;
                card.classList.add('unanswered');
                
                // Track first unanswered question
                if (!firstUnanswered) {
                    firstUnanswered = card;
                }
            }
        });
        
        // If there are unanswered questions, prevent submission
        if (unansweredCount > 0) {
            e.preventDefault();
            
            // Show alert message
            const message = unansweredCount === 1 
                ? 'Please answer the highlighted question before submitting.'
                : `Please answer all ${unansweredCount} highlighted questions before submitting.`;
            
            // Remove existing alert if any
            const existingAlert = document.querySelector('.quiz-validation-alert');
            if (existingAlert) {
                existingAlert.remove();
            }
            
            // Create and show alert
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-warning alert-dismissible fade show quiz-validation-alert';
            alertDiv.setAttribute('role', 'alert');
            alertDiv.innerHTML = `
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            // Insert alert before the form
            quizForm.parentNode.insertBefore(alertDiv, quizForm);
            
            // Scroll to first unanswered question with offset for header
            if (firstUnanswered) {
                const headerOffset = 100;
                const elementPosition = firstUnanswered.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
                
                // Add a pulse animation to draw attention
                firstUnanswered.classList.add('unanswered-pulse');
                setTimeout(() => {
                    firstUnanswered.classList.remove('unanswered-pulse');
                }, 1500);
            }
            
            return false;
        }
    });
    
    // Remove unanswered highlight when user answers a question
    document.querySelectorAll('.question-card input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const card = this.closest('.question-card');
            if (card) {
                card.classList.remove('unanswered');
                card.classList.remove('unanswered-pulse');
                
                // Check if all questions are now answered to remove the alert
                const unansweredCards = document.querySelectorAll('.question-card.unanswered');
                if (unansweredCards.length === 0) {
                    const alert = document.querySelector('.quiz-validation-alert');
                    if (alert) {
                        alert.remove();
                    }
                }
            }
        });
    });

    // Share button functionality
    const shareBtn = document.querySelector('.share-btn');
    if (shareBtn) {
        shareBtn.addEventListener('click', async function() {
            const quizUrl = this.dataset.quizUrl;
            const quizTitle = this.dataset.quizTitle;
            
            // Try native share API first (mobile devices)
            if (navigator.share) {
                try {
                    await navigator.share({
                        title: quizTitle,
                        text: `Take this quiz: ${quizTitle}`,
                        url: quizUrl
                    });
                    return;
                } catch (err) {
                    // User cancelled or share failed, fall back to clipboard
                    if (err.name === 'AbortError') return;
                }
            }
            
            // Fall back to clipboard copy
            try {
                await navigator.clipboard.writeText(quizUrl);
                showShareToast('Link copied to clipboard!', 'success');
            } catch (err) {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = quizUrl;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                showShareToast('Link copied to clipboard!', 'success');
            }
        });
    }
});

/**
 * Show a toast notification for share feedback
 */
function showShareToast(message, type = 'success') {
    // Remove existing toast if any
    const existingToast = document.querySelector('.share-toast');
    if (existingToast) {
        existingToast.remove();
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `share-toast share-toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
        ${message}
    `;
    
    document.body.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
