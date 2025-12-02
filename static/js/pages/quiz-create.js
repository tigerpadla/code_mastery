/**
 * Quiz Create/Edit Page JavaScript
 * Handles dynamic question form management
 */

document.addEventListener('DOMContentLoaded', function() {
    const questionsContainer = document.getElementById('questions-container');
    const addQuestionBtn = document.getElementById('add-question');
    const questionTemplate = document.getElementById('question-template');
    const totalFormsInput = document.querySelector('[name="questions-TOTAL_FORMS"]');
    
    /**
     * Update question numbers after add/delete
     */
    function updateQuestionNumbers() {
        const questionCards = questionsContainer.querySelectorAll('.question-form-card:not(.deleted)');
        questionCards.forEach((card, index) => {
            const numberSpan = card.querySelector('.question-number');
            if (numberSpan) {
                numberSpan.textContent = `Question ${index + 1}`;
            }
        });
    }
    
    /**
     * Add a new question form
     */
    function addQuestion() {
        const formCount = parseInt(totalFormsInput.value);
        const newFormHtml = questionTemplate.innerHTML
            .replace(/__prefix__/g, formCount)
            .replace(/__num__/g, formCount + 1);
        
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = newFormHtml;
        const newForm = tempDiv.firstElementChild;
        
        questionsContainer.appendChild(newForm);
        totalFormsInput.value = formCount + 1;
        
        // Add delete handler to new form
        attachDeleteHandler(newForm);
        
        // Scroll to new question
        newForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Focus on question text
        const textArea = newForm.querySelector('textarea[name$="-text"]');
        if (textArea) {
            setTimeout(() => textArea.focus(), 300);
        }
        
        updateQuestionNumbers();
    }
    
    /**
     * Delete a question (mark for deletion)
     */
    function deleteQuestion(card) {
        const deleteCheckbox = card.querySelector('input[name$="-DELETE"]');
        const visibleCards = questionsContainer.querySelectorAll('.question-form-card:not(.deleted)');
        
        // Don't allow deleting if it's the only question
        if (visibleCards.length <= 1) {
            showToast('You must have at least one question.', 'error');
            return;
        }
        
        if (deleteCheckbox) {
            // Existing form - mark for deletion
            deleteCheckbox.checked = true;
            card.classList.add('deleted');
            card.style.display = 'none';
        } else {
            // New form (not yet saved) - just remove
            card.remove();
            // Update total forms count
            totalFormsInput.value = parseInt(totalFormsInput.value) - 1;
        }
        
        updateQuestionNumbers();
    }
    
    /**
     * Attach delete handler to a question card
     */
    function attachDeleteHandler(card) {
        const deleteBtn = card.querySelector('.delete-question');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', function() {
                if (confirm('Are you sure you want to delete this question?')) {
                    deleteQuestion(card);
                }
            });
        }
    }
    
    /**
     * Show toast notification
     */
    function showToast(message, type = 'success') {
        const existingToast = document.querySelector('.share-toast');
        if (existingToast) {
            existingToast.remove();
        }
        
        const toast = document.createElement('div');
        toast.className = `share-toast share-toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
            ${message}
        `;
        
        document.body.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    // Add question button handler
    if (addQuestionBtn) {
        addQuestionBtn.addEventListener('click', addQuestion);
    }
    
    // Attach delete handlers to existing questions
    document.querySelectorAll('.question-form-card').forEach(card => {
        attachDeleteHandler(card);
    });
    
    // Form validation before submit
    const quizForm = document.getElementById('quiz-form');
    if (quizForm) {
        quizForm.addEventListener('submit', function(e) {
            const visibleCards = questionsContainer.querySelectorAll('.question-form-card:not(.deleted)');
            
            if (visibleCards.length === 0) {
                e.preventDefault();
                showToast('You must have at least one question.', 'error');
                return false;
            }
            
            // Validate each visible question
            let isValid = true;
            visibleCards.forEach((card, index) => {
                const text = card.querySelector('textarea[name$="-text"]');
                const optionA = card.querySelector('input[name$="-option_a"]');
                const optionB = card.querySelector('input[name$="-option_b"]');
                const optionC = card.querySelector('input[name$="-option_c"]');
                const optionD = card.querySelector('input[name$="-option_d"]');
                const correctAnswer = card.querySelector('select[name$="-correct_answer"]');
                
                if (!text?.value.trim()) {
                    isValid = false;
                    text?.classList.add('is-invalid');
                } else {
                    text?.classList.remove('is-invalid');
                }
                
                [optionA, optionB, optionC, optionD].forEach(opt => {
                    if (!opt?.value.trim()) {
                        isValid = false;
                        opt?.classList.add('is-invalid');
                    } else {
                        opt?.classList.remove('is-invalid');
                    }
                });
                
                if (!correctAnswer?.value) {
                    isValid = false;
                    correctAnswer?.classList.add('is-invalid');
                } else {
                    correctAnswer?.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showToast('Please fill in all required fields.', 'error');
                
                // Scroll to first invalid field
                const firstInvalid = quizForm.querySelector('.is-invalid');
                if (firstInvalid) {
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstInvalid.focus();
                }
                return false;
            }
        });
    }
    
    // Remove invalid class on input
    document.querySelectorAll('.form-control, .form-select').forEach(input => {
        input.addEventListener('input', function() {
            this.classList.remove('is-invalid');
        });
        input.addEventListener('change', function() {
            this.classList.remove('is-invalid');
        });
    });
});
