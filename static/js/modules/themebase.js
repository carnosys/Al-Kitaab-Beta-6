document.addEventListener("DOMContentLoaded", function () {
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

    applyTheme(theme); // Apply theme on load

    function applyTheme(theme) {
        switch (theme) {
            case 'light':

                document.querySelector("#header-title span").style.color='black';            
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

                document.querySelector("#reading-options span").style.color='black';
                document.querySelectorAll("#reading-options .tag").forEach(btn => btn.style.color = "black");
                document.querySelectorAll("#reading-options .tag").forEach(btn => btn.style.backgroundColor = "#d8e3ed");
                

                document.querySelectorAll('.surah-card').forEach(el => {el.style.backgroundColor = '#d8e3ed';});

                if (continueReading) {
                    continueReading.style.backgroundColor = '#d8e3ed';
                    continueReading.style.color = 'black';
                }

                if (readingCard) {
                    readingCard.style.backgroundColor = '#ffffff';
                    readingCard.style.color = 'black';
                    document.querySelector(".reading-name-arabic").style.color='black'
                    document.querySelector(".reading-details").style.color='black'

                }

                if (streakScore) {
                    streakScore.style.backgroundColor = '#d8e3ed';
                    streakScore.style.color = 'black';
                    document.querySelector("#streak-card span").style.color='black';

                }

                if (weeklyStreaks) {
                    weeklyStreaks.style.backgroundColor = '#d8e3ed';
                    weeklyStreaks.style.color = 'black';
                    document.querySelector("#weekly-card span").style.color='black';

                    
                }

                if (ayahOfTheDay) {
                    ayahOfTheDay.style.backgroundColor = '#d8e3ed';
                    ayahOfTheDay.style.color = 'black';
                    document.querySelector("#ayah-card span").style.color='black';

                }

                document.querySelector("#contact-us-list1").style.color='black';
                document.querySelector("#contact-us-list2").style.color='black';
                document.querySelector("#contact-us-list3").style.color='black';


                streakCards.forEach(card => {
                    card.style.backgroundColor = '#ffffff';
                    card.style.color = 'black';
                });
                break;

            case 'sepia':

            document.querySelector("#header-title span").style.color='#5b4636';  
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

                document.querySelector("#reading-options span").style.color='#5b4636';
                document.querySelectorAll("#reading-options .tag").forEach(btn => btn.style.color = "#5b4636");
                document.querySelectorAll("#reading-options .tag").forEach(btn => btn.style.backgroundColor = "#e9d9b0");

                document.querySelectorAll('.surah-card').forEach(el => {el.style.backgroundColor = '#f1d6b4';});
                
                if (continueReading) {
                    continueReading.style.backgroundColor = '#f1d6b4';
                    continueReading.style.color = '#5b4636';
                    document.querySelector(".reading-name-arabic").style.color='#5b4636'
                    document.querySelector(".reading-details").style.color='#5b4636'
                    readingCard.style.backgroundColor='#f4ecd8';
                }

                if (streakScore) {
                    streakScore.style.backgroundColor = '#f1d6b4';
                    streakScore.style.color = '#5b4636';
                    document.querySelector("#streak-card span").style.color='#5b4636';

                }

                if (weeklyStreaks) {
                    weeklyStreaks.style.backgroundColor = '#f1d6b4';
                    weeklyStreaks.style.color = '#5b4636';
                    document.querySelector("#weekly-card span").style.color='#5b4636';

                }

                if (ayahOfTheDay) {
                    ayahOfTheDay.style.backgroundColor = '#f1d6b4';
                    ayahOfTheDay.style.color = '#5b4636';
                    document.querySelector("#ayah-card span").style.color='#5b4636';

                }

                document.querySelector("#contact-us-list1").style.color='#5b4636';
                document.querySelector("#contact-us-list2").style.color='#5b4636';
                document.querySelector("#contact-us-list3").style.color='#5b4636';

                

                streakCards.forEach(card => {
                    card.style.backgroundColor = '#f4ecd8';
                    card.style.color = '#5b4636';
                });
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
});
