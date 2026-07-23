document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    
    loginForm.addEventListener('submit', (event) => {
        const usernameInput = document.getElementById('username').value.trim();
        
        if (usernameInput === "") {
            alert("Username cannot be empty spaces!");
            event.preventDefault(); // Stops the form from submitting to the backend
        }
    });
});