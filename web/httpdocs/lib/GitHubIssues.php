<?php
declare(strict_types=1);

final class GitHubIssues
{
    /**
     * @param array<string,mixed> $github
     * @param list<string> $labels
     * @return array{number:int,html_url:string}
     */
    public static function create(array $github, string $title, string $body, array $labels): array
    {
        $token = (string) ($github['token'] ?? '');
        $owner = (string) ($github['owner'] ?? '');
        $repo = (string) ($github['repo'] ?? '');
        $api = rtrim((string) ($github['apiBase'] ?? 'https://api.github.com'), '/');

        if ($token === '' || str_starts_with($token, 'YOUR_')) {
            throw new GitHubAuthException('GitHub-Token fehlt oder ist Platzhalter.');
        }

        $url = $api . '/repos/' . rawurlencode($owner) . '/' . rawurlencode($repo) . '/issues';
        $payload = json_encode([
            'title' => $title,
            'body' => $body,
            'labels' => array_values($labels),
        ], JSON_UNESCAPED_UNICODE);
        if ($payload === false) {
            throw new RuntimeException('Issue-JSON konnte nicht erzeugt werden.');
        }

        $ch = curl_init($url);
        if ($ch === false) {
            throw new RuntimeException('cURL nicht verfügbar.');
        }
        curl_setopt_array($ch, [
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $payload,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => [
                'Accept: application/vnd.github+json',
                'Authorization: Bearer ' . $token,
                'X-GitHub-Api-Version: 2022-11-28',
                'Content-Type: application/json',
                'User-Agent: gag-playlist-webform',
            ],
            CURLOPT_TIMEOUT => 30,
        ]);
        $raw = curl_exec($ch);
        $status = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $err = curl_error($ch);
        curl_close($ch);

        if ($raw === false) {
            throw new RuntimeException('GitHub-Request fehlgeschlagen: ' . $err);
        }
        if ($status === 401 || $status === 403) {
            throw new GitHubAuthException('GitHub-API abgelehnt (HTTP ' . $status . ').');
        }
        if ($status < 200 || $status >= 300) {
            throw new RuntimeException('GitHub-API Fehler HTTP ' . $status . ': ' . substr($raw, 0, 300));
        }
        $data = json_decode($raw, true);
        if (!is_array($data) || !isset($data['number'], $data['html_url'])) {
            throw new RuntimeException('Unerwartete GitHub-Antwort.');
        }
        return [
            'number' => (int) $data['number'],
            'html_url' => (string) $data['html_url'],
        ];
    }
}

final class GitHubAuthException extends RuntimeException
{
}
