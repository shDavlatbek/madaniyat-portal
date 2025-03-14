/**
 * Dynamic Backgrounds Handler
 * 
 * This script sets background images from data attributes and handles fallbacks
 */
document.addEventListener('DOMContentLoaded', function() {
    // Set background images from data attributes
    document.querySelectorAll('[data-background]').forEach(function(element) {
        const bgImage = element.getAttribute('data-background');
        if (bgImage) {
            element.style.backgroundImage = `url('${bgImage}')`;
        }
    });

    // Handle onerror for images with fallbacks
    document.querySelectorAll('[data-fallback-src]').forEach(function(img) {
        img.onerror = function() {
            // Clear the error handler to prevent loops
            this.onerror = null;
            // Set the fallback image
            this.src = img.getAttribute('data-fallback-src');
        };
    });
}); 