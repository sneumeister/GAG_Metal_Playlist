<?php
declare(strict_types=1);

require_once __DIR__ . '/lib/bootstrap.php';

app_require_post();

if (app_honeypot_filled()) {
    app_json_response(['ok' => true, 'message' => 'Wenn die Adresse gültig ist, wurde ein Code versendet.']);
}

$cfg = app_config();
$email = trim((string) ($_POST['email'] ?? ''));
if ($email === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    app_json_response(['ok' => false, 'error' => 'Bitte eine gültige E-Mail-Adresse angeben.'], 400);
}

$ip = app_client_ip();
$dir = (string) $cfg['rateLimitDir'];
$maxIp = (int) ($cfg['rateLimitCodePerIpPerHour'] ?? 5);
$maxMail = (int) ($cfg['rateLimitCodePerEmailPerHour'] ?? 3);

if (!RateLimit::allow($dir, 'code_ip_' . $ip, $maxIp, 3600)) {
    app_json_response(['ok' => false, 'error' => 'Zu viele Code-Anforderungen von dieser Adresse. Bitte später erneut versuchen.'], 429);
}
if (!RateLimit::allow($dir, 'code_mail_' . RateLimit::emailHash($email), $maxMail, 3600)) {
    app_json_response(['ok' => false, 'error' => 'Zu viele Code-Anforderungen für diese E-Mail. Bitte später erneut versuchen.'], 429);
}

$code = OneTimeCode::generate();
$ttl = (int) ($cfg['codeTtlSeconds'] ?? 1200);
$codesDir = (string) $cfg['codesDir'];

$minutes = max(1, (int) round($ttl / 60));
$body = "Dein Bestätigungscode für die GAG Metal Playlist:\n\n"
    . "  {$code}\n\n"
    . "Gültig ca. {$minutes} Minuten. Danach erneut „Code anfordern“.\n"
    . "Wenn du das nicht warst, diese Mail ignorieren.\n";

try {
    Mailer::send(
        is_array($cfg['smtp'] ?? null) ? $cfg['smtp'] : [],
        $email,
        $email,
        'Dein Code – GAG Metal Playlist',
        $body
    );
} catch (MailerException $e) {
    app_json_response([
        'ok' => false,
        'error' => $e->getMessage(),
        'phase' => $e->phase,
    ], 502);
} catch (Throwable $e) {
    app_json_response([
        'ok' => false,
        'error' => 'Unerwarteter Fehler beim Mailversand: ' . $e->getMessage(),
        'phase' => 'unknown',
    ], 502);
}

OneTimeCode::store($codesDir, $code, $ttl);
app_json_response(['ok' => true, 'message' => 'Wenn die Adresse gültig ist, wurde ein Code versendet.']);
