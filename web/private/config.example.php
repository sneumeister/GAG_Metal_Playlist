<?php
/**
 * Vorlage für web/private/config.php (diese Datei wird versioniert).
 * Kopieren nach config.php und Secrets eintragen.
 */
declare(strict_types=1);

$private = __DIR__;

return [
    'baseUrl' => 'https://gag-playlist.sneumeister.de',

    'codesDir' => $private . DIRECTORY_SEPARATOR . 'form-codes',
    'rateLimitDir' => $private . DIRECTORY_SEPARATOR . 'rate-limits',

    'codeTtlSeconds' => 1200,

    'rateLimitCodePerIpPerHour' => 5,
    'rateLimitCodePerEmailPerHour' => 3,
    'rateLimitSubmitPerIpPerDay' => 10,

    'github' => [
        'token' => 'YOUR_GITHUB_PAT',
        'owner' => 'sneumeister',
        'repo' => 'GAG_Metal_Playlist',
        'apiBase' => 'https://api.github.com',
    ],

    'smtp' => [
        'host' => 'mxe842.netcup.net',
        'port' => 465,
        'encryption' => 'ssl',
        'user' => 'gag-playlist@sneumeister.de',
        'pass' => 'YOUR_SMTP_PASS',
        'from' => 'gag-playlist@sneumeister.de',
        'fromName' => 'GAG Metal Playlist',
    ],

    'alert' => [
        'email' => 'neumi@gmx.net',
        'name' => 'Stephan Neumeister',
    ],
];
