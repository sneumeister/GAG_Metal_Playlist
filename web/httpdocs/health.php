<?php
declare(strict_types=1);

/**
 * Diagnose ohne Secrets – nach dem Check wieder entfernen oder absichern.
 * Läuft bewusst auch unter PHP 7.4 (kein match / str_starts_with).
 */
header('Content-Type: application/json; charset=utf-8');

$private = dirname(__DIR__) . DIRECTORY_SEPARATOR . 'private';
$config = $private . DIRECTORY_SEPARATOR . 'config.php';
$minPhp = '8.1.0';
$phpOk = version_compare(PHP_VERSION, $minPhp, '>=');

$out = array(
    'ok' => true,
    'php' => PHP_VERSION,
    'phpOk' => $phpOk,
    'phpMinRequired' => $minPhp,
    'sapi' => PHP_SAPI,
    'extensions' => array(
        'openssl' => extension_loaded('openssl'),
        'curl' => extension_loaded('curl'),
        'mbstring' => extension_loaded('mbstring'),
    ),
    'paths' => array(
        'httpdocs' => __DIR__,
        'private' => $private,
        'configExists' => is_file($config),
        'privateWritable' => is_dir($private) && is_writable($private),
    ),
);

if (!$phpOk) {
    $out['ok'] = false;
    $out['error'] = 'PHP zu alt: ' . PHP_VERSION . ' – in Plesk für gag-playlist.sneumeister.de auf PHP '
        . $minPhp . '+ umstellen (Hosting → PHP-Einstellungen).';
}

if (is_file($config)) {
    try {
        $cfg = require $config;
        $out['paths']['codesDir'] = isset($cfg['codesDir']) ? (string) $cfg['codesDir'] : null;
        $codesDir = isset($cfg['codesDir']) ? (string) $cfg['codesDir'] : '';
        $out['paths']['codesDirWritable'] = $codesDir !== ''
            && ((is_dir($codesDir) && is_writable($codesDir))
                || (!is_dir($codesDir) && is_writable(dirname($codesDir))));
        $smtp = (isset($cfg['smtp']) && is_array($cfg['smtp'])) ? $cfg['smtp'] : array();
        $pass = isset($smtp['pass']) ? (string) $smtp['pass'] : '';
        $out['smtpHostSet'] = isset($smtp['host']) && (string) $smtp['host'] !== '';
        $out['smtpPassSet'] = $pass !== '' && strpos($pass, 'YOUR_') !== 0;
    } catch (Exception $e) {
        $out['ok'] = false;
        $out['configError'] = $e->getMessage();
    } catch (Throwable $e) {
        $out['ok'] = false;
        $out['configError'] = $e->getMessage();
    }
} else {
    $out['ok'] = false;
}

echo json_encode($out, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
