
// Professional Analytics Dashboard JavaScript

// Initialize analytics when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeAnalytics();
    setupEventListeners();
    animateCounters();
    initializeCharts();
});

// Initialize AOS animations
function initializeAnalytics() {
    AOS.init({
        duration: 800,
        easing: 'ease-out-cubic',
        once: true,
        offset: 50
    });
}

// Setup all event listeners
function setupEventListeners() {
    // Search form handler
    const searchForm = document.getElementById('analyticsSearchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', handleAnalyticsSearch);
    }

    // Period selector buttons
    document.querySelectorAll('[data-period]').forEach(btn => {
        btn.addEventListener('click', handlePeriodChange);
    });

    // Platform checkboxes
    document.querySelectorAll('.platform-checkboxes input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', updatePlatformSelection);
    });

    // Tab switching
    document.querySelectorAll('#searchTabs button[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', handleTabSwitch);
    });

    // Image upload
    const imageInput = document.getElementById('imageInput');
    if (imageInput) {
        imageInput.addEventListener('change', handleImageUpload);
    }

    // Drag and drop for upload zones
    setupDragAndDrop();
}

// Animate counter numbers
function animateCounters() {
    const counters = document.querySelectorAll('.stat-value');
    
    counters.forEach(counter => {
        const target = parseInt(counter.textContent.replace(/[^\d]/g, ''));
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;
        
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            
            // Format number based on original format
            const originalText = counter.textContent;
            if (originalText.includes('₹')) {
                counter.textContent = '₹' + Math.floor(current).toLocaleString();
            } else {
                counter.textContent = Math.floor(current).toLocaleString();
            }
        }, 16);
    });
}

// Handle analytics search form submission
function handleAnalyticsSearch(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const productName = document.getElementById('productName').value.trim();
    const priceRange = document.getElementById('priceRange').value;
    
    // Get selected platforms
    const platforms = [];
    document.querySelectorAll('.platform-checkboxes input[type="checkbox"]:checked').forEach(cb => {
        platforms.push(cb.value);
    });
    
    // Validation
    if (!productName) {
        showAlert('Please enter a product name', 'warning');
        return;
    }
    
    if (platforms.length === 0) {
        showAlert('Please select at least one platform', 'warning');
        return;
    }
    
    // Show loading state
    showLoadingState();
    
    // Simulate API call with realistic delay
    setTimeout(() => {
        // Redirect to search page with parameters
        const params = new URLSearchParams({
            q: productName,
            platforms: platforms.join(','),
            price_range: priceRange,
            source: 'analytics'
        });
        window.location.href = `/search?${params.toString()}`;
    }, 2500);
}

// Show loading state with progress animation
function showLoadingState() {
    const resultsSection = document.getElementById('resultsSection');
    const loadingState = document.getElementById('loadingState');
    const resultsContent = document.getElementById('resultsContent');
    
    resultsSection.style.display = 'block';
    loadingState.style.display = 'block';
    resultsContent.style.display = 'none';
    
    // Animate progress bar
    const progressBar = document.querySelector('.progress-bar');
    let width = 0;
    const messages = [
        'Connecting to platforms...',
        'Scanning Amazon products...',
        'Analyzing Flipkart listings...',
        'Checking Croma inventory...',
        'Processing Snapdeal data...',
        'Comparing prices...',
        'Finalizing results...'
    ];
    let messageIndex = 0;
    
    const interval = setInterval(() => {
        width += Math.random() * 12 + 3;
        if (width >= 100) {
            width = 100;
            clearInterval(interval);
        }
        progressBar.style.width = width + '%';
        
        // Update loading message
        if (Math.random() > 0.7 && messageIndex < messages.length - 1) {
            messageIndex++;
            const messageElement = loadingState.querySelector('p');
            messageElement.textContent = messages[messageIndex];
            messageElement.style.animation = 'fadeInUp 0.5s ease-out';
        }
    }, 200);
    
    // Update button state
    const btn = document.querySelector('#analyticsSearchForm button[type="submit"]');
    btn.disabled = true;
    btn.querySelector('.btn-text').textContent = 'Analyzing Market...';
    btn.querySelector('.spinner-border').classList.remove('d-none');
}

