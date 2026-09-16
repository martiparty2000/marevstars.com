// Compose locally. No message is submitted to the website or marked as sent.
(() => {
    const form = document.querySelector('#contact-compose');
    if (!form) return;
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        if (!form.reportValidity()) return;
        const data = new FormData(form);
        const body = data.get('message').trim() + '\n\nИме: ' + data.get('name').trim() + '\nИмейл за обратна връзка: ' + data.get('email').trim();
        const subject = 'Запитване за тренировка — Марев Старс';
        window.location.href = 'mailto:office@marevstars.com?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
        document.querySelector('#compose-status').textContent = 'Изпратете писмото от вашата програма за имейл. Ако тя не се отвори, копирайте текста и пишете на office@marevstars.com.';
    });
    form.hidden = false;
})();
