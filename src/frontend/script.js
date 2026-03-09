document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            errorMessage.textContent = ''; // Clear previous errors

            const username = loginForm.username.value;
            const password = loginForm.password.value;

            // Client-side validation
            if (!username || !password) {
                errorMessage.textContent = 'Username and password are required.';
                return;
            }

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
                });

                if (response.ok) {
                    const data = await response.json();
                    // Redirect to landing page on successful login
                    window.location.href = data.redirect_to || '/landing';
                } else {
                    const errorData = await response.json();
                    errorMessage.textContent = errorData.detail || 'Invalid username or password.';
                }
            } catch (error) {
                console.error('Login error:', error);
                errorMessage.textContent = 'An unexpected error occurred. Please try again later.';
            }
        });
    }

    // Simple check for a landing page (for demonstration)
    if (window.location.pathname === '/landing') {
        // You might want to fetch user data here to display on the landing page
        // For now, just display a welcome message
        const welcomeMessage = document.createElement('h1');
        welcomeMessage.textContent = 'Welcome to the Landing Page!';
        document.body.appendChild(welcomeMessage);

        const logoutButton = document.createElement('button');
        logoutButton.textContent = 'Logout';
        logoutButton.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/logout', {
                    method: 'GET',
                });
                if (response.ok) {
                    window.location.href = '/'; // Redirect to login page after logout
                } else {
                    console.error('Logout failed');
                }
            } catch (error) {
                console.error('Logout error:', error);
            }
        });
        document.body.appendChild(logoutButton);

        // Example of fetching user info after login
        fetch('/api/user')
            .then(res => res.json())
            .then(data => {
                if (data.username) {
                    const userInfo = document.createElement('p');
                    userInfo.textContent = `Logged in as: ${data.username}`;
                    document.body.insertBefore(userInfo, welcomeMessage.nextSibling);
                }
            })
            .catch(err => console.error('Failed to fetch user info:', err));
    }
});
