document.addEventListener('DOMContentLoaded', () => {
    const toggleButton = document.getElementById('toggle-mode');
    console.log('Script loaded');

    // Check if dark mode is enabled from localStorage
    if (localStorage.getItem('dark-mode') === 'enabled') {
        document.body.classList.add('dark-mode');
    }

    toggleButton.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        // Save the current mode to localStorage
        if (document.body.classList.contains('dark-mode')) {
            localStorage.setItem('dark-mode', 'enabled');
        } else {
            localStorage.setItem('dark-mode', 'disabled');
        }
        console.log('Dark mode toggled');
    });
});
