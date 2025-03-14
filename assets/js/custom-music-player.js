document.addEventListener('DOMContentLoaded', function() {
    // Initialize all music players on the page
    initMusicPlayers();
});

// Global variable to track currently playing audio
let currentlyPlaying = null;
let isAudioOperationInProgress = false;

// Function to initialize custom music players
function initMusicPlayers() {
    
    // Get all music player elements
    const musicPlayers = document.querySelectorAll('.music-player-custom');
    
    // Initialize each music player
    musicPlayers.forEach(function(player, index) {
        
        // Get necessary elements
        const audio = player.querySelector('.main-audio');
        if (!audio) {
            console.error("Audio element not found for player", index);
            return;
        }
        
        const playPauseBtn = player.querySelector('.play-pause-btn');
        const progressBar = player.querySelector('.progress-bar');
        const progressArea = player.querySelector('.progress-area');
        const currentTimeEl = player.querySelector('.current');
        const durationEl = player.querySelector('.duration');
        const volumeIcon = player.querySelector('.volume-icon');
        const volumeSlider = player.querySelector('.volume-slider');
        const volumeProgress = player.querySelector('.volume-progress');
        
        // Set a unique ID for this player
        const playerId = player.dataset.compositionId || index;
        player.setAttribute('data-player-id', playerId);
        
        // Format time to mm:ss
        function formatTime(time) {
            const minutes = Math.floor(time / 60);
            const seconds = Math.floor(time % 60);
            return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
        }
        
        // When metadata is loaded (audio file is ready)
        audio.addEventListener('loadedmetadata', function() {
            // Set duration
            durationEl.textContent = formatTime(audio.duration);
            // Set volume to 80%
            audio.volume = 0.8;
            if (volumeProgress) {
                volumeProgress.style.width = '80%';
            }
        });
        
        // Log any errors with audio loading
        audio.addEventListener('error', function(e) {
            console.error("Audio error:", e);
            console.error("Error code:", audio.error ? audio.error.code : "unknown");
            console.error("Error message:", audio.error ? audio.error.message : "unknown");
            isAudioOperationInProgress = false;
        });
        
        // When audio time updates during playback
        audio.addEventListener('timeupdate', function() {
            // Calculate progress percentage
            const progressPercent = (audio.currentTime / audio.duration) * 100;
            // Update progress bar width
            progressBar.style.width = `${progressPercent}%`;
            // Update current time display
            currentTimeEl.textContent = formatTime(audio.currentTime);
            
            console.log("Current time: ", audio.currentTime);
            // If audio ended, reset to start
            if (audio.ended) {
                playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
                playPauseBtn.classList.remove('playing');
                progressBar.style.width = '0%';
                currentTimeEl.textContent = '0:00';
                currentlyPlaying = null;
                isAudioOperationInProgress = false;
            }
        });
        
        // Click on progress bar to seek
        if (progressArea) {
            progressArea.addEventListener('click', function(e) {
                // Get clicked position relative to progress area width
                const progressWidth = progressArea.offsetWidth;
                const clickedOffsetX = e.offsetX;
                const clickedPercent = (clickedOffsetX / progressWidth) * 100;
                
                // Calculate time to seek to
                const seekTime = (clickedPercent / 100) * audio.duration;
                
                audio.currentTime = parseFloat(seekTime);
                
                // If was paused, start playing
                if (audio.paused) {
                    playAudio(audio, playPauseBtn);
                }
            });
        }
        
        // Volume control
        if (volumeSlider) {
            volumeSlider.addEventListener('click', function(e) {
                const sliderWidth = volumeSlider.offsetWidth;
                const clickedOffsetX = e.offsetX;
                const clickedPercent = (clickedOffsetX / sliderWidth) * 100;
                
                // Set volume (0-1 range)
                audio.volume = clickedPercent / 100;
                volumeProgress.style.width = `${clickedPercent}%`;
                
                // Update volume icon based on level
                if (clickedPercent === 0) {
                    volumeIcon.className = 'fas fa-volume-mute volume-icon';
                } else if (clickedPercent < 40) {
                    volumeIcon.className = 'fas fa-volume-down volume-icon';
                } else {
                    volumeIcon.className = 'fas fa-volume-up volume-icon';
                }
            });
        }
        
        // Volume icon click to mute/unmute
        if (volumeIcon) {
            volumeIcon.addEventListener('click', function() {
                // Store volume before muting
                if (!audio.dataset.prevVolume) {
                    audio.dataset.prevVolume = audio.volume;
                }
                
                if (audio.volume > 0) {
                    // Mute - store previous volume
                    audio.dataset.prevVolume = audio.volume;
                    audio.volume = 0;
                    volumeProgress.style.width = '0%';
                    volumeIcon.className = 'fas fa-volume-mute volume-icon';
                } else {
                    // Unmute - restore previous volume
                    const prevVolume = parseFloat(audio.dataset.prevVolume) || 0.8;
                    audio.volume = prevVolume;
                    volumeProgress.style.width = `${prevVolume * 100}%`;
                    
                    if (prevVolume < 0.4) {
                        volumeIcon.className = 'fas fa-volume-down volume-icon';
                    } else {
                        volumeIcon.className = 'fas fa-volume-up volume-icon';
                    }
                }
            });
        }
        
        // Function to play audio
        function playAudio(audioElement, playButton) {
            if (isAudioOperationInProgress) {
                return;
            }
            
            isAudioOperationInProgress = true;
            
            // Set the UI immediately to give feedback
            playButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            // Play audio
            const playPromise = audioElement.play();
            if (playPromise !== undefined) {
                playPromise.then(() => {
                    currentlyPlaying = audioElement;
                    playButton.innerHTML = '<i class="fas fa-pause"></i>';
                    playButton.classList.add('playing');
                    isAudioOperationInProgress = false;
                }).catch(error => {
                    console.error("Error playing audio:", error);
                    // Reset UI
                    playButton.innerHTML = '<i class="fas fa-play"></i>';
                    playButton.classList.remove('playing');
                    isAudioOperationInProgress = false;
                    
                    // Check if it's an autoplay restriction
                    if (error.name === 'NotAllowedError') {
                        console.error("This appears to be an autoplay restriction. User interaction is required first.");
                        alert("Please interact with the page first before playing audio. This is a browser security feature.");
                    }
                });
            } else {
                console.error("Play promise is undefined");
                playButton.innerHTML = '<i class="fas fa-play"></i>';
                playButton.classList.remove('playing');
                isAudioOperationInProgress = false;
            }
        }
        
        // Function to pause audio
        function pauseAudio(audioElement, playButton) {
            if (isAudioOperationInProgress) {
                return;
            }
            
            // Pause audio
            audioElement.pause();
            currentlyPlaying = null;
            playButton.innerHTML = '<i class="fas fa-play"></i>';
            playButton.classList.remove('playing');
        }
        
        // Play/Pause button functionality
        if (playPauseBtn) {
            playPauseBtn.addEventListener('click', function(e) {
                // Prevent event bubbling
                e.stopPropagation();
                // If an operation is already in progress, ignore this click
                if (isAudioOperationInProgress) {
                    return;
                }
                
                // If this is not the currently playing audio and something else is playing
                if (currentlyPlaying && currentlyPlaying !== audio) {
                    // Pause any other playing audio
                    try {
                        currentlyPlaying.pause();
                        // Reset UI of other players
                        const allPlayButtons = document.querySelectorAll('.music-player-custom .play-pause-btn');
                        allPlayButtons.forEach(btn => {
                            btn.innerHTML = '<i class="fas fa-play"></i>';
                            btn.classList.remove('playing');
                        });
                    } catch (err) {
                        console.error("Error stopping other audio:", err);
                    }
                }
                
                // Simple toggle between play and pause
                if (audio.paused) {
                    playAudio(audio, playPauseBtn);
                } else {
                    pauseAudio(audio, playPauseBtn);
                }
            });
        }
    });
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Space bar - Play/Pause
    if (e.code === 'Space' && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
        e.preventDefault();
        if (currentlyPlaying) {
            // Find the current player and toggle play/pause
            const players = document.querySelectorAll('.music-player-custom');
            players.forEach(player => {
                const audio = player.querySelector('.main-audio');
                if (audio === currentlyPlaying) {
                    const playPauseBtn = player.querySelector('.play-pause-btn');
                    playPauseBtn.click();
                }
            });
        }
    }
});