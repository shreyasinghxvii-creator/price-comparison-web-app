
// Fallback alert function if showAlert is not available
if (typeof showAlert === 'undefined') {
    function showAlert(message, type) {
        alert(message);
    }
}

// Search Form Handlers
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const imageSearchForm = document.getElementById('imageSearchForm');
    
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const productName = document.getElementById('productName').value;
            performSearch(productName);
        });
    }
    
    if (imageSearchForm) {
        imageSearchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const productImageInput = document.getElementById('productImage');
            const imageFile = productImageInput ? productImageInput.files[0] : null;
            
            console.log('Image upload submitted, file:', imageFile); // Debug log
            
            if (!imageFile) {
                alert('Please select an image file first!');
                return;
            }
            
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            if (loading) loading.style.display = 'block';
            if (results) results.innerHTML = '';
            
            const formData = new FormData();
            formData.append('image', imageFile);
            
            fetch('/upload-image', { method: 'POST', body: formData })
            .then(response => response.json())
            .then(data => {
                if (loading) loading.style.display = 'none';
                if (data.success) {
                    const productNameInput = document.getElementById('productName');
                    if (productNameInput) productNameInput.value = data.product_name;
                    performSearch(data.product_name);
                } else {
                    showAlert(`OCR Error: ${data.error}`, 'danger');
                }
            })
            .catch(error => {
                if (loading) loading.style.display = 'none';
                showAlert('Error processing image.', 'danger');
            });
        });
    }
    
    // Image upload handlers
    const productImage = document.getElementById('productImage');
    const uploadPreview = document.getElementById('uploadPreview');
    const uploadContent = document.querySelector('.upload-content');
    const scanButton = document.getElementById('scanButton');
    
    if (productImage) {
        productImage.addEventListener('change', function(e) {
            console.log('File input changed, files:', e.target.files); // Debug log
            const file = e.target.files[0];
            if (file) {
                handleImageSelection(file);
            } else {
                // Clear preview if no file selected
                clearUpload();
            }
        });
    }
    
    // Drag and drop functionality
    const uploadZone = document.getElementById('uploadZone');
    if (uploadZone) {
        uploadZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadZone.classList.add('drag-over');
        });
        
        uploadZone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadZone.classList.remove('drag-over');
        });
        
        uploadZone.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadZone.classList.remove('drag-over');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.type.startsWith('image/')) {
                    productImage.files = files;
                    handleImageSelection(file);
                }
            }
        });
    }
});

function handleImageSelection(file) {
    console.log('Handling image selection:', file.name, file.type, file.size); // Debug log
    
    const uploadPreview = document.getElementById('uploadPreview');
    const uploadContent = document.querySelector('.upload-content');
    const scanButton = document.getElementById('scanButton');
    const previewImage = document.getElementById('previewImage');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    
    if (!file.type.startsWith('image/')) {
        alert('Please select a valid image file (JPG, PNG, WebP)');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) { // 10MB limit
        alert('Image size should be less than 10MB');
        return;
    }
    
    // Show preview
    const reader = new FileReader();
    reader.onload = function(e) {
        if (previewImage) previewImage.src = e.target.result;
        if (fileName) fileName.textContent = file.name;
        if (fileSize) fileSize.textContent = (file.size / 1024 / 1024).toFixed(2) + ' MB';
        
        if (uploadContent) uploadContent.style.display = 'none';
        if (uploadPreview) uploadPreview.style.display = 'block';
        if (scanButton) scanButton.disabled = false;
    };
    reader.readAsDataURL(file);
}

function clearUpload() {
    const productImage = document.getElementById('productImage');
    const uploadPreview = document.getElementById('uploadPreview');
    const uploadContent = document.querySelector('.upload-content');
    const scanButton = document.getElementById('scanButton');
    
    if (productImage) productImage.value = '';
    if (uploadContent) uploadContent.style.display = 'block';
    if (uploadPreview) uploadPreview.style.display = 'none';
    if (scanButton) scanButton.disabled = true;
}

function openCamera() {
    // For now, just trigger the file input (mobile will show camera option)
    const productImage = document.getElementById('productImage');
    if (productImage) {
        productImage.setAttribute('capture', 'camera');
        productImage.click();
        // Remove capture attribute after click
        setTimeout(() => {
            productImage.removeAttribute('capture');
        }, 100);
    }
}

