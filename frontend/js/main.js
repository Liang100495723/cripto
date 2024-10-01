document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');
    const loginForm = document.getElementById('loginForm');
    const encryptionForm = document.getElementById('encryptionForm');
    const signatureForm = document.getElementById('signatureForm');

    // Registro de usuarios
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        // Llamada al backend para registrar al usuario
        const response = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const result = await response.json();
        alert(result.message);
    });

    // Autenticación de usuarios
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;
        
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const result = await response.json();
        alert(result.message);
    });

    // Cifrado de información
    encryptionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const plaintext = document.getElementById('plaintext').value;

        const response = await fetch('/encrypt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ plaintext })
        });
        const result = await response.json();
        document.getElementById('ciphertext').textContent = `Texto cifrado: ${result.ciphertext}`;
    });

    // Verificación de firma digital
    signatureForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = document.getElementById('data').value;

        const response = await fetch('/verify-signature', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data })
        });
        const result = await response.json();
        document.getElementById('signatureResult').textContent = `Resultado: ${result.verification}`;
    });
});
