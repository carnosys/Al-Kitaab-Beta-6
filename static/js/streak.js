// Function to fetch current streak from the server
async function fetchCurrentStreak() {
    try {
        const response = await fetch('/api/get-streak');
        const data = await response.json();
        if (data.success) {
            updateStreakDisplay(data.current_streak);
        }
    } catch (error) {
        console.error('Error fetching streak:', error);
    }
}

// Function to update the streak display
function updateStreakDisplay(streak) {
    const streakCard = document.getElementById('streak-card');
    if (streakCard) {
        streakCard.innerHTML = `<span>${streak} day streak</span>`;
    }
}

// Check for streak updates every minute
setInterval(fetchCurrentStreak, 60000);

// Initial fetch when page loads
document.addEventListener('DOMContentLoaded', fetchCurrentStreak); 