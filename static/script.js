// Get the pop-up and the register button
const registerPopup = document.getElementById("registerPopup");
const registerBtn = document.getElementById("registerBtn");
const loginBtn = document.getElementById("loginBtn");
const loginPopup = document.getElementById("loginPopup");

// Load the form from the Flask route for Registration
function loadFormRegister() {
    fetch('/register_form')
        .then(response => response.text())
        .then(html => {
            registerPopup.innerHTML = html;

            // Get the close button after loading the form
            const closeBtn = registerPopup.querySelector(".close-popup");

            // Show the popup
            registerPopup.style.display = "block";

            // Close the pop-up when the "x" is clicked
            closeBtn.onclick = function() {
                registerPopup.style.display = "none";
            };

            // Close the pop-up if clicking outside the form
            window.onclick = function(event) {
                if (event.target === registerPopup) {
                    registerPopup.style.display = "none";
                }
            };

            // Handle form submission via AJAX
            const form = document.getElementById("registerform");
            form.onsubmit = function(event) {
                event.preventDefault(); // Evitar el comportamiento de envío por defecto

                const formData = new FormData(form);
                fetch('/register', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Si el inicio de sesión es exitoso
                        window.location.href = '/';  // Redirigir a la página principal
                    } else {
                        // Mostrar mensaje de error en el popup
                        const flashMessage = document.createElement("p");
                        flashMessage.textContent = data.message;
                        flashMessage.classList.add("flash-message");
                        registerPopup.querySelector(".popup-content").appendChild(flashMessage);
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

// Load the login form from the Flask route
function loadFormLogin() {
    fetch('/login_form')
        .then(response => response.text())
        .then(html => {
            loginPopup.innerHTML = html;

            // Get the close button after loading the form
            const closeBtn = loginPopup.querySelector(".close-popup");

            // Show the popup
            loginPopup.style.display = "block";

            // Close the pop-up when the "x" is clicked
            closeBtn.onclick = function() {
                loginPopup.style.display = "none";
            };

            // Close the pop-up if clicking outside the form
            window.onclick = function(event) {
                if (event.target === loginPopup) {
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

                        // Display success message, close popup, and redirect
                        const flashMessage = document.createElement("p");
                        flashMessage.textContent = data.message;
                        flashMessage.classList.add("flash-message");
                        loginPopup.querySelector(".popup-content").appendChild(flashMessage);

                        // Close the popup and redirect to the homepage
                        loginPopup.style.display = "none";
                        window.location.href = '/';  // Redirect to homepage
                    } else {
                        // Display error message
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

// Button to see Password
function togglePassword(fieldId) {
    var passwordField = document.getElementById(fieldId);
    if (passwordField.type === "password") {
        passwordField.type = "text";
    } else {
        passwordField.type = "password";
    }
}

// Función para mostrar el popup
function showPopup(popupId) {
    var popup = document.getElementById(popupId);
    popup.style.display = 'block';
}

// Función para cerrar el popup
document.addEventListener("DOMContentLoaded", function () {
    var closeButtons = document.querySelectorAll('.close-popup');

    closeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var popup = this.closest('.popup-content');
            popup.style.display = 'none';
        });
    });
});

function confirmLogout() {
    var confirmAction = confirm("¿Estás seguro de que quieres cerrar sesión?");
    if (confirmAction) {
        window.location.href = '/logout';
    }
}

// When the user clicks the "Regístrate" button, load and show the form
registerBtn.onclick = function() {
    loadFormRegister();
}

// When the user clicks the "Inicia sesión" button, load and show the form
loginBtn.onclick = function() {
    loadFormLogin();
}
