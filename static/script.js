function SoyPapaNoel(){
    const cartasLeer = document.getElementById("NoSoyPapaNoel");
    cartasLeer.style.display = "none";

    const button = document.getElementById("LeerCartas");
    button.style.display = "block";
    button.onclick = function(){
        alert("Leyendo cartas...");
        fetch('/leer-cartas-descifradas')
        .then(response => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }
        return response.json();
    })
    .then(cartas => displayCartas(cartas))
    .catch(error => console.error('Error:', error));
    };
}

function displayCartas(cartas) {
    const cartasContainer = document.getElementById("cartasContainer");

    // Comprueba que existe cartasContainer
    if (!cartasContainer) {
        console.warn("cartasContainer not found on this page.");
        return;
    }

    cartasContainer.innerHTML = ''; // Borras lo que había antes

    cartas.forEach(carta => {
        const cartaElement = document.createElement("div");
        cartaElement.classList.add("carta");

        // Añadimos los detalles de las cartas
        cartaElement.innerHTML = `
            <strong>Nombre:</strong> ${carta.nombre}<br>
            <strong>Email:</strong> ${carta.email}<br>
            <strong>Ciudad:</strong> ${carta.ciudad}<br>
            <strong>País:</strong> ${carta.pais}<br>
            <strong>Carta:</strong> ${carta.carta}<br><br>
        `;

        // Añadimos la carta
        cartasContainer.appendChild(cartaElement);
    });
}


// Pop-up y botón de registro
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

            // Botton de X
            const closeBtn = registerPopup.querySelector(".close-popup");

            // Mostrar el popup
            registerPopup.style.display = "block";

            // Cerrar el popup
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
                        // If registration is successful, show the welcome message
                        //updateWelcomeMessage(data.username, data.avatarUrl);
                        alert("Registro exitoso");
                        // Close the registration popup
                        registerPopup.style.display = "none";

                    } else {
                        // Display error message in the popup
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
                        // Display success message, close popup, and update welcome message
                        alert("Inicio de sesión exitoso");
                        if (data.username === "PAPA NOEL"){
                            console.log("Username is PAPA NOEL");
                            alert("Wow, ¿eres Papá Noel de verdad?")
                            SoyPapaNoel();
                        }
                        else{
                            console.log("Username is not PAPA NOEL");
                        }
                        updateWelcomeMessage(data.username, data.avatar_url);
                        loginPopup.style.display = "none";


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

// After a successful login, update the welcome message and show the logout button
function updateWelcomeMessage(username, avatarUrl) {
    console.log("Actualizando mensaje de bienvenida para:", username);
    /*if (username === "PAPA NOEL"){
        console.log("Username is PAPA NOEL");
        alert("Wow, eres Papá Noel de verdad?")
        SoyPapaNoel();
    }
    else{
        console.log("Username is not PAPA NOEL");
    }*/
    const accountDiv = document.getElementById("account");

    if (!accountDiv) {
        console.error("No se encuentra el div con el ID 'account'");
        return;
    }

    // Create the user profile elements
    const userProfile = document.createElement("div");
    userProfile.classList.add("user-profile");

    const avatarImg = document.createElement("img");
    avatarImg.src = avatarUrl || 'static/images/fotoperfil.png';  // Default avatar if none provided
    avatarImg.alt = "Avatar de " + username;
    avatarImg.classList.add("user-avatar");

    const welcomeMessage = document.createElement("p");
    welcomeMessage.id = "welcome-message";
    welcomeMessage.textContent = "¡Hola, " + username + "!";

    const logoutBtn = document.createElement("button");
    logoutBtn.classList.add("enlarge");
    logoutBtn.id = "logoutBtn";
    logoutBtn.textContent = "Cerrar sesión";
    logoutBtn.onclick = function() {
        confirmLogout();
    };

    // Append the new elements to the account div
    userProfile.appendChild(avatarImg);
    userProfile.appendChild(welcomeMessage);
    userProfile.appendChild(logoutBtn);

    // Clear the current content of the account div and insert the new content
    accountDiv.innerHTML = '';
    accountDiv.appendChild(userProfile);
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

document.addEventListener('DOMContentLoaded', function() {
    // Selecciona el formulario
    const form = document.getElementById("formulario");
    alert("Formulario cargado");
    form.onsubmit = function(event) {
        event.preventDefault(); // Prevent default form submission
        alert("Estoy intentando enviar la carta");
        const formData = new FormData(form);
        fetch('/enviar-carta', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                alert('Oh no');
                throw new Error('Error al enviar la carta');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Mostrar éxito al usuario
            console.log('Carta enviada con éxito:', data);
            alert('Carta enviada correctamente');
                
            }
            
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Hubo un problema al enviar la carta.');
        });
    };
});
