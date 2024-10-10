// Get the pop-up and the register button
const registerPopup = document.getElementById("registerPopup");
const registerBtn = document.getElementById("registerBtn");
const loginBtn = document.getElementById("loginBtn");
const loginPopup = document.getElementById("loginPopup");

// Load the form from the Flask route
function loadFormRegister() {
    fetch('/register_form')
        .then(response => response.text())
        .then(html => {
            registerPopup.innerHTML = html;

            // Get the close button after loading the form
            const closeBtn = document.querySelector(".close-popup");

            // Show the popup
            registerPopup.style.display = "block";

            // Close the pop-up when the "x" is clicked
            closeBtn.onclick = function() {
                registerPopup.style.display = "none";
            };

            // Close the pop-up if clicking outside the form
            window.onclick = function(event) {
                if (event.target == registerPopup) {
                    registerPopup.style.display = "none";
                }
            };

            // Handle form submission via AJAX
            const form = document.getElementById("registerform");
            form.onsubmit = function(event) {
                event.preventDefault(); // Prevent default form submission

                const formData = new FormData(form);
                fetch('/register', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Clear any previous flash messages
                        const existingFlashMessage = document.querySelector(".flash-message");
                        if (existingFlashMessage) {
                            existingFlashMessage.remove();
                        }

                        // Display flash message inside the popup
                        const flashMessage = document.createElement("p");
                        flashMessage.textContent = data.message;
                        flashMessage.classList.add("flash-message");
                        document.querySelector(".popup-content").appendChild(flashMessage);
                    }
                    else{
                        // Clear any previous flash messages
                        const existingFlashMessage = document.querySelector(".flash-message");
                        if (existingFlashMessage) {
                            existingFlashMessage.remove();
                        }

                        // Display flash message inside the popup
                        const flashMessage = document.createElement("p");
                        flashMessage.textContent = data.message;
                        flashMessage.classList.add("flash-message");
                        document.querySelector(".popup-content").appendChild(flashMessage);

                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            };
        })
        .catch(error => {
            console.error('Error loading the form:', error);
        });
}

function loadFormLogin() {
    fetch('/login_form')
        .then(response => response.text())
        .then(html => {
            loginPopup.innerHTML = html;
            // Get the close button after loading the form
            const closeBtn = document.querySelector(".close-popup");

            // Show the popup
            loginPopup.style.display = "block";

            // Close the pop-up when the "x" is clicked
            closeBtn.onclick = function() {
                loginPopup.style.display = "none";
            };

            // Close the pop-up if clicking outside the form
            window.onclick = function(event) {
                if (event.target == registerPopup) {
                    loginPopup.style.display = "none";
                }
            };

            // Handle form submission via AJAX
            const form = document.getElementById("loginform");
            form.onsubmit = function(event) {
                event.preventDefault(); // Prevent default form submission

                const formData = new FormData(form);
                fetch('/login', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Clear any previous flash messages
                        const existingFlashMessage = document.querySelector(".flash-message");
                        if (existingFlashMessage) {
                            existingFlashMessage.remove();
                        }

                        // Display flash message inside the popup
                        const flashMessage = document.createElement("p");
                        flashMessage.textContent = data.message;
                        flashMessage.classList.add("flash-message");
                        document.querySelector(".popup-content").appendChild(flashMessage);
                    }
                    else {
                        // Clear any previous flash messages
                        const existingFlashMessage = document.querySelector(".flash-message");
                        if (existingFlashMessage) {
                            existingFlashMessage.remove();
                        }

                        // Display flash message inside the popup
                        const flashMessage = document.createElement("p");
                        flashMessage.textContent = data.message;
                        flashMessage.classList.add("flash-message");
                        document.querySelector(".popup-content").appendChild(flashMessage);

                    }
    
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            };
        })
        .catch(error => {
            console.error('Error loading the form:', error);
        });
}

// When the user clicks the "Regístrate" button, load and show the form
registerBtn.onclick = function() {
    loadFormRegister();
}

loginBtn.onclick = function() {
    loadFormLogin();
}