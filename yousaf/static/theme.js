document.addEventListener("DOMContentLoaded", function () {
    const themeRadios = document.querySelectorAll('input[name="theme"]');
    const body = document.body;
    const container = document.querySelector(".settings-container");

    const quranFont = document.getElementById('quranFont');
    const fontStyle = document.getElementById('fontStyle');
    const sampleText = document.getElementsByClassName('sample-text')[0];

    // Apply theme when user changes selection
    themeRadios.forEach(radio => {
        radio.addEventListener("change", () => {
            const selectedTheme = document.querySelector('input[name="theme"]:checked').value;
            localStorage.setItem("selectedTheme", selectedTheme); // Save theme
            applyTheme(selectedTheme);
        });
    });

    function applyTheme(theme) {
        switch (theme) {
            case 'light':
                body.style.backgroundColor = '#ffffff';
                body.style.color = '#000000';
                container.style.backgroundColor = '#D8E3ED';

                quranFont.style.backgroundColor = '#BED0E1';
                quranFont.style.border = '#BED0E1';
                quranFont.style.color = '#000000';

                fontStyle.style.backgroundColor = '#BED0E1';
                fontStyle.style.border = '#BED0E1';
                fontStyle.style.color = '#000000';

                sampleText.style.backgroundColor = '#BED0E1';
                break;

            case 'sepia':
                body.style.backgroundColor = '#f4ecd8';
                body.style.color = '#5b4636';
                container.style.backgroundColor = '#F1D6B4';

                quranFont.style.backgroundColor = '#EBC18F';
                quranFont.style.border = '#EBC18F';
                quranFont.style.color = '#000000';

                fontStyle.style.backgroundColor = '#EBC18F';
                fontStyle.style.border = '#EBC18F';
                fontStyle.style.color = '#000000';

                sampleText.style.backgroundColor = '#EBC18F';
                break;

            case 'auto':
                const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
                if (prefersDark) {
                    applyDarkTheme();
                } else {
                    applyTheme('light');
                }
                break;

            default:
                applyDarkTheme();
        }
    }

    function applyDarkTheme() {
        body.style.backgroundColor = '#030916';
        body.style.color = '#ffffff';
        container.style.backgroundColor = '#150734';

        quranFont.style.backgroundColor = '#2c1354';
        quranFont.style.border = '#2c1354';
        quranFont.style.color = '#ffffff';

        fontStyle.style.backgroundColor = '#2c1354';
        fontStyle.style.border = '#2c1354';
        fontStyle.style.color = '#ffffff';

        sampleText.style.backgroundColor = '#2c1354';
    }

    // Apply saved theme on page load if available
    const savedTheme = localStorage.getItem("selectedTheme");
    if (savedTheme) {
        document.querySelector(`input[value="${savedTheme}"]`).checked = true;
        applyTheme(savedTheme);
    } else {
        const currentTheme = document.querySelector('input[name="theme"]:checked').value;
        applyTheme(currentTheme);
    }
});
