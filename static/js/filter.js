// Filter and Search Functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const clearSearch = document.getElementById('clearSearch');
    const categoryFilter = document.getElementById('categoryFilter');
    const priceFilter = document.getElementById('priceFilter');
    const sortFilter = document.getElementById('sortFilter');
    const resetFilters = document.getElementById('resetFilters');
    const productsGrid = document.getElementById('productsGrid');
    const resultsCount = document.getElementById('resultsCount');
    
    let allProducts = Array.from(document.querySelectorAll('.product-card'));
    
    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            
            if (searchTerm.length > 0) {
                clearSearch.classList.add('active');
            } else {
                clearSearch.classList.remove('active');
            }
            
            applyFilters();
        });
    }
    
    // Clear search
    if (clearSearch) {
        clearSearch.addEventListener('click', function() {
            searchInput.value = '';
            clearSearch.classList.remove('active');
            applyFilters();
        });
    }
    
    // Category filter
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            applyFilters();
            updateFilterState();
        });
    }
    
    // Price filter
    if (priceFilter) {
        priceFilter.addEventListener('change', function() {
            applyFilters();
            updateFilterState();
        });
    }
    
    // Sort filter
    if (sortFilter) {
        sortFilter.addEventListener('change', function() {
            applyFilters();
            updateFilterState();
        });
    }
    
    // Reset all filters
    if (resetFilters) {
        resetFilters.addEventListener('click', function() {
            searchInput.value = '';
            clearSearch.classList.remove('active');
            categoryFilter.value = 'all';
            priceFilter.value = 'all';
            sortFilter.value = 'default';
            updateFilterState();
            applyFilters();
        });
    }
    
    function applyFilters() {
        const searchTerm = searchInput.value.toLowerCase();
        const category = categoryFilter.value;
        const priceRange = priceFilter.value;
        const sortBy = sortFilter.value;
        
        let visibleProducts = [];
        
        allProducts.forEach(product => {
            let isVisible = true;
            
            // Search filter
            if (searchTerm) {
                const productName = product.querySelector('h6').textContent.toLowerCase();
                const productDesc = product.querySelector('.product-description').textContent.toLowerCase();
                isVisible = productName.includes(searchTerm) || productDesc.includes(searchTerm);
            }
            
            // Category filter
            if (isVisible && category !== 'all') {
                const badges = product.querySelectorAll('.badge');
                let hasCategory = false;
                badges.forEach(badge => {
                    if (category === 'digital' && badge.textContent.includes('Numérique')) {
                        hasCategory = true;
                    }
                    if (category === 'physical' && badge.textContent.includes('Physique')) {
                        hasCategory = true;
                    }
                });
                isVisible = hasCategory;
            }
            
            // Price filter
            if (isVisible && priceRange !== 'all') {
                const priceText = product.querySelector('.product-price').textContent;
                const price = parseFloat(priceText.replace('$', ''));
                
                if (priceRange === 'low') {
                    isVisible = price < 20;
                } else if (priceRange === 'medium') {
                    isVisible = price >= 20 && price <= 50;
                } else if (priceRange === 'high') {
                    isVisible = price > 50;
                }
            }
            
            if (isVisible) {
                product.classList.remove('hidden-filter');
                visibleProducts.push(product);
            } else {
                product.classList.add('hidden-filter');
            }
        });
        
        // Sort products
        if (sortBy !== 'default') {
            visibleProducts.sort((a, b) => {
                if (sortBy === 'name-asc') {
                    const nameA = a.querySelector('h6').textContent;
                    const nameB = b.querySelector('h6').textContent;
                    return nameA.localeCompare(nameB);
                } else if (sortBy === 'name-desc') {
                    const nameA = a.querySelector('h6').textContent;
                    const nameB = b.querySelector('h6').textContent;
                    return nameB.localeCompare(nameA);
                } else if (sortBy === 'price-asc') {
                    const priceA = parseFloat(a.querySelector('.product-price').textContent.replace('$', ''));
                    const priceB = parseFloat(b.querySelector('.product-price').textContent.replace('$', ''));
                    return priceA - priceB;
                } else if (sortBy === 'price-desc') {
                    const priceA = parseFloat(a.querySelector('.product-price').textContent.replace('$', ''));
                    const priceB = parseFloat(b.querySelector('.product-price').textContent.replace('$', ''));
                    return priceB - priceA;
                }
            });
            
            // Reorder products in the grid
            visibleProducts.forEach(product => {
                productsGrid.appendChild(product.parentElement);
            });
        }
        
        // Update results count
        updateResultsCount(visibleProducts.length);
    }
    
    function updateResultsCount(count) {
        const totalProducts = allProducts.length;
        if (count === totalProducts) {
            resultsCount.textContent = `Affichage de tous les produits (${totalProducts})`;
        } else if (count === 0) {
            resultsCount.textContent = 'Aucun produit trouvé';
            resultsCount.style.color = '#e53e3e';
        } else {
            resultsCount.textContent = `${count} produit${count > 1 ? 's' : ''} trouvé${count > 1 ? 's' : ''}`;
            resultsCount.style.color = '#48bb78';
        }
    }
    
    function updateFilterState() {
        // Add visual feedback to active filters
        [categoryFilter, priceFilter, sortFilter].forEach(filter => {
            if (filter.value !== 'all' && filter.value !== 'default') {
                filter.classList.add('active');
            } else {
                filter.classList.remove('active');
            }
        });
    }
});
