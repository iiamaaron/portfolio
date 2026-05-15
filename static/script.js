const form = document.getElementById('contact-form');
const feedback = document.getElementById('form-feedback');

form.addEventListener('submit', async function(e) {
    e.preventDefault();

    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const message = document.getElementById('message').value;

    try {
        const response = await fetch('/api/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, email, message })
        });

        const data = await response.json();

        if (response.ok) {
            feedback.style.color = 'green';
            feedback.textContent = 'Message sent! I will get back to you soon.';
            form.reset();
        } else {
            feedback.style.color = 'red';
            feedback.textContent = data.error || 'Something went wrong. Please try again.';
        }

    } catch (error) {
        feedback.style.color = 'red';
        feedback.textContent = 'Could not connect to the server. Please try again.';
    }
});