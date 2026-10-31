(() => {
  const form = document.getElementById('mitmachen');
  const typeSelect = document.getElementById('type');
  const codeStatusEl = document.getElementById('code-status');
  const resultEl = document.getElementById('result');
  const resultTextEl = document.getElementById('result-text');
  const btnCode = document.getElementById('btn-code');
  const btnSubmit = document.getElementById('btn-submit');

  function showCodeStatus(msg, kind) {
    codeStatusEl.hidden = false;
    codeStatusEl.textContent = msg;
    codeStatusEl.className = 'status ' + (kind || '');
  }

  function clearCodeStatus() {
    codeStatusEl.hidden = true;
    codeStatusEl.textContent = '';
    codeStatusEl.className = 'status';
  }

  function showResult(msg, kind) {
    resultEl.hidden = false;
    resultEl.className = 'result ' + (kind || '');
    resultTextEl.textContent = msg;
  }

  function clearResult() {
    resultEl.hidden = true;
    resultEl.className = 'result';
    resultTextEl.textContent = '';
  }

  function setBusy(busy) {
    btnCode.disabled = busy;
    btnSubmit.disabled = busy;
  }

  /** Kurze Pause vor dem Issue-Link, damit die Triage-Action Labels/Kommentar setzen kann. */
  function redirectAfterCountdown(url, seconds) {
    let left = seconds;
    const tick = () => {
      showResult(
        left > 0
          ? 'Issue angelegt. Weiterleitung in ' + left + ' s …'
          : 'Issue angelegt – Weiterleitung …',
        'ok'
      );
      if (left <= 0) {
        window.location.href = url;
        return;
      }
      left -= 1;
      window.setTimeout(tick, 1000);
    };
    tick();
  }

  function syncPanels() {
    const t = typeSelect.value;
    form.querySelectorAll('.panel').forEach((panel) => {
      const on = panel.getAttribute('data-type') === t;
      panel.hidden = !on;
      panel.querySelectorAll('input, select, textarea').forEach((el) => {
        if (el.name === 'website') return;
        el.disabled = !on;
      });
    });
  }

  typeSelect.addEventListener('change', syncPanels);
  syncPanels();

  btnCode.addEventListener('click', async () => {
    const email = form.email.value.trim();
    if (!email) {
      showCodeStatus('Bitte zuerst eine E-Mail-Adresse eintragen.', 'err');
      form.email.focus();
      return;
    }
    setBusy(true);
    clearResult();
    showCodeStatus('Code wird versendet …', '');
    try {
      const body = new FormData();
      body.set('email', email);
      body.set('website', form.website.value);
      const res = await fetch('request_code.php', { method: 'POST', body, credentials: 'same-origin' });
      const raw = await res.text();
      let data = {};
      try {
        data = raw ? JSON.parse(raw) : {};
      } catch {
        showCodeStatus(
          'Serverantwort ungültig (HTTP ' + res.status + '). '
          + (raw ? raw.replace(/\s+/g, ' ').slice(0, 180) : 'Leerer Body – PHP-Fatal/Extensions prüfen (…/health.php).'),
          'err'
        );
        return;
      }
      if (!res.ok || !data.ok) {
        const phase = data.phase ? ' [' + data.phase + ']' : '';
        const fallback = !raw
          ? 'Code-Anforderung fehlgeschlagen (HTTP ' + res.status + ', leerer Body). Bitte /health.php prüfen.'
          : 'Code konnte nicht angefordert werden (HTTP ' + res.status + ').';
        showCodeStatus((data.error || fallback) + phase, 'err');
        return;
      }
      showCodeStatus(data.message || 'Code versendet. Bitte Posteingang und Spam prüfen.', 'ok');
      form.code.focus();
    } catch {
      showCodeStatus('Netzwerkfehler beim Anfordern des Codes.', 'err');
    } finally {
      setBusy(false);
    }
  });

  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const code = form.code.value.trim();
    if (!/^[A-Za-z0-9]{8}$/.test(code)) {
      showCodeStatus('Bitte den 8-stelligen Code aus der Mail eintragen.', 'err');
      form.code.focus();
      return;
    }
    setBusy(true);
    clearCodeStatus();
    showResult('Wird geprüft und eingereicht …', '');
    let holdBusy = false;
    try {
      const body = new FormData(form);
      const res = await fetch('submit_form.php', { method: 'POST', body, credentials: 'same-origin' });
      const raw = await res.text();
      let data = {};
      try {
        data = raw ? JSON.parse(raw) : {};
      } catch {
        showResult(
          'Serverantwort ungültig (HTTP ' + res.status + '). '
          + (raw ? raw.replace(/\s+/g, ' ').slice(0, 180) : 'Leerer Body.'),
          'err'
        );
        return;
      }
      if (!res.ok || !data.ok) {
        showResult(data.error || ('Einsendung fehlgeschlagen (HTTP ' + res.status + ').'), 'err');
        return;
      }
      if (data.redirect) {
        holdBusy = true;
        redirectAfterCountdown(data.redirect, 10);
        return;
      }
      showResult('Gespeichert.', 'ok');
    } catch {
      showResult('Netzwerkfehler beim Absenden.', 'err');
    } finally {
      if (!holdBusy) setBusy(false);
    }
  });
})();
