<?php
declare(strict_types=1);

/**
 * Gemeinsames Bootstrap für Formular-Endpunkte.
 */

function app_config(): array
{
    static $cfg = null;
    if ($cfg !== null) {
        return $cfg;
    }
    $path = dirname(__DIR__, 2) . DIRECTORY_SEPARATOR . 'private' . DIRECTORY_SEPARATOR . 'config.php';
    if (!is_file($path)) {
        http_response_code(500);
        header('Content-Type: text/plain; charset=utf-8');
        echo 'Konfiguration fehlt (private/config.php).';
        exit(1);
    }
    $cfg = require $path;
    if (!is_array($cfg)) {
        throw new RuntimeException('config.php muss ein Array zurückgeben.');
    }
    foreach (['codesDir', 'rateLimitDir'] as $dirKey) {
        $dir = $cfg[$dirKey] ?? null;
        if (is_string($dir) && $dir !== '' && !is_dir($dir)) {
            mkdir($dir, 0750, true);
        }
    }
    return $cfg;
}

function app_client_ip(): string
{
    $ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
    return is_string($ip) ? $ip : '0.0.0.0';
}

function app_normalize(string $s): string
{
    $s = mb_strtolower(trim($s), 'UTF-8');
    $s = preg_replace('/\s+/u', ' ', $s) ?? $s;
    return $s;
}

function app_json_response(array $payload, int $status = 200): void
{
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    exit;
}

function app_require_post(): void
{
    if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
        app_json_response(['ok' => false, 'error' => 'Nur POST erlaubt.'], 405);
    }
}

function app_honeypot_filled(): bool
{
    $hp = $_POST['website'] ?? '';
    return is_string($hp) && trim($hp) !== '';
}

/** @param array<string,mixed> $cfg */
function app_alert_github_auth(array $cfg): void
{
    $dir = (string) ($cfg['rateLimitDir'] ?? '');
    if ($dir === '' || !RateLimit::allow($dir, 'alert_github_auth', 1, 3600)) {
        return;
    }
    $alert = is_array($cfg['alert'] ?? null) ? $cfg['alert'] : [];
    $to = (string) ($alert['email'] ?? '');
    $name = (string) ($alert['name'] ?? $to);
    $smtp = is_array($cfg['smtp'] ?? null) ? $cfg['smtp'] : [];
    if ($to === '' || $smtp === []) {
        return;
    }
    try {
        Mailer::send(
            $smtp,
            $to,
            $name,
            '[GAG Playlist] GitHub-Token ungültig',
            "Die Webformulare konnten kein Issue anlegen (HTTP 401/403).\n"
            . "Bitte den Fine-grained PAT in private/config.php prüfen bzw. erneuern.\n\n"
            . 'Zeit: ' . date('c') . "\n"
            . 'IP (letzter Versuch): ' . app_client_ip() . "\n"
        );
    } catch (Throwable) {
        // Alert darf Submit nicht zusätzlich killen.
    }
}

require_once __DIR__ . '/RateLimit.php';
require_once __DIR__ . '/OneTimeCode.php';
require_once __DIR__ . '/Mailer.php';
require_once __DIR__ . '/GitHubIssues.php';
require_once __DIR__ . '/Precheck.php';
require_once __DIR__ . '/IssueBuilder.php';
