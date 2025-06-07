// mindwell_navigator/static/js/script.js

document.addEventListener('DOMContentLoaded', function() {
    // Basic script for potential future enhancements.
    // For example, smooth scrolling or minor UI interactions.

    // Example: Confirm navigation away from assessment if in progress
    const assessmentForm = document.querySelector('.assessment-question-section form');
    if (assessmentForm) {
        const links = document.querySelectorAll('a:not([href^="#"]):not([target="_blank"])'); // All internal links
        
        // This is a very basic check. A more robust solution would check if
        // any radio button has been selected or if the assessment has truly started.
        let assessmentStarted = false; 
        const radioButtons = assessmentForm.querySelectorAll('input[type="radio"]');
        radioButtons.forEach(radio => {
            radio.addEventListener('change', () => {
                assessmentStarted = true;
            });
        });

        // Check if we are beyond the first question (a bit of a hacky way)
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar && progressBar.textContent.includes('Question 1 of')) {
            // Don't consider it "started" for warning purposes on the very first question page load
        } else if (progressBar) {
            assessmentStarted = true; // If not question 1, assume it's in progress
        }


        // Removed the disruptive window.onbeforeunload for now as it can be annoying
        // and hard to manage perfectly with session state.
        // User can use browser back button, which the current app structure handles okay
        // by re-showing the current question based on session index.

        // console.log("MindWell Navigator script loaded.");
    }

    // Auto-dismiss flash messages after a few seconds
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            // Add a class to trigger CSS transition for dismissal
            message.classList.add('dismiss');
            // Optionally remove the element from DOM after transition
            // setTimeout(() => message.remove(), 1000); // 500ms for opacity + some buffer
        }, 5000); // 5 seconds
    });

});