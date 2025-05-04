// Main JavaScript file that loads all modules

// Import modules
import { initializeAccountDropdown } from './modules/account.js';
import { initializeTheme } from './modules/theme.js';
import { initializeIcons } from './modules/icons.js';
import { initializeLogo } from './modules/logo.js';
import { initializeSurahIcons } from './modules/surahIcons.js';

// Initialize modules when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme first as it handles icon updates
    initializeTheme();
    
    // Then initialize other modules
    initializeAccountDropdown();
    initializeIcons();
    initializeLogo();
    initializeSurahIcons();
}); 