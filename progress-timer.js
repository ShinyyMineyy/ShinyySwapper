// Progress Timer with realistic estimates
function createProgressTimer(type, enhanceMode = 'none') {
    // Base times per item in seconds
    const TIME_ESTIMATES = {
        image_none: 3,        // Normal face swap
        image_faces: 8,       // Face swap + GFPGAN
        image_full: 15,       // Face swap + Real-ESRGAN + GFPGAN
        video_frame: 0.5,     // Per frame (no enhance)
        video_frame_faces: 2, // Per frame + GFPGAN
        video_frame_full: 4,  // Per frame + Real-ESRGAN + GFPGAN
        multi_none: 4,        // Per face swap
        multi_faces: 10,      // Per face + GFPGAN
        multi_full: 18        // Per face + Real-ESRGAN + GFPGAN
    };
    
    let estimatedTimePerItem = TIME_ESTIMATES[`${type}_${enhanceMode}`] || 3;
    
    return {
        update: function(current, total, timerElement) {
            if (!timerElement || current === 0) return;
            const remaining = estimatedTimePerItem * (total - current);
            const mins = Math.floor(remaining / 60);
            const secs = Math.floor(remaining % 60);
            timerElement.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
        },
        reset: function() {
            // Not needed with fixed estimates
        }
    };
}

// Smooth progress animation
function animateProgress(element, targetPercent, duration = 500) {
    const currentPercent = parseFloat(element.style.width) || 0;
    const diff = targetPercent - currentPercent;
    const startTime = Date.now();
    
    function animate() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const newPercent = currentPercent + (diff * easeOut);
        
        element.style.width = newPercent + '%';
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    }
    
    requestAnimationFrame(animate);
}
