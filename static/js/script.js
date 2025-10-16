// 🎯 PROFESSIONAL CTF PLATFORM JAVASCRIPT

document.addEventListener('DOMContentLoaded', function() {
    // 🎨 Initialize animations
    initializeAnimations();
    
    // 🎯 Initialize challenge interactions
    initializeChallenges();
    
    // 📊 Initialize scoreboard updates
    initializeScoreboard();
    
    // 🎮 Initialize hacker effects
    initializeHackerEffects();
    
    // 📱 Initialize responsive features
    initializeResponsive();
});

// 🎨 ANIMATION FUNCTIONS
function initializeAnimations() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card, .challenge-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in-up');
    });
    
    // Add typing effect to hero text
    const heroText = document.querySelector('.hero h1');
    if (heroText) {
        heroText.classList.add('typing-effect');
    }
}

// 🎯 CHALLENGE INTERACTIONS
function initializeChallenges() {
    // Add click handlers to challenge cards
    const challengeCards = document.querySelectorAll('.challenge-card');
    challengeCards.forEach(card => {
        card.addEventListener('click', function() {
            // Add ripple effect
            createRippleEffect(this, event);
            
            // Add glow effect
            this.style.boxShadow = '0 0 30px rgba(0, 212, 255, 0.5)';
            setTimeout(() => {
                this.style.boxShadow = '';
            }, 300);
        });
    });
    
    // Add hover effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px) scale(1.05)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// 📊 SCOREBOARD UPDATES
function initializeScoreboard() {
    // Auto-refresh scoreboard every 30 seconds
    setInterval(updateScoreboard, 30000);
    
    // Add real-time score animations
    const scoreElements = document.querySelectorAll('.score');
    scoreElements.forEach(score => {
        animateNumber(score);
    });
}

function updateScoreboard() {
    // This would typically fetch new data from the server
    console.log('Updating scoreboard...');
    
    // Add pulsing effect to indicate update
    const scoreboard = document.querySelector('.scoreboard');
    if (scoreboard) {
        scoreboard.style.animation = 'pulse 1s ease-in-out';
        setTimeout(() => {
            scoreboard.style.animation = '';
        }, 1000);
    }
}

function animateNumber(element) {
    const finalNumber = parseInt(element.textContent);
    let currentNumber = 0;
    const increment = finalNumber / 50;
    
    const timer = setInterval(() => {
        currentNumber += increment;
        if (currentNumber >= finalNumber) {
            currentNumber = finalNumber;
            clearInterval(timer);
        }
        element.textContent = Math.floor(currentNumber);
    }, 30);
}

// 🎮 HACKER EFFECTS
function initializeHackerEffects() {
    // Add matrix-style background effect
    createMatrixEffect();
    
    // Add glitch effect to logo
    const logo = document.querySelector('.logo');
    if (logo) {
        setInterval(() => {
            if (Math.random() < 0.1) {
                logo.style.animation = 'glitch 0.3s ease-in-out';
                setTimeout(() => {
                    logo.style.animation = '';
                }, 300);
            }
        }, 2000);
    }
}

function createMatrixEffect() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.zIndex = '-1';
    canvas.style.opacity = '0.1';
    canvas.style.pointerEvents = 'none';
    
    document.body.appendChild(canvas);
    
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const matrix = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789@#$%^&*()*&^%+-/~{[|`]}";
    const matrixArray = matrix.split("");
    
    const fontSize = 10;
    const columns = canvas.width / fontSize;
    
    const drops = [];
    for (let x = 0; x < columns; x++) {
        drops[x] = 1;
    }
    
    function draw() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = '#00ff88';
        ctx.font = fontSize + 'px monospace';
        
        for (let i = 0; i < drops.length; i++) {
            const text = matrixArray[Math.floor(Math.random() * matrixArray.length)];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);
            
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }
    
    setInterval(draw, 35);
}

// 📱 RESPONSIVE FEATURES
function initializeResponsive() {
    // Handle mobile menu
    const navLinks = document.querySelector('.nav-links');
    const menuToggle = document.createElement('button');
    menuToggle.innerHTML = '☰';
    menuToggle.className = 'menu-toggle';
    menuToggle.style.display = 'none';
    
    // Add mobile menu styles
    const style = document.createElement('style');
    style.textContent = `
        @media (max-width: 768px) {
            .menu-toggle {
                display: block !important;
                background: none;
                border: none;
                color: var(--neon-green);
                font-size: 1.5rem;
                cursor: pointer;
            }
            
            .nav-links {
                display: none;
                flex-direction: column;
                position: absolute;
                top: 100%;
                left: 0;
                width: 100%;
                background: rgba(26, 26, 26, 0.95);
                padding: 1rem;
            }
            
            .nav-links.active {
                display: flex;
            }
        }
    `;
    document.head.appendChild(style);
    
    // Add menu toggle functionality
    menuToggle.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });
    
    // Insert menu toggle
    const navContainer = document.querySelector('.nav-container');
    if (navContainer) {
        navContainer.appendChild(menuToggle);
    }
}

// 🎯 UTILITY FUNCTIONS
function createRippleEffect(element, event) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.style.position = 'absolute';
    ripple.style.borderRadius = '50%';
    ripple.style.background = 'rgba(0, 255, 136, 0.3)';
    ripple.style.transform = 'scale(0)';
    ripple.style.animation = 'ripple 0.6s linear';
    ripple.style.pointerEvents = 'none';
    
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// 🎯 FORM VALIDATION
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('input[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = 'var(--danger)';
            isValid = false;
        } else {
            input.style.borderColor = 'var(--neon-green)';
        }
    });
    
    return isValid;
}

// 🎯 NOTIFICATION SYSTEM
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '1000';
    notification.style.minWidth = '300px';
    notification.style.animation = 'slideInRight 0.3s ease-out';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-in';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// 🎯 KEYBOARD SHORTCUTS
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + K for quick search
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.querySelector('input[type="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals
    if (event.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.active');
        modals.forEach(modal => {
            modal.classList.remove('active');
        });
    }
});

// 🎯 PERFORMANCE OPTIMIZATION
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 🎯 SCROLL ANIMATIONS
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in-up');
        }
    });
}, observerOptions);

// Observe all cards and sections
document.querySelectorAll('.card, .challenge-card, .scoreboard').forEach(el => {
    observer.observe(el);
});

// 🎯 ADDITIONAL CSS ANIMATIONS
const additionalStyles = document.createElement('style');
additionalStyles.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    @keyframes glitch {
        0% { transform: translate(0); }
        20% { transform: translate(-2px, 2px); }
        40% { transform: translate(-2px, -2px); }
        60% { transform: translate(2px, 2px); }
        80% { transform: translate(2px, -2px); }
        100% { transform: translate(0); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
`;
document.head.appendChild(additionalStyles);
