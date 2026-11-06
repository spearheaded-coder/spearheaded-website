(function () {
  // Mobile menu
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.menu-toggle');
  if (header && toggle) {
    toggle.addEventListener('click', function () {
      var open = header.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.querySelector('.menu-label').textContent = open ? 'Close' : 'Menu';
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && header.classList.contains('is-open')) {
        header.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.querySelector('.menu-label').textContent = 'Menu';
        toggle.focus();
      }
    });
  }

  // Hero film: pause / play
  document.querySelectorAll('.film').forEach(function (film) {
    var btn = film.querySelector('.film-toggle');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var paused = film.classList.toggle('is-paused');
      btn.setAttribute('aria-label', paused ? 'Play the film' : 'Pause the film');
      btn.querySelector('.film-toggle-text').textContent = paused ? 'Play' : 'Pause';
    });
  });

  // Current year in footer
  var year = document.querySelector('[data-year]');
  if (year) year.textContent = String(new Date().getFullYear());

  // Consultation form: Netlify handles submission on the live site.
  // Anywhere else (a preview), stop the submit and say so instead of failing silently.
  var form = document.querySelector('form[data-netlify="true"]');
  if (form) {
    var live = /(^|\.)spearheaded\.ca$|\.netlify\.app$/.test(window.location.hostname);
    form.addEventListener('submit', function (e) {
      if (!live) {
        e.preventDefault();
        var status = form.querySelector('.form-status');
        if (status) status.textContent = 'This is a preview: the form will send once the site is live on Netlify.';
      }
    });
  }
})();
