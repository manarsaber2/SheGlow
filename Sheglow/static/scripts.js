// Show and hide the search bar
const searchIcon = document.getElementById('search-icon');
const searchBar = document.getElementById('search-bar');
const closeSearch = document.getElementById('close-search');
const searchInput = document.getElementById('search-input');
const suggestionsContainer = document.getElementById('suggestions-container');

searchIcon.addEventListener('click', () => {
    searchBar.style.display = 'block';
});

closeSearch.addEventListener('click', () => {
    searchBar.style.display = 'none';
    suggestionsContainer.innerHTML = ''; // Clear suggestions when closing the search bar
    suggestionsContainer.style.display = 'none'; // Hide suggestions container
});


// Toggle dropdown menu
function toggleDropdown() {
    const dropdown = document.querySelector('.dropdown');
    dropdown.classList.toggle('active');
}

// Close dropdown if clicked outside
window.addEventListener('click', function (event) {
    const dropdown = document.querySelector('.dropdown');
    const dropbtn = document.querySelector('.dropbtn');
    if (!dropdown.contains(event.target) && event.target !== dropbtn) {
        dropdown.classList.remove('active');
    }
});

searchInput.addEventListener('input', function () {
    const query = searchInput.value.trim();

    // If query is empty, clear suggestions
    if (!query) {
        suggestionsContainer.innerHTML = '';
        suggestionsContainer.style.display = 'none'; // Hide suggestions container when no input
        return;
    }

    // Make AJAX request to get search suggestions
    fetch(`/search_suggestions?q=${query}`)
        .then(response => response.json())
        .then(data => {
            // Clear previous suggestions
            suggestionsContainer.innerHTML = '';

            // Show the suggestions container if there are results
            if (data.length > 0) {
                suggestionsContainer.style.display = 'block'; // Show suggestions container

                data.forEach(product => {
                    const suggestionItem = document.createElement('div');
                    suggestionItem.classList.add('autocomplete-suggestion');
                    suggestionItem.textContent = product.ProductName;
                    suggestionItem.onclick = function () {
                        searchInput.value = product.ProductName;  // Fill input with selected suggestion
                        suggestionsContainer.innerHTML = '';  // Clear suggestions
                        suggestionsContainer.style.display = 'none'; // Hide suggestions container
                    };
                    suggestionsContainer.appendChild(suggestionItem);
                });
            } else {
                suggestionsContainer.style.display = 'none'; // Hide if no results
            }
        });
});
