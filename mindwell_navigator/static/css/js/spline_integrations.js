// mindwell_navigator/static/js/spline_integrations.js

import { Application } from 'https://unpkg.com/@splinetool/runtime@1.0.67/build/runtime.js';

// --- Helper function to load a Spline scene into a canvas ---
function loadSplineScene(canvasId, splineSceneUrl) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas with ID ${canvasId} not found.`);
        return null;
    }
    // Make sure the parent of the canvas has relative or absolute positioning
    // if you want to absolutely position the Spline canvas within it.
    // canvas.style.position = 'absolute';
    // canvas.style.top = '0';
    // canvas.style.left = '0';
    // canvas.style.width = '100%';
    // canvas.style.height = '100%';


    const app = new Application(canvas);
    app.load(splineSceneUrl)
        .then(() => {
            console.log(`Spline scene ${splineSceneUrl} loaded successfully on canvas ${canvasId}`);
            // You can interact with the loaded scene here if needed immediately
            // For example, find an object:
            // const myObject = app.findObjectByName('MyObjectNameInSpline');
            // if (myObject) {
            //     console.log('Found object:', myObject);
            // }
        })
        .catch(error => {
            console.error(`Error loading Spline scene ${splineSceneUrl}:`, error);
        });
    return app;
}

// --- Specific Spline Scene Initializations ---

// Example for a Welcome Page animation
export function initWelcomeAnimation(canvasId, sceneUrl) {
    const app = loadSplineScene(canvasId, sceneUrl);
    // Add any specific interactions for the welcome animation if 'app' is returned and valid
    if (app) {
        // e.g., app.addEventListener('mouseDown', (e) => { ... });
    }
}

// Example for an Assessment Progress indicator
let progressApp = null;
export function initAssessmentProgress(canvasId, sceneUrl) {
    progressApp = loadSplineScene(canvasId, sceneUrl);
}

export function updateAssessmentProgress(percentage) {
    if (progressApp && progressApp.findObjectByName) { // Check if app and findObjectByName are available
        // Let's assume you have an object in your Spline scene named 'ProgressBar'
        // And you want to control its scale or an animation based on the percentage.
        // This is highly dependent on how you set up your Spline scene.

        // Example 1: Control a variable 'ProgressValue' in Spline
        // progressApp.setVariable('ProgressValue', percentage);

        // Example 2: Trigger an animation state or control an object's property
        // const progressBarObject = progressApp.findObjectByName('ProgressFill');
        // if (progressBarObject) {
        //    progressBarObject.scale.x = percentage / 100;
        // }

        // Example 3: Emit an event that your Spline scene listens to
        // progressApp.emitEvent('progressUpdate', 'ProgressControlId', { value: percentage });

        console.log(`Updating Spline progress to ${percentage}% (Placeholder - implement actual Spline interaction)`);
        // IMPORTANT: You'll need to replace the above with actual interaction logic
        // based on how you've designed your 'Progress' scene in Spline.
        // For instance, if you have an animation you want to play up to a certain point:
        // progressApp.playAnimations({ names: ['MyProgressAnimation'], playMode: 'forward', progress: percentage/100 });

    }
}


// Example for Results Page visualization
let resultsApp = null;
export function initResultsVisualization(canvasId, sceneUrl, resultsData) {
    resultsApp = loadSplineScene(canvasId, sceneUrl);
    if (resultsApp) {
        resultsApp.addEventListener('load', () => { // Ensure scene is fully loaded before trying to set variables
             // Example: Pass the overall summary score or specific category scores to Spline
            if (resultsData.overallScore !== undefined) {
                // Assuming you have a variable named 'OverallWellnessScore' in your Spline scene
                // resultsApp.setVariable('OverallWellnessScore', resultsData.overallScore);
                console.log("Attempting to set Spline variable for overallScore:", resultsData.overallScore);
            }
            // You could iterate through resultsData.categoryScores and set multiple variables
            // for (const [category, score] of Object.entries(resultsData.categoryScores)) {
            // resultsApp.setVariable(category + 'Score', score);
            // }
            console.log("Results visualization data passed to Spline (Placeholder):", resultsData);
        });
    }
}

// --- Auto-initialize scenes based on data attributes in the HTML ---
document.addEventListener('DOMContentLoaded', () => {
    const welcomeCanvas = document.getElementById('splineWelcomeCanvas');
    if (welcomeCanvas && welcomeCanvas.dataset.splineUrl) {
        initWelcomeAnimation('splineWelcomeCanvas', welcomeCanvas.dataset.splineUrl);
    }

    const progressCanvas = document.getElementById('splineProgressCanvas');
    if (progressCanvas && progressCanvas.dataset.splineUrl) {
        initAssessmentProgress('splineProgressCanvas', progressCanvas.dataset.splineUrl);
        // Initial progress update if needed (e.g., if starting not from question 1)
        const progressBarElement = document.querySelector('.progress-bar'); // from assessment_page.html
        if (progressBarElement && progressBarElement.style.width) {
            const initialProgress = parseFloat(progressBarElement.style.width);
            if (!isNaN(initialProgress)) {
                updateAssessmentProgress(initialProgress);
            }
        }
    }

    const resultsCanvas = document.getElementById('splineResultsCanvas');
    if (resultsCanvas && resultsCanvas.dataset.splineUrl) {
        const resultsDataElement = document.getElementById('splineResultsData');
        let resultsData = {};
        if (resultsDataElement) {
            try {
                resultsData = JSON.parse(resultsDataElement.textContent);
            } catch (e) {
                console.error("Could not parse results data for Spline:", e);
            }
        }
        initResultsVisualization('splineResultsCanvas', resultsCanvas.dataset.splineUrl, resultsData);
    }
});