// Landing Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        offset: 100
    });
    initNavbar();
    initHeroAnimations();
    initPerformanceChart();
    initFAQ();
    initDownloadTracking();
    initScrollAnimations();
    initMobileMenu();
    
    console.log('01Agent Landing Page Initialized');
});

// Navbar functionality
function initNavbar() {
    const navbar = document.getElementById('navbar');
    let lastScrollY = window.scrollY;
    
    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;
        
        // Add scrolled class for styling
        if (currentScrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        // Hide/show navbar on scroll
        if (currentScrollY > lastScrollY && currentScrollY > 100) {
            navbar.style.transform = 'translateY(-100%)';
        } else {
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScrollY = currentScrollY;
    });
    
    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Hero animations
function initHeroAnimations() {
    // Animate hero elements on load
    const heroElements = document.querySelectorAll('.hero-badge, .hero-title, .hero-description, .hero-stats, .hero-cta, .hero-notice');
    
    heroElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            element.style.transition = 'all 0.8s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 200);
    });
    
    // Animate app preview
    const appPreview = document.querySelector('.app-preview');
    if (appPreview) {
        setTimeout(() => {
            appPreview.style.opacity = '0';
            appPreview.style.transform = 'perspective(1000px) rotateY(-15deg) rotateX(5deg) translateY(50px)';
            appPreview.style.transition = 'all 1s ease';
            
            setTimeout(() => {
                appPreview.style.opacity = '1';
                appPreview.style.transform = 'perspective(1000px) rotateY(-15deg) rotateX(5deg) translateY(0)';
            }, 100);
        }, 800);
    }
    
    // Animate typing indicator
    const typingIndicator = document.querySelector('.typing-indicator');
    if (typingIndicator) {
        setInterval(() => {
            typingIndicator.style.opacity = typingIndicator.style.opacity === '0' ? '1' : '0';
        }, 3000);
    }
}

// Performance chart animation
function initPerformanceChart() {
    const chartBars = document.querySelectorAll('.bar-fill');
    
    const animateChart = () => {
        chartBars.forEach((bar, index) => {
            setTimeout(() => {
                bar.style.width = bar.style.width || (index === 0 ? '100%' : '25%');
            }, index * 500);
        });
    };
    
    // Animate when chart comes into view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateChart();
                observer.unobserve(entry.target);
            }
        });
    });
    
    const chartContainer = document.querySelector('.performance-chart');
    if (chartContainer) {
        observer.observe(chartContainer);
    }
}

// FAQ functionality
function initFAQ() {
    window.toggleFaq = function(element) {
        const faqItem = element.parentElement;
        const isActive = faqItem.classList.contains('active');
        
        // Close all FAQ items
        document.querySelectorAll('.faq-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Open clicked item if it wasn't active
        if (!isActive) {
            faqItem.classList.add('active');
        }
    };
}

// Download tracking
function initDownloadTracking() {
    window.downloadApp = function(platform) {
        // Track download event
        if (typeof gtag !== 'undefined') {
            gtag('event', 'download', {
                'event_category': 'engagement',
                'event_label': platform,
                'value': 1
            });
        }
        
        // Show download started message
        showNotification(`Download started for ${platform}!`, 'success');
        
        // Simulate download (replace with actual download URLs)
        const downloadUrls = {
            windows: 'https://releases.01agent.ai/latest/01agent-windows-x64.exe',
            macos: 'https://releases.01agent.ai/latest/01agent-macos-universal.dmg',
            linux: 'https://releases.01agent.ai/latest/01agent-linux-x64.AppImage'
        };
        
        // Create temporary download link
        const link = document.createElement('a');
        link.href = downloadUrls[platform] || '#';
        link.download = '';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };
    
    window.trackDownload = function(source) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'download_intent', {
                'event_category': 'engagement',
                'event_label': source,
                'value': 1
            });
        }
    };
}

// Demo modal functionality
window.playDemo = function() {
    const modal = document.getElementById('demo-modal');
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Track demo view
        if (typeof gtag !== 'undefined') {
            gtag('event', 'demo_view', {
                'event_category': 'engagement',
                'value': 1
            });
        }
    }
};

