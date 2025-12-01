/**
 * Quiz Results Page JavaScript
 * Handles share functionality
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
