<?php
declare(strict_types=1);

/**
 * Gemeinsames Bootstrap für Formular-Endpunkte.
 * Benötigt PHP ≥ 8.1 (match, str_starts_with, …).
 */

if (PHP_VERSION_ID < 80100) {
    http_response_code(500);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode([
        'ok' => false,
        'error' => 'PHP ' . PHP_VERSION . ' ist zu alt. Bitte in Plesk für diese Subdomain PHP 8.1 oder neuer einstellen (aktuell erforderlich wegen match/str_starts_with).',
        'phase' => 'php',
        'php' => PHP_VERSION,
    ], JSON_UNESCAPED_UNICODE);
    exit(1);
}

function app_private_dir(): string
{
    return dirname(__DIR__, 2) . DIRECTORY_SEPARATOR . 'private';
}

function app_config_path(): string
{
    return app_private_dir() . DIRECTORY_SEPARATOR . 'config.php';
}

function app_register_fatal_json(): void
{
    static $done = false;
    if ($done) {
        return;
    }
    $done = true;
    register_shutdown_function(static function (): void {
        $err = error_get_last();
        if ($err === null) {
            return;
        }
        $fatalTypes = [E_ERROR, E_PARSE, E_CORE_ERROR, E_COMPILE_ERROR, E_USER_ERROR];
        if (!in_array((int) $err['type'], $fatalTypes, true)) {
            return;
        }
        if (headers_sent()) {
            return;
        }
        http_response_code(500);
        header('Content-Type: application/json; charset=utf-8');
        $msg = (string) ($err['message'] ?? 'Unbekannter Fatal-Error');
        $file = basename((string) ($err['file'] ?? ''));
        $line = (int) ($err['line'] ?? 0);
        echo json_encode([
            'ok' => false,
            'error' => 'PHP-Fehler: ' . $msg . ($file !== '' ? " ({$file}:{$line})" : ''),
            'phase' => 'php',
        ], JSON_UNESCAPED_UNICODE);
    });
}

app_register_fatal_json();

function app_config(): array
{
    static $cfg = null;
    if ($cfg !== null) {
        return $cfg;
    }
    $path = app_config_path();
    if (!is_file($path)) {
        app_json_response([
            'ok' => false,
            'error' => 'Server-Konfiguration fehlt (private/config.php unter '
                . app_private_dir() . '). Bitte per SFTP anlegen.',
            'phase' => 'config',
        ], 500);
    }
    $cfg = require $path;
    if (!is_array($cfg)) {
        app_json_response([
            'ok' => false,
            'error' => 'config.php muss ein Array zurückgeben.',
            'phase' => 'config',
        ], 500);
    }
    foreach (['codesDir', 'rateLimitDir'] as $dirKey) {
        $dir = $cfg[$dirKey] ?? null;
        if (is_string($dir) && $dir !== '' && !is_dir($dir)) {
            if (!@mkdir($dir, 0750, true) && !is_dir($dir)) {
                app_json_response([
                    'ok' => false,
                    'error' => 'Verzeichnis nicht anlegbar: ' . $dir . ' (Rechte prüfen).',
                    'phase' => 'config',
                ], 500);
            }
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
    $s = trim($s);
    if (function_exists('mb_strtolower')) {
        $s = mb_strtolower($s, 'UTF-8');
    } else {
        $s = strtolower($s);
    }
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
