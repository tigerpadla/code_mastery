/**
 * Quiz Results Page JavaScript
 * Handles share and save functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Share button functionality
    const shareBtn = document.querySelector('.share-btn');
    if (shareBtn) {
        shareBtn.addEventListener('click', async function() {
            // Build absolute URL from relative URL
            const relativeUrl = this.dataset.quizUrl;
            const quizUrl = window.location.origin + relativeUrl;
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
                showToast('Link copied to clipboard!', 'success');
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
                showToast('Link copied to clipboard!', 'success');
            }
        });
    }

    // Save quiz button functionality (AJAX)
    const saveButtons = document.querySelectorAll('.save-quiz-btn');
    saveButtons.forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            
            const quizId = this.dataset.quizId;
            const csrfToken = this.dataset.csrfToken;
            
            try {
                const response = await fetch(`/accounts/quiz/${quizId}/save/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    
                    // Update button state
                    this.dataset.saved = data.saved ? 'true' : 'false';
                    
                    // Update button icon and text
                    const icon = this.querySelector('i');
                    const textSpan = this.querySelector('.btn-text');
                    
                    if (data.saved) {
                        if (icon) {
                            icon.className = 'fas fa-bookmark me-2';
                        }
                        if (textSpan) {
                            textSpan.textContent = 'Saved';
                        }
                        this.classList.add('saved');
                    } else {
                        if (icon) {
                            icon.className = 'far fa-bookmark me-2';
                        }
                        if (textSpan) {
                            textSpan.textContent = 'Save Quiz';
                        }
                        this.classList.remove('saved');
                    }
                    
                    showToast(data.message, 'success');
                } else if (response.status === 401) {
                    window.location.href = '/accounts/login/?next=' + window.location.pathname;
                } else {
                    showToast('Failed to save quiz. Please try again.', 'error');
                }
            } catch (error) {
                console.error('Save quiz error:', error);
                showToast('An error occurred. Please try again.', 'error');
            }
        });
    });
});

/**
 * Show a toast notification for share/save feedback
 */
function showToast(message, type = 'success') {
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
