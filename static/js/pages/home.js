/**
 * Home Page JavaScript
 * Handles the quiz generator form, loading modal, and random topic generation
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('quiz-generator-form');
    const loadingModal = document.getElementById('loading-modal');
    const topicInput = document.getElementById('topic-input');
    const randomTopicBtn = document.getElementById('random-topic-btn');
    
    // Only run if form exists on page
    if (!form || !loadingModal) return;
    
    /**
     * Random Programming Topics
     * Curated list of programming topics for quiz generation
     */
    const programmingTopics = [
        // Python
        'Python list comprehensions',
        'Python decorators',
        'Python generators and iterators',
        'Python error handling',
        'Python object-oriented programming',
        'Python file handling',
        'Python lambda functions',
        'Python dictionaries',
        'Python string methods',
        'Python regular expressions',
        
        // JavaScript
        'JavaScript promises and async/await',
        'JavaScript array methods',
        'JavaScript DOM manipulation',
        'JavaScript closures',
        'JavaScript ES6 features',
        'JavaScript event handling',
        'JavaScript objects and prototypes',
        'JavaScript fetch API',
        'JavaScript local storage',
        'JavaScript template literals',
        
        // Web Development
        'HTML5 semantic elements',
        'CSS Flexbox layout',
        'CSS Grid layout',
        'CSS animations and transitions',
        'Responsive web design',
        'Bootstrap 5 components',
        'REST API concepts',
        'HTTP methods and status codes',
        
        // Databases
        'SQL SELECT queries',
        'SQL JOIN operations',
        'Database normalization',
        'PostgreSQL basics',
        'Django ORM queries',
        
        // Django
        'Django models and migrations',
        'Django views and URLs',
        'Django templates',
        'Django forms',
        'Django authentication',
        'Django class-based views',
        
        // Git & Version Control
        'Git branching strategies',
        'Git commands basics',
        'GitHub pull requests',
        
        // General Programming
        'Data structures basics',
        'Algorithm complexity (Big O)',
        'Object-oriented programming principles',
        'Design patterns basics',
        'API design best practices',
        'Testing fundamentals',
        'Clean code principles'
    ];
    
    /**
     * Get a random topic from the list
     */
    function getRandomTopic() {
        const randomIndex = Math.floor(Math.random() * programmingTopics.length);
        return programmingTopics[randomIndex];
    }
    
    /**
     * Random Topic Button Click Handler
     */
    if (randomTopicBtn && topicInput) {
        randomTopicBtn.addEventListener('click', function() {
            // Add rolling animation to dice
            const diceIcon = this.querySelector('i');
            diceIcon.classList.add('dice-rolling');
            
            // Wait for animation to complete, then set random topic
            setTimeout(function() {
                topicInput.value = getRandomTopic();
                diceIcon.classList.remove('dice-rolling');
                topicInput.focus();
            }, 500);
        });
    }
    
    /**
     * Form Submission Handler
     */
    let isSubmitting = false;
    
    form.addEventListener('submit', function(e) {
        // Prevent double submission
        if (isSubmitting) {
            e.preventDefault();
            return false;
        }
        
        // Check if form is valid
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
