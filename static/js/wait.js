document.addEventListener('DOMContentLoaded', function() {
    let timeLeft = 100;
    const timerElement = document.getElementById('timer');

    const countdown = setInterval(() => {
        timeLeft--;
        timerElement.textContent = timeLeft;
        
        if (timeLeft <= 0) {
            clearInterval(countdown);
            window.location.href = '/';  // Redirect to home page
        }
    }, 1000);
});
