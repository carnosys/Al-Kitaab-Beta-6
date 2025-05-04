// Logo management module
export function initializeLogo() {
    const logoImg = document.querySelector(".logo img");
    const theme = localStorage.getItem("selectedTheme") || "auto";

    updateLogo(theme);

    function updateLogo(theme) {
        if (theme === "light") {
            logoImg.src = "/static/images/alkitab_logo_light.png";
        } else if (theme === "sepia") {
            logoImg.src = "/static/images/alkitab_logo_sepia.png";
        } else {
            // Default to dark theme logo
            logoImg.src = "/static/images/logo.png";
        }
        
        logoImg.style.width = "160px";
        logoImg.style.height = "auto";
    }
} 