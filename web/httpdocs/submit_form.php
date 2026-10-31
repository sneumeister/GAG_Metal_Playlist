<?php
declare(strict_types=1);

require_once __DIR__ . '/lib/bootstrap.php';

app_require_post();

if (app_honeypot_filled()) {
    app_json_response(['ok' => true, 'redirect' => 'https://github.com/sneumeister/GAG_Metal_Playlist/issues']);
}

$cfg = app_config();
$ip = app_client_ip();
$dir = (string) $cfg['rateLimitDir'];
$maxSubmit = (int) ($cfg['rateLimitSubmitPerIpPerDay'] ?? 10);

if (!RateLimit::allow($dir, 'submit_ip_' . $ip, $maxSubmit, 86400)) {
    app_json_response(['ok' => false, 'error' => 'Tageslimit für Einsendungen erreicht. Bitte morgen erneut versuchen.'], 429);
}

$type = trim((string) ($_POST['type'] ?? ''));
if (!in_array($type, ['vorschlag', 'korrektur', 'sonstiges'], true)) {
    app_json_response(['ok' => false, 'error' => 'Ungültige Anfrageart.'], 400);
}

$code = trim((string) ($_POST['code'] ?? ''));
if (!OneTimeCode::consume((string) $cfg['codesDir'], $code)) {
    app_json_response(['ok' => false, 'error' => 'Code ungültig oder abgelaufen. Bitte neuen Code anfordern.'], 400);
}

$fields = match ($type) {
    'vorschlag' => [
        'band' => trim((string) ($_POST['band'] ?? '')),
        'song' => trim((string) ($_POST['song'] ?? '')),
        'folge' => trim((string) ($_POST['folge'] ?? '')),
        'begruendung' => trim((string) ($_POST['begruendung'] ?? '')),
        'links' => trim((string) ($_POST['links'] ?? '')),
        'stufe' => trim((string) ($_POST['stufe'] ?? 'Unsicher')),
        'sonstiges' => trim((string) ($_POST['sonstiges'] ?? '')),
    ],
    'korrektur' => [
        'fehlerart' => trim((string) ($_POST['fehlerart'] ?? '')),
        'eintrag' => trim((string) ($_POST['eintrag'] ?? '')),
        'soll' => trim((string) ($_POST['soll'] ?? '')),
        'beleg' => trim((string) ($_POST['beleg'] ?? '')),
        'sonstiges' => trim((string) ($_POST['sonstiges'] ?? '')),
    ],
    'sonstiges' => [
        'bereich' => trim((string) ($_POST['bereich'] ?? '')),
        'kurz' => trim((string) ($_POST['kurz'] ?? '')),
        'details' => trim((string) ($_POST['details'] ?? '')),
        'sonstiges' => trim((string) ($_POST['sonstiges'] ?? '')),
    ],
};

$missing = match ($type) {
    'vorschlag' => array_filter([
        $fields['band'] === '' ? 'Band' : null,
        $fields['song'] === '' ? 'Songtitel' : null,
        $fields['folge'] === '' ? 'GAG-Folge' : null,
        $fields['begruendung'] === '' ? 'Kurze Begründung' : null,
    ]),
    'korrektur' => array_filter([
        $fields['fehlerart'] === '' ? 'Was ist falsch?' : null,
        $fields['eintrag'] === '' ? 'Betroffener Eintrag' : null,
        $fields['soll'] === '' ? 'Soll-Zustand' : null,
    ]),
    'sonstiges' => array_filter([
        $fields['bereich'] === '' ? 'Bereich' : null,
        $fields['kurz'] === '' ? 'Kurzbeschreibung' : null,
        $fields['details'] === '' ? 'Details' : null,
    ]),
};
if ($missing !== []) {
    app_json_response(['ok' => false, 'error' => 'Pflichtfelder fehlen: ' . implode(', ', $missing) . '.'], 400);
}

$pre = Precheck::check($type, $fields);
if (empty($pre['ok'])) {
    app_json_response([
        'ok' => false,
        'error' => (string) ($pre['message'] ?? 'Vorprüfung fehlgeschlagen.'),
    ], 400);
}

try {
    $issue = IssueBuilder::build($type, $fields);
} catch (Throwable $e) {
    app_json_response(['ok' => false, 'error' => 'Formular konnte nicht verarbeitet werden.'], 400);
}

try {
    $created = GitHubIssues::create(
        is_array($cfg['github'] ?? null) ? $cfg['github'] : [],
        $issue['title'],
        $issue['body'],
        $issue['labels']
    );
} catch (GitHubAuthException) {
    app_alert_github_auth($cfg);
    app_json_response([
        'ok' => false,
        'error' => 'Einsendung derzeit nicht möglich. Bitte später erneut versuchen.',
    ], 503);
} catch (Throwable) {
    app_json_response([
        'ok' => false,
        'error' => 'Issue konnte nicht angelegt werden. Bitte später erneut versuchen.',
    ], 502);
}

app_json_response([
    'ok' => true,
    'redirect' => $created['html_url'],
    'number' => $created['number'],
]);
