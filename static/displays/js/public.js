(function () {
    const refreshInterval = parseInt(document.querySelector('meta[http-equiv="refresh"]').content, 10);
    const countdownEl = document.createElement('div');
    countdownEl.className = 'refresh-countdown';
    document.body.appendChild(countdownEl);

    let remaining = refreshInterval;
    function tick() {
        if (!Number.isFinite(remaining)) {
            countdownEl.textContent = '';
            return;
        }
        countdownEl.textContent = `تازه‌سازی دوباره تا ${remaining} ثانیه`;
        remaining -= 1;
        if (remaining >= 0) {
            setTimeout(tick, 1000);
        }
    }
    tick();
})();
