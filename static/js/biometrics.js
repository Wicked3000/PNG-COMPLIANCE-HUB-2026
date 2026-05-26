/**
 * PNG Compliance Hub 2026 — Biometric (WebAuthn) Manager
 * Client-side handling for passwordless authentication.
 */

async function checkBiometricSupport() {
    return (
        window.PublicKeyCredential &&
        (await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable())
    );
}

// Helper: Convert Base64/Base64URL to Uint8Array
function _base64ToUint8Array(str) {
    str = str.replace(/-/g, "+").replace(/_/g, "/");
    while (str.length % 4) str += "=";
    return Uint8Array.from(atob(str), c => c.charCodeAt(0));
}

async function registerBiometrics() {
    console.log('Biometric Registration: Initiating...');
    
    // 1. Get registration options from server
    const response = await fetch('/accounts/biometric/register/options/');
    const options = await response.json();

    // 2. Transform bytes (WebAuthn expects ArrayBuffer)
    options.user.id = _base64ToUint8Array(options.user.id);
    options.challenge = _base64ToUint8Array(options.challenge);
    if (options.excludeCredentials) {
        options.excludeCredentials.forEach(cred => {
            cred.id = _base64ToUint8Array(cred.id);
        });
    }

    // 3. Create credential via browser
    try {
        const credential = await navigator.credentials.create({
            publicKey: options
        });
        
        // 4. Send back to server for verification
        const result = await fetch('/accounts/biometric/register/verify/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: credential.id,
                rawId: btoa(String.fromCharCode(...new Uint8Array(credential.rawId))),
                type: credential.type,
                response: {
                    attestationObject: btoa(String.fromCharCode(...new Uint8Array(credential.response.attestationObject))),
                    clientDataJSON: btoa(String.fromCharCode(...new Uint8Array(credential.response.clientDataJSON))),
                }
            })
        });

        if (result.ok) {
            alert('Success: Biometric device registered successfully!');
            location.reload();
        } else {
            const error = await result.json();
            console.error('Registration Verification Error:', error);
            alert('❌ Registration failed: ' + (error.message || 'Server error'));
        }
    } catch (err) {
        console.error('WebAuthn Error:', err);
        if (err.name === 'NotAllowedError') {
            alert('❌ Registration cancelled. Ensure you are on a secure (HTTPS) connection and have biometric hardware enabled.');
        } else {
            alert('❌ Biometric registration failed: ' + err.message);
        }
    }
}

async function loginWithBiometrics() {
    console.log('Biometric Login: Initiating...');
    
    // 1. Get assertion options from server
    const response = await fetch('/accounts/biometric/login/options/');
    const options = await response.json();

    // 2. Transform bytes
    options.challenge = _base64ToUint8Array(options.challenge);
    if (options.allowCredentials) {
        options.allowCredentials.forEach(cred => {
            cred.id = _base64ToUint8Array(cred.id);
        });
    }

    // 3. Request assertion (login)
    try {
        const assertion = await navigator.credentials.get({
            publicKey: options
        });

        // 4. Verify assertion on server
        const result = await fetch('/accounts/biometric/login/verify/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: assertion.id,
                rawId: btoa(String.fromCharCode(...new Uint8Array(assertion.rawId))),
                type: assertion.type,
                response: {
                    authenticatorData: btoa(String.fromCharCode(...new Uint8Array(assertion.response.authenticatorData))),
                    clientDataJSON: btoa(String.fromCharCode(...new Uint8Array(assertion.response.clientDataJSON))),
                    signature: btoa(String.fromCharCode(...new Uint8Array(assertion.response.signature))),
                    userHandle: assertion.response.userHandle ? btoa(String.fromCharCode(...new Uint8Array(assertion.response.userHandle))) : null,
                }
            })
        });

        if (result.ok) {
            window.location.href = '/dashboard/';
        } else {
            const error = await result.json();
            alert('❌ Authentication failed: ' + error.message);
        }
    } catch (err) {
        console.error('WebAuthn Assertion Error:', err);
        alert('❌ Biometric login failed.');
    }
}
