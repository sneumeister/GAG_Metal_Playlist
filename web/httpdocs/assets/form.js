(() => {
  const form = document.getElementById('mitmachen');
  const typeSelect = document.getElementById('type');
  const statusEl = document.getElementById('status');
  const btnCode = document.getElementById('btn-code');
  const btnSubmit = document.getElementById('btn-submit');

  function showStatus(msg, kind) {
    statusEl.hidden = false;
    statusEl.textContent = msg;
    statusEl.className = 'status ' + (kind || '');
  }

  function setBusy(busy) {
    btnCode.disabled = busy;
    btnSubmit.disabled = busy;
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
      showStatus('Bitte zuerst eine E-Mail-Adresse eintragen.', 'err');
      form.email.focus();
      return;
    }
    setBusy(true);
    showStatus('Code wird versendet …', '');
    try {
      const body = new FormData();
      body.set('email', email);
      body.set('website', form.website.value);
      const res = await fetch('request_code.php', { method: 'POST', body, credentials: 'same-origin' });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.ok) {
        showStatus(data.error || 'Code konnte nicht angefordert werden.', 'err');
        return;
      }
      showStatus(data.message || 'Code versendet. Bitte Posteingang und Spam prüfen.', 'ok');
      form.code.focus();
    } catch {
      showStatus('Netzwerkfehler beim Anfordern des Codes.', 'err');
    } finally {
      setBusy(false);
    }
  });

  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const code = form.code.value.trim();
    if (!/^[A-Za-z0-9]{8}$/.test(code)) {
      showStatus('Bitte den 8-stelligen Code aus der Mail eintragen.', 'err');
      form.code.focus();
      return;
    }
    setBusy(true);
    showStatus('Wird geprüft und eingereicht …', '');
    try {
      const body = new FormData(form);
      // Nur Felder des aktiven Typs mitsenden: disabled Inputs fehlen schon.
      const res = await fetch('submit_form.php', { method: 'POST', body, credentials: 'same-origin' });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.ok) {
        showStatus(data.error || 'Einsendung fehlgeschlagen.', 'err');
        return;
      }
      if (data.redirect) {
        showStatus('Issue angelegt – Weiterleitung …', 'ok');
        window.location.href = data.redirect;
        return;
      }
      showStatus('Gespeichert.', 'ok');
    } catch {
      showStatus('Netzwerkfehler beim Absenden.', 'err');
    } finally {
      setBusy(false);
    }
  });
})();
