// Account dropdown module
export function initializeAccountDropdown() {
    const accountBtn = document.getElementById('account-btn');
    const accountDropdown = document.getElementById('account-dropdown');

    if (accountBtn && accountDropdown) {
        accountBtn.addEventListener('click', function (event) {
            event.preventDefault();
            accountDropdown.classList.toggle('show');
        });

        window.addEventListener('click', function (event) {
            if (!accountBtn.contains(event.target) && !accountDropdown.contains(event.target)) {
                accountDropdown.classList.remove('show');
            }
        });
    }
} 