
// Initialize AOS
AOS.init({
    duration: 800,
    once: true
});

// Theme Toggle Logic
function setupThemeToggle() {
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    if (!themeToggleBtn) return;

    const applyTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    };

    const getPreferredTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            return savedTheme;
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };

    const currentTheme = getPreferredTheme();
    applyTheme(currentTheme);

    themeToggleBtn.addEventListener('click', () => {
        const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        applyTheme(newTheme);
    });

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            applyTheme(e.matches ? 'dark' : 'light');
        }
    });
}

// Scroll Spy & Navigation Animation
function setupScrollHighlight() {
    const sections = document.querySelectorAll('div.main-content, div.search-container, section');
    const navLi = document.querySelectorAll('.navbar-nav .nav-item .nav-link.nav-anim');

    const highlightNav = () => {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            if (window.scrollY >= (sectionTop - 200)) {
                current = section.getAttribute('id');
            }
        });

        navLi.forEach(li => {
            li.classList.remove('active');
            if (li.getAttribute('href').includes(current)) {
                li.classList.add('active');
            }
        });
    };

    window.addEventListener('scroll', highlightNav);
    highlightNav();
}

// Alert System
function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show m-3`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    alertContainer.prepend(alert);
    
    setTimeout(() => {
        if (window.bootstrap && window.bootstrap.Alert) {
            bootstrap.Alert.getOrCreateInstance(alert).close();
        }
    }, 5000);
}

// Chatbot Logic
function toggleChat() {
    const chatWindow = document.getElementById('chatWindow');
    if (chatWindow) {
        chatWindow.classList.toggle('active');
        if (chatWindow.classList.contains('active')) {
            const chatInput = document.getElementById('chatInput');
            if (chatInput) chatInput.focus();
        }
    }
}

function handleEnter(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function addMessage(message, sender) {
    const chatBody = document.getElementById('chatBody');
    if (!chatBody) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;
    messageDiv.textContent = message;
    chatBody.appendChild(messageDiv);
    chatBody.scrollTop = chatBody.scrollHeight;
}

function sendMessage() {
    const input = document.getElementById('chatInput');
    if (!input) return;
    
    const message = input.value.trim();
    if (!message) return;

    // Add User Message
    addMessage(message, 'user');
    input.value = '';

    // Send to Backend
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.text) {
            addMessage(data.text, 'bot');
            
            // Handle actions
            if (data.action === 'search' && data.query) {
                setTimeout(() => {
                    window.location.href = `/search?q=${encodeURIComponent(data.query)}`;
                }, 500);
            } else if (data.action === 'navigate' && data.url) {
                setTimeout(() => {
                    window.location.href = data.url;
                }, 500);
            }
        }
    })
    .catch(error => {
        console.error('Chat error:', error);
        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
    });
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    setupThemeToggle();
    setupScrollHighlight();
});