function quickSearch(productName) {
    const productNameInput = document.getElementById('productName');
    if (productNameInput) {
        productNameInput.value = productName;
    }
    performSearch(productName);
}

function performSearch(productName) {
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    if (loading) loading.style.display = 'block';
    if (results) results.innerHTML = '';
    
    // Scroll to results
    const searchContainer = document.querySelector('.search-container');
    if (searchContainer) {
         window.scrollTo({ top: searchContainer.offsetTop + searchContainer.offsetHeight - 70, behavior: 'smooth' });
    }
    
    fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'product_name=' + encodeURIComponent(productName)
    })
    .then(response => response.json())
    .then(data => {
        if (loading) loading.style.display = 'none';
        if (data.success) {
            displayResults(data.products, data.product_groups);
        } else {
            showAlert(`Search Error: ${data.error}`, 'danger');
        }
    })
    .catch(error => {
        if (loading) loading.style.display = 'none';
        showAlert('A critical error occurred. Please try again.', 'danger');
    });
}

function addToWishlist(product) {
    fetch('/add_to_wishlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(product)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message, 'success');
        } else {
            showAlert(data.error, 'warning'); 
        }
    })
    .catch(error => {
        showAlert('Error adding to wishlist.', 'danger');
    });
}

function displayResults(products, group_count) {
    const results = document.getElementById('results');
    if (!results) return;
    
    if (products.length === 0) {
        results.innerHTML = `<div class="alert alert-warning">No products found.</div>`;
        return;
    }
    
    const groups = {};
    products.forEach(product => {
        if (!groups[product.group_key]) groups[product.group_key] = [];
        groups[product.group_key].push(product);
    });
    
    let html = `<h2 class="mb-4">Found ${products.length} Products</h2><p class="text-muted mb-4">Comparing prices across ${group_count} product variants</p>`;
    
    Object.keys(groups).forEach(groupKey => {
        const groupProducts = groups[groupKey];
        const groupName = groupProducts[0].group_name;
        
        html += `
            <div class="product-group">
                <div class="group-header">
                    <h4>${groupName} - Price Comparison</h4>
                    <small class="text-muted">${groupProducts.length} offers found</small>
                </div>
                <div class="row">
        `;
        
        groupProducts.sort((a, b) => a.price - b.price);
        
        groupProducts.forEach((product, index) => {
            const imageUrl = product.image || 'https://via.placeholder.com/200x200?text=No+Image';
            const productData = JSON.stringify(product).replace(/'/g, "&apos;").replace(/"/g, "&quot;");
            const cardId = 'prod-' + product.website + Math.random().toString(36).substr(2, 9);

            html += `
                <div class="col-lg-4 col-md-6 mb-4">
                    <div class="product-card" id="${cardId}" style="animation-delay: ${index * 100}ms">
                        ${product.lowest_overall ? '<span class="badge best-price-badge"><i class="bi bi-stars"></i> Best Deal</span>' : ''}
                        ${product.lowest_in_group && !product.lowest_overall ? '<span class="badge best-in-group-badge">Best in Group</span>' : ''}

                        <div class="product-image-container">
                            <img src="${imageUrl}"
                                 alt="${product.name}"
                                 class="product-image"
                                 onerror="this.src='https://via.placeholder.com/200x200?text=No+Image'">
                        </div>
                        
                        <div class="product-info">
                            <span class="product-website">${product.website}</span>
                            <h5 class="product-title" title="${product.name}">${product.name}</h5>
                            
                            <div class="product-price">
                                <span class="price-value">₹${product.price}</span>
                            </div>

                            <div class="product-buttons">
                                ${product.url ? `<a href="${product.url}" target="_blank" class="btn btn-primary btn-sm"><i class="bi bi-eye-fill"></i> View Deal</a>` : ''}
                                <button class="btn btn-outline-danger btn-sm" onclick='addToWishlist(${productData})'>
                                    <i class="bi bi-heart"></i> Track
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `</div></div>`;
    });
    
    results.innerHTML = html;
    
    const cards = document.querySelectorAll('.product-card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('is-visible');
        }, index * 50); 
    });
}
