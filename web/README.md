# Webformulare (Mitmachen)

Öffentliche Formulare unter `https://gag-playlist.sneumeister.de/` – ohne GitHub-Login, mit E-Mail-Code und Soft-Vorprüfung. Plan: `plans/anonyme-mitmachen-formulare.md`.

## Lokal

```text
web/httpdocs/   → Document Root (PHP)
web/private/    → config.php (Secrets), form-codes/, rate-limits/
```

1. `web/private/config.example.php` nach `config.php` kopieren und Secrets setzen.
2. Docroot auf `web/httpdocs` zeigen (**PHP ≥ 8.1**, cURL, OpenSSL, mbstring).
3. `private/` darf nicht öffentlich erreichbar sein.

**Plesk:** Domain/Subdomain → PHP-Einstellungen → Version **8.1+** (nicht 7.4).  
`open_basedir` = 2. Vorlage `{WEBSPACEROOT}{/}{:}{TMP}{/}{:}{/}var{/}lib{/}php{/}sessions` (nicht nur `{DOCROOT}` – sonst kein Zugriff auf `../private`).  
Diagnose: `/health.php` (`phpOk`, `configExists` müssen `true` sein).

## Deploy (Plesk Git)

Checkout nach `…/repo/` (nicht nach `httpdocs`). Deploy-Aktionen:

```bash
mkdir -p ../httpdocs ../private/form-codes ../private/rate-limits
find ../httpdocs -mindepth 1 -maxdepth 1 -exec rm -rf {} +
cp -a ./web/httpdocs/. ../httpdocs/
cp -f ./web/private/config.example.php ../private/
```

`config.php` einmal per SFTP nach `../private/`. Webhook bei GitHub für Push → Pull.

## Endpunkte

| Pfad | Rolle |
| --- | --- |
| `/` / `index.php` | Formular |
| `request_code.php` | Code per SMTP |
| `submit_form.php` | Soft-Precheck → GitHub-Issue → Redirect |
