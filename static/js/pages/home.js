/**
 * Home Page JavaScript
 * Handles the quiz generator form and loading modal
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('quiz-generator-form');
    const loadingModal = document.getElementById('loading-modal');
    
    // Only run if form exists on page
    if (!form || !loadingModal) return;
    
    let isSubmitting = false;
    
    form.addEventListener('submit', function(e) {
        // Prevent double submission
        if (isSubmitting) {
            e.preventDefault();
            return false;
        }
        
        // Check if form is valid
        const topicInput = form.querySelector('input[name="topic"]');
        if (!topicInput.value.trim()) {
            return false;
        }
        
        // Set flag and show loading modal
        isSubmitting = true;
        loadingModal.classList.add('active');
        
        // Disable visible form elements after a tiny delay to allow form submission
        setTimeout(function() {
            // Disable only visible inputs and buttons (not hidden CSRF token)
            form.querySelectorAll('input[type="text"], button').forEach(el => {
                el.disabled = true;
            });
            
            // Also disable the external generate button
            const externalBtn = document.querySelector('button[form="quiz-generator-form"]');
            if (externalBtn) {
                externalBtn.disabled = true;
            }
        }, 10);
    });
});
