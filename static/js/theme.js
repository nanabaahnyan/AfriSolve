// Theme toggle script for AfriSolve
(function () {
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
})();

window.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateToggleIcon(newTheme);
        });
    }

    function updateToggleIcon(theme) {
        const icon = document.getElementById('theme-toggle-icon');
        if (icon) {
            icon.textContent = theme === 'dark' ? '☀️' : '🌙';
        }
    }

    // Initialize toggle icon
    updateToggleIcon(document.documentElement.getAttribute('data-theme'));
});