// Handle period change
function handlePeriodChange(e) {
    document.querySelectorAll('[data-period]').forEach(b => b.classList.remove('active'));
    e.target.classList.add('active');
    
    const period = e.target.dataset.period;
    updateChartsForPeriod(period);
    
    // Add visual feedback
    e.target.style.transform = 'scale(0.95)';
    setTimeout(() => {
        e.target.style.transform = 'scale(1)';
    }, 150);
}

// Update platform selection
function updatePlatformSelection(e) {
    const checkbox = e.target;
    const label = checkbox.nextElementSibling;
    
    if (checkbox.checked) {
        label.style.animation = 'pulse 0.5s ease-out';
        label.style.color = '#3b82f6';
    } else {
        label.style.color = '';
    }
    
    // Update platform count
    const checkedCount = document.querySelectorAll('.platform-checkboxes input[type="checkbox"]:checked').length;
    const submitBtn = document.querySelector('#analyticsSearchForm button[type="submit"]');
    
    if (checkedCount === 0) {
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.6';
    } else {
        submitBtn.disabled = false;
        submitBtn.style.opacity = '1';
    }
}

// Handle tab switching
function handleTabSwitch(e) {
    const tabId = e.target.getAttribute('data-bs-target');
    const tabContent = document.querySelector(tabId);
    
    // Add entrance animation to tab content
    tabContent.style.animation = 'fadeInUp 0.5s ease-out';
    
    // Reset animation after completion
    setTimeout(() => {
        tabContent.style.animation = '';
    }, 500);
}

// Handle image upload
function handleImageUpload(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        const uploadZone = input.closest('.upload-zone');
        
        // Validate file type
        if (!file.type.startsWith('image/')) {
            showAlert('Please select a valid image file', 'error');
            return;
        }
        
        // Validate file size (10MB)
        if (file.size > 10 * 1024 * 1024) {
            showAlert('File size must be less than 10MB', 'error');
            return;
        }
        
        // Show upload progress
        uploadZone.innerHTML = `
            <div class="upload-progress">
                <i class="bi bi-check-circle display-4 text-success mb-3"></i>
                <h6>Image Uploaded Successfully</h6>
                <p class="text-muted">${file.name}</p>
                <div class="progress mt-3" style="height: 6px;">
                    <div class="progress-bar bg-success" style="width: 100%"></div>
                </div>
            </div>
        `;
        
        // Process image with OCR (simulate)
        setTimeout(() => {
            processImageWithOCR(file);
        }, 1000);
    }
}

// Setup drag and drop functionality
function setupDragAndDrop() {
    const uploadZones = document.querySelectorAll('.upload-zone');
    
    uploadZones.forEach(zone => {
        zone.addEventListener('dragover', handleDragOver);
        zone.addEventListener('dragleave', handleDragLeave);
        zone.addEventListener('drop', handleDrop);
    });
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('drag-over');
    e.currentTarget.style.borderColor = '#3b82f6';
    e.currentTarget.style.backgroundColor = '#eff6ff';
}

function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    e.currentTarget.style.borderColor = '';
    e.currentTarget.style.backgroundColor = '';
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    e.currentTarget.style.borderColor = '';
    e.currentTarget.style.backgroundColor = '';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const input = e.currentTarget.querySelector('input[type="file"]');
        input.files = files;
        handleImageUpload(input);
    }
}

// Process image with OCR
function processImageWithOCR(file) {
    // Simulate OCR processing
    const reader = new FileReader();
    reader.onload = function(e) {
        // Mock OCR result
        const mockProducts = ['iPhone 15', 'Samsung Galaxy S24', 'MacBook Pro', 'Sony WH-1000XM5'];
        const detectedProduct = mockProducts[Math.floor(Math.random() * mockProducts.length)];
        
        // Update search field
        document.getElementById('productName').value = detectedProduct;
        
        // Show success message
        showAlert(`Detected product: ${detectedProduct}`, 'success');
        
        // Switch to quick search tab
        const quickSearchTab = document.getElementById('quick-search-tab');
        quickSearchTab.click();
    };
    reader.readAsDataURL(file);
}