window.closeDemo = function() {
    const modal = document.getElementById('demo-modal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
};

// Close modal on outside click
document.addEventListener('click', function(e) {
    const modal = document.getElementById('demo-modal');
    if (e.target === modal) {
        closeDemo();
    }
});

// Close modal on escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeDemo();
    }
});

// Mobile menu functionality
function initMobileMenu() {
    window.toggleMobileMenu = function() {
        const navLinks = document.querySelector('.nav-links');
        const mobileBtn = document.querySelector('.mobile-menu-btn');
        
        navLinks.classList.toggle('mobile-active');
        mobileBtn.classList.toggle('active');
    };
}

// Scroll animations
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fadeIn');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.feature-card, .testimonial-card, .pricing-card, .download-card, .metric').forEach(el => {
        observer.observe(el);
    });
}

// Notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">${getNotificationIcon(type)}</span>
            <span class="notification-message">${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 16px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        max-width: 400px;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    return icons[type] || icons.info;
}

function getNotificationColor(type) {
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    return colors[type] || colors.info;
}

// Add notification animations to CSS
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
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
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: white;
        font-size: 18px;
        cursor: pointer;
        padding: 0;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: background 0.2s ease;
    }
    
    .notification-close:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    
    .mobile-active {
        display: flex !important;
        position: fixed;
        top: 70px;
        left: 0;
        right: 0;
        background: var(--bg-primary);
        flex-direction: column;
        padding: 20px;
        border-bottom: 1px solid var(--border);
        box-shadow: var(--shadow-lg);
    }
    
    .mobile-menu-btn.active span:nth-child(1) {
        transform: rotate(45deg) translate(5px, 5px);
    }
    
    .mobile-menu-btn.active span:nth-child(2) {
        opacity: 0;
    }
    
    .mobile-menu-btn.active span:nth-child(3) {
        transform: rotate(-45deg) translate(7px, -6px);
    }
`;
document.head.appendChild(notificationStyles);

// Performance monitoring
function initPerformanceMonitoring() {
    // Monitor page load performance
    window.addEventListener('load', () => {
        setTimeout(() => {
            const perfData = performance.getEntriesByType('navigation')[0];
            const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
            
            console.log(`Page loaded in ${loadTime}ms`);
            
            // Track performance if analytics is available
            if (typeof gtag !== 'undefined') {
                gtag('event', 'page_load_time', {
                    'event_category': 'performance',
                    'value': Math.round(loadTime)
                });
            }
        }, 0);
    });
}

// Initialize performance monitoring
initPerformanceMonitoring();

// Easter egg - Konami code
let konamiCode = [];
const konamiSequence = [
    'ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown',
    'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight',
    'KeyB', 'KeyA'
];

document.addEventListener('keydown', (e) => {
    konamiCode.push(e.code);
    
    if (konamiCode.length > konamiSequence.length) {
        konamiCode.shift();
    }
    
    if (konamiCode.join(',') === konamiSequence.join(',')) {
        showNotification('🎉 Konami Code activated! You found the easter egg!', 'success');
        
        // Add special effect
        document.body.style.animation = 'rainbow 2s ease-in-out';
        setTimeout(() => {
            document.body.style.animation = '';
        }, 2000);
        
        konamiCode = [];
    }
});

// Add rainbow animation
const rainbowStyles = document.createElement('style');
rainbowStyles.textContent = `
    @keyframes rainbow {
        0% { filter: hue-rotate(0deg); }
        25% { filter: hue-rotate(90deg); }
        50% { filter: hue-rotate(180deg); }
        75% { filter: hue-rotate(270deg); }
        100% { filter: hue-rotate(360deg); }
    }
`;
document.head.appendChild(rainbowStyles);

// Preload critical resources
function preloadResources() {
    const criticalResources = [
        'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap'
    ];
    
    criticalResources.forEach(resource => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = resource;
        link.as = 'style';
        document.head.appendChild(link);
    });
}

preloadResources();
