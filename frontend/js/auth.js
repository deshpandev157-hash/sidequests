/* auth.js */
const auth = {
    saveUser(user) {
        localStorage.setItem('user', JSON.stringify(user));
        this.updateNav();
    },

    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },

    isLoggedIn() {
        return !!this.getUser();
    },

    logout() {
        localStorage.removeItem('user');
        window.location.href = 'index.html';
    },

    updateNav() {
        // Wait for DOM
        document.addEventListener('DOMContentLoaded', () => {
            const nav = document.querySelector('nav');
            if (!nav) return;

            // Simple login/stats swap
            const user = this.getUser();
            
            // Rebuild stats link to show name if logged in
            // Use current items as basis
            const currentLinks = Array.from(nav.querySelectorAll('a'));
            
            // Check if login/logout already exists
            const existingAuth = nav.querySelector('.auth-link');
            if (existingAuth) existingAuth.remove();

            const profileLink = currentLinks.find(a => a.href.includes('profile.html'));

            if (user) {
                // Update profile link text to show name
                if (profileLink) {
                    profileLink.innerHTML = `<span style="color:var(--accent-color)">${user.username}</span>'s Profile`;
                }
                
                // Add Logout
                const logoutBtn = document.createElement('a');
                logoutBtn.href = '#';
                logoutBtn.innerText = 'Logout';
                logoutBtn.className = 'auth-link';
                logoutBtn.style.color = '#ff4444';
                logoutBtn.onclick = (e) => {
                    e.preventDefault();
                    auth.logout();
                };
                nav.appendChild(logoutBtn);
            } else {
                // Not logged in
                if (profileLink) {
                    profileLink.innerText = 'Profile & Stats';
                }

                // Add Login
                const loginBtn = document.createElement('a');
                loginBtn.href = 'login.html';
                loginBtn.innerText = 'Login';
                loginBtn.className = 'auth-link';
                loginBtn.style.color = 'var(--accent-color)';
                nav.appendChild(loginBtn);
            }
        });
    }
};

// Auto-run nav update
auth.updateNav();
