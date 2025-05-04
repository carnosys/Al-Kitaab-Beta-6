// Theme management module
export function initializeTheme() {
    const theme = localStorage.getItem("selectedTheme") || "dark";
    const body = document.body;
    const header = document.querySelector("header");
    const footer = document.querySelector("footer");
    const footerContent = document.querySelector(".footer-content");
    const footerBottom = document.querySelector(".footer-bottom");
    const continueReading = document.querySelector(".continue-reading");
    const readingCard = document.querySelector(".reading-card");
    const streakScore = document.querySelector(".streak-score");
    const weeklyStreaks = document.querySelector(".weekly-streaks");
    const ayahOfTheDay = document.querySelector(".ayah-of-the-day");
    const streakCards = document.querySelectorAll(".streak-card, .weekly-card, .ayah-card");

    // Update icons immediately
    updateIcons(theme);

    // Apply theme
    applyTheme(theme);

    // Listen for theme changes
    window.addEventListener('storage', (e) => {
        if (e.key === 'selectedTheme') {
            applyTheme(e.newValue);
            updateIcons(e.newValue);
        }
    });

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (localStorage.getItem('selectedTheme') === 'auto') {
            const theme = e.matches ? 'dark' : 'light';
            applyTheme(theme);
            updateIcons(theme);
        }
    });

    function updateIcons(theme) {
        let suffix = "";
        switch (theme) {
            case "light":
                suffix = "_light.svg";
                break;
            case "sepia":
                suffix = "_sepia.svg";
                break;
            case "dark":
                // For dark theme, try dark variant first, then fall back to light
                suffix = "_dark.svg";
                break;
            case "auto":
                const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
                return updateIcons(prefersDark ? "dark" : "light");
        }

        // Update header icons
        const headerIcons = document.querySelectorAll('header img[data-base-path]');
        headerIcons.forEach(img => {
            const basePath = img.dataset.basePath;
            const iconName = img.dataset.iconName;
            
            if (basePath && iconName) {
                // Special case for user-solid icon which doesn't have theme variants
                if (iconName === 'user-solid') {
                    img.src = `${basePath}${iconName}.svg`;
                } else {
                    // For other icons, try the theme-specific suffix first
                    const themePath = `${basePath}${iconName}${suffix}`;
                    // Check if the file exists by trying to load it
                    const imgTest = new Image();
                    imgTest.onerror = () => {
                        // If theme variant doesn't exist, fall back to light theme
                        if (theme === 'dark') {
                            img.src = `${basePath}${iconName}_light.svg`;
                        } else {
                            img.src = themePath;
                        }
                    };
                    imgTest.onload = () => {
                        img.src = themePath;
                    };
                    imgTest.src = themePath;
                }
            }
        });

        // Update other icons in the page
        document.querySelectorAll('img[data-base-path]:not(header img)').forEach(img => {
            const basePath = img.dataset.basePath;
            const iconName = img.dataset.iconName;
            if (basePath && iconName) {
                img.src = `${basePath}${iconName}${suffix}`;
            }
        });
    }

    function applyTheme(theme) {
        switch (theme) {
            case 'light':
                applyLightTheme();
                break;
            case 'sepia':
                applySepiaTheme();
                break;
            case 'auto':
                const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
                if (prefersDark) {
                    applyDarkTheme();
                } else {
                    applyLightTheme();
                }
                break;
            default:
                applyDarkTheme();
        }
    }

    function applyLightTheme() {
        document.querySelector("#header-title span").style.color = 'black';
        body.style.backgroundColor = '#ffffff';
        body.style.color = 'black';
        header.style.backgroundColor = '#d8e3ed';
        header.style.color = 'black';
        footer.style.backgroundColor = '#d8e3ed';
        footer.style.color = 'black';
        footerContent.style.backgroundColor = '#ffffff';
        footerContent.style.color = 'black';
        footerBottom.style.backgroundColor = '#ffffff';
        footerBottom.style.color = 'black';

        if (continueReading) {
            continueReading.style.backgroundColor = '#d8e3ed';
            continueReading.style.color = 'black';
        }

        if (readingCard) {
            readingCard.style.backgroundColor = '#ffffff';
            readingCard.style.color = 'black';
        }

        if (streakScore) {
            streakScore.style.backgroundColor = '#d8e3ed';
            streakScore.style.color = 'black';
        }

        if (weeklyStreaks) {
            weeklyStreaks.style.backgroundColor = '#d8e3ed';
            weeklyStreaks.style.color = 'black';
        }

        if (ayahOfTheDay) {
            ayahOfTheDay.style.backgroundColor = '#d8e3ed';
            ayahOfTheDay.style.color = 'black';
        }

        streakCards.forEach(card => {
            card.style.backgroundColor = '#ffffff';
            card.style.color = 'black';
        });
    }

    function applySepiaTheme() {
        document.querySelector("#header-title span").style.color = '#5b4636';
        body.style.backgroundColor = '#f4ecd8';
        body.style.color = '#5b4636';
        header.style.backgroundColor = '#f1d6b4';
        header.style.color = '#5b4636';
        footer.style.backgroundColor = '#f1d6b4';
        footer.style.color = '#5b4636';
        footerContent.style.backgroundColor = '#f4ecd8';
        footerContent.style.color = '#5b4636';
        footerBottom.style.backgroundColor = '#f4ecd8';
        footerBottom.style.color = '#5b4636';

        if (continueReading) {
            continueReading.style.backgroundColor = '#f1d6b4';
            continueReading.style.color = '#5b4636';
        }

        if (readingCard) {
            readingCard.style.backgroundColor = '#f4ecd8';
            readingCard.style.color = '#5b4636';
        }

        if (streakScore) {
            streakScore.style.backgroundColor = '#f1d6b4';
            streakScore.style.color = '#5b4636';
        }

        if (weeklyStreaks) {
            weeklyStreaks.style.backgroundColor = '#f1d6b4';
            weeklyStreaks.style.color = '#5b4636';
        }

        if (ayahOfTheDay) {
            ayahOfTheDay.style.backgroundColor = '#f1d6b4';
            ayahOfTheDay.style.color = '#5b4636';
        }

        streakCards.forEach(card => {
            card.style.backgroundColor = '#f4ecd8';
            card.style.color = '#5b4636';
        });
    }

    function applyDarkTheme() {
        body.style.backgroundColor = '#030916';
        body.style.color = '#ffffff';
        header.style.backgroundColor = '#150734';
        header.style.color = '#ffffff';
        footer.style.backgroundColor = '#150734';
        footer.style.color = '#ffffff';
        footerContent.style.backgroundColor = '#0e0523';
        footerContent.style.color = '#ffffff';
        footerBottom.style.backgroundColor = '#0e0523';
        footerBottom.style.color = '#ffffff';

        if (continueReading) {
            continueReading.style.backgroundColor = '#150734';
            continueReading.style.color = '#ffffff';
        }

        if (readingCard) {
            readingCard.style.backgroundColor = '#0e0523';
            readingCard.style.color = '#ffffff';
        }

        if (streakScore) {
            streakScore.style.backgroundColor = '#150734';
            streakScore.style.color = '#ffffff';
        }

        if (weeklyStreaks) {
            weeklyStreaks.style.backgroundColor = '#150734';
            weeklyStreaks.style.color = '#ffffff';
        }

        if (ayahOfTheDay) {
            ayahOfTheDay.style.backgroundColor = '#150734';
            ayahOfTheDay.style.color = '#ffffff';
        }

        streakCards.forEach(card => {
            card.style.backgroundColor = '#0e0523';
            card.style.color = '#ffffff';
        });
    }
}