// Initialize charts
function initializeCharts() {
    initializePriceChart();
    initializePlatformChart();
}

// Initialize price trends chart
function initializePriceChart() {
    const ctx = document.getElementById('priceChart');
    if (!ctx) return;
    
    const chart = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Average Price',
                data: [45000, 42000, 44000, 41000, 43000, 40000],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#3b82f6',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: false
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#6b7280'
                    }
                },
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        color: '#6b7280',
                        callback: function(value) {
                            return '₹' + value.toLocaleString();
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            animation: {
                duration: 2000,
                easing: 'easeOutCubic'
            }
        }
    });
    
    // Store chart reference for updates
    window.priceChart = chart;
}

// Initialize platform distribution chart
function initializePlatformChart() {
    const ctx = document.getElementById('platformChart');
    if (!ctx) return;
    
    const chart = new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: ['Amazon', 'Flipkart', 'Croma', 'Snapdeal'],
            datasets: [{
                data: [35, 28, 22, 15],
                backgroundColor: ['#ff9500', '#047bd6', '#e42529', '#e60012'],
                borderWidth: 0,
                hoverBorderWidth: 3,
                hoverBorderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 12,
                            weight: '500'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed + '%';
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                duration: 2000,
                easing: 'easeOutCubic'
            }
        }
    });
    
    // Store chart reference for updates
    window.platformChart = chart;
}

// Update charts for selected period
function updateChartsForPeriod(period) {
    const priceData = {
        '7d': {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            data: [42000, 41500, 42200, 41800, 42500, 41200, 40800]
        },
        '30d': {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            data: [43000, 42000, 41500, 40800]
        },
        '90d': {
            labels: ['Month 1', 'Month 2', 'Month 3'],
            data: [45000, 42500, 40800]
        }
    };
    
    if (window.priceChart && priceData[period]) {
        window.priceChart.data.labels = priceData[period].labels;
        window.priceChart.data.datasets[0].data = priceData[period].data;
        window.priceChart.update('active');
    }
}

// Utility functions
function searchSuggestion(query) {
    document.getElementById('productName').value = query;
    document.getElementById('productName').focus();
    
    // Add visual feedback
    const input = document.getElementById('productName');
    input.style.animation = 'pulse 0.5s ease-out';
    setTimeout(() => {
        input.style.animation = '';
    }, 500);
}

function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alertTypes = {
        success: 'alert-success',
        error: 'alert-danger',
        warning: 'alert-warning',
        info: 'alert-info'
    };
    
    const alert = document.createElement('div');
    alert.className = `alert ${alertTypes[type]} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

function exportData() {
    showAlert('Exporting analytics data...', 'info');
    
    // Simulate export process
    setTimeout(() => {
        showAlert('Analytics data exported successfully!', 'success');
    }, 2000);
}

function refreshAnalytics() {
    showAlert('Refreshing analytics data...', 'info');
    
    // Animate refresh
    const refreshBtn = document.querySelector('button[onclick="refreshAnalytics()"]');
    const icon = refreshBtn.querySelector('i');
    icon.style.animation = 'spin 1s linear infinite';
    
    setTimeout(() => {
        icon.style.animation = '';
        showAlert('Analytics data refreshed!', 'success');
        
        // Refresh counters
        animateCounters();
        
        // Update charts
        if (window.priceChart) window.priceChart.update();
        if (window.platformChart) window.platformChart.update();
    }, 2000);
}

// Export functions for global access
window.searchSuggestion = searchSuggestion;
window.handleImageUpload = handleImageUpload;
window.exportData = exportData;
window.refreshAnalytics = refreshAnalytics;
