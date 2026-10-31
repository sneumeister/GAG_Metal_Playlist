<?php
declare(strict_types=1);

/**
 * Diagnose ohne Secrets – nach dem Check wieder entfernen oder absichern.
 */
header('Content-Type: application/json; charset=utf-8');

$private = dirname(__DIR__) . DIRECTORY_SEPARATOR . 'private';
$config = $private . DIRECTORY_SEPARATOR . 'config.php';

$out = [
    'ok' => true,
    'php' => PHP_VERSION,
    'sapi' => PHP_SAPI,
    'extensions' => [
        'openssl' => extension_loaded('openssl'),
        'curl' => extension_loaded('curl'),
        'mbstring' => extension_loaded('mbstring'),
    ],
    'paths' => [
        'httpdocs' => __DIR__,
        'private' => $private,
        'configExists' => is_file($config),
        'privateWritable' => is_dir($private) && is_writable($private),
    ],
];

if (is_file($config)) {
    try {
        $cfg = require $config;
        $out['paths']['codesDir'] = isset($cfg['codesDir']) ? (string) $cfg['codesDir'] : null;
        $out['paths']['codesDirWritable'] = isset($cfg['codesDir'])
            && is_string($cfg['codesDir'])
            && ((is_dir($cfg['codesDir']) && is_writable($cfg['codesDir']))
                || (!is_dir($cfg['codesDir']) && is_writable(dirname($cfg['codesDir']))));
        $out['smtpHostSet'] = is_array($cfg['smtp'] ?? null)
            && (string) (($cfg['smtp']['host'] ?? '')) !== '';
        $out['smtpPassSet'] = is_array($cfg['smtp'] ?? null)
            && (string) (($cfg['smtp']['pass'] ?? '')) !== ''
            && !str_starts_with((string) $cfg['smtp']['pass'], 'YOUR_');
    } catch (Throwable $e) {
        $out['ok'] = false;
        $out['configError'] = $e->getMessage();
    }
} else {
    $out['ok'] = false;
}

echo json_encode($out, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
