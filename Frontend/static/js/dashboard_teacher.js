/* document.addEventListener('DOMContentLoaded', function() {
    // Select all navigation links
    const navLinks = document.querySelectorAll('.navbar a');
    // Select all tab content sections
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Set default active tab
    showTab('mark-attendance');
    
    // Add click event listeners to all navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default anchor behavior
            const targetId = link.id.replace('-link', ''); // Get target tab id
            showTab(targetId);
        });
    });

    function showTab(tabId) {
        tabContents.forEach(tab => {
            if (tab.id === tabId) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });
    }
});
 */


document.addEventListener('DOMContentLoaded', function() {
    console.log('Document loaded and script initialized'); // Debugging message

    // Select all navigation links
    const navLinks = document.querySelectorAll('.navbar a');
    // Select all tab content sections
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Set default active tab
    showTab('mark-attendance');
    
    // Add click event listeners to all navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default anchor behavior
            console.log(`Navigating to tab: ${link.id}`); // Debugging message
            const targetId = link.id.replace('-link', ''); // Get target tab id
            showTab(targetId);
        });
    });

    function showTab(tabId) {
        tabContents.forEach(tab => {
            if (tab.id === tabId) {
                tab.classList.add('active');
                console.log(`Showing tab: ${tabId}`); // Debugging message
            } else {
                tab.classList.remove('active');
            }
        });
    }
});
