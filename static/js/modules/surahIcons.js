// Surah page icon management module
export function initializeSurahIcons() {
    const theme = localStorage.getItem("selectedTheme") || "auto";
    const icons = {
        play: document.querySelectorAll('.play img'),
        share: document.querySelectorAll('.share img'),
        tafseer: document.querySelectorAll('.tafseer img'),
        copy: document.querySelectorAll('.copy img'),
        bookmark: document.querySelectorAll('.bookmark img'),
        lastSeen: document.querySelectorAll('.last-seen img')
    };

    updateSurahIcons(theme);

    function updateSurahIcons(theme) {
        let suffix = "";

        switch (theme) {
            case "light":
                suffix = "_light.svg";
                break;
            case "sepia":
                suffix = "_sepia.svg";
                break;
            case "dark":
                suffix = "_dark.svg";
                break;
            case "auto":
                const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
                return updateSurahIcons(prefersDark ? "dark" : "light");
        }

        // Update play/pause icons
        icons.play.forEach(img => {
            const basePath = img.dataset.basePath;
            img.src = `${basePath}${suffix}`;
        });

        // Update share icons
        icons.share.forEach(img => {
            const basePath = img.dataset.basePath;
            img.src = `${basePath}${suffix}`;
        });

        // Update tafseer icons
        icons.tafseer.forEach(img => {
            const basePath = img.dataset.basePath;
            img.src = `${basePath}${suffix}`;
        });

        // Update copy icons
        icons.copy.forEach(img => {
            const basePath = img.dataset.basePath;
            img.src = `${basePath}${suffix}`;
        });

        // Update bookmark icons
        icons.bookmark.forEach(img => {
            const basePath = img.dataset.basePath;
            img.src = `${basePath}${suffix}`;
        });

        // Update last seen icons
        icons.lastSeen.forEach(img => {
            const basePath = img.dataset.basePath;
            img.src = `${basePath}${suffix}`;
        });
    }

    // Listen for theme changes
    window.addEventListener('storage', (e) => {
        if (e.key === 'selectedTheme') {
            updateSurahIcons(e.newValue);
        }
    });

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (localStorage.getItem('selectedTheme') === 'auto') {
            updateSurahIcons(e.matches ? 'dark' : 'light');
        }
    });
} 