<?php
declare(strict_types=1);

final class Precheck
{
    private const PLAYLIST_URL = 'https://raw.githubusercontent.com/sneumeister/GAG_Metal_Playlist/main/data/GAG_Metal_Playlist.json';
    private const REJECTED_URL = 'https://raw.githubusercontent.com/sneumeister/GAG_Metal_Playlist/main/data/rejected.json';
    private const SONGS_URL = 'https://raw.githubusercontent.com/sneumeister/GAG_Metal_Playlist/main/data/songs.json';

    /**
     * @param array<string,string> $fields
     * @return array{ok:bool,message?:string}
     */
    public static function check(string $type, array $fields): array
    {
        if ($type === 'sonstiges') {
            return ['ok' => true];
        }

        try {
            $playlist = self::fetchJson(self::PLAYLIST_URL);
            $rejected = self::fetchJson(self::REJECTED_URL);
            $songs = self::fetchJson(self::SONGS_URL);
        } catch (Throwable) {
            // Abruf fehlgeschlagen → nicht blockieren.
            return ['ok' => true];
        }

        $plEntries = is_array($playlist['entries'] ?? null) ? $playlist['entries'] : [];
        $rjEntries = is_array($rejected['entries'] ?? null) ? $rejected['entries'] : [];
        $songList = is_array($songs) ? $songs : [];

        if ($type === 'vorschlag') {
            return self::checkVorschlag($fields, $plEntries, $rjEntries, $songList);
        }
        if ($type === 'korrektur') {
            return self::checkKorrektur($fields, $plEntries, $rjEntries, $songList);
        }
        return ['ok' => true];
    }

    /**
     * @param array<string,string> $fields
     * @param list<mixed> $plEntries
     * @param list<mixed> $rjEntries
     * @param list<mixed> $songList
     * @return array{ok:bool,message?:string}
     */
    private static function checkVorschlag(array $fields, array $plEntries, array $rjEntries, array $songList): array
    {
        $band = app_normalize($fields['band'] ?? '');
        $song = app_normalize($fields['song'] ?? '');
        $episodeId = self::extractEpisodeId($fields['folge'] ?? '');
        if ($band === '' || $song === '') {
            return ['ok' => false, 'message' => 'Band und Songtitel sind erforderlich.'];
        }

        foreach ($plEntries as $e) {
            if (!is_array($e)) {
                continue;
            }
            $eb = app_normalize((string) ($e['band'] ?? ''));
            $et = app_normalize((string) ($e['songTitle'] ?? ''));
            if ($eb !== $band || $et !== $song) {
                continue;
            }
            if ($episodeId === null || (int) ($e['episodeId'] ?? -1) === $episodeId) {
                return [
                    'ok' => false,
                    'message' => 'Dieses Paar steht bereits in der Playlist'
                        . ($episodeId !== null ? ' (Folge #' . $episodeId . ')' : '')
                        . '.',
                ];
            }
        }

        $songIds = self::resolveSongIds($band, $song, $plEntries, $songList);
        foreach ($rjEntries as $e) {
            if (!is_array($e)) {
                continue;
            }
            $sid = (string) ($e['songId'] ?? '');
            if ($sid === '' || !isset($songIds[$sid])) {
                continue;
            }
            if ($episodeId === null || (int) ($e['episodeId'] ?? -1) === $episodeId) {
                return [
                    'ok' => false,
                    'message' => 'Dieses Paar wurde bereits geprüft und abgelehnt'
                        . ($episodeId !== null ? ' (Folge #' . $episodeId . ')' : '')
                        . '.',
                ];
            }
        }

        return ['ok' => true];
    }

    /**
     * @param array<string,string> $fields
     * @param list<mixed> $plEntries
     * @param list<mixed> $rjEntries
     * @param list<mixed> $songList
     * @return array{ok:bool,message?:string}
     */
    private static function checkKorrektur(array $fields, array $plEntries, array $rjEntries, array $songList): array
    {
        $needle = app_normalize($fields['eintrag'] ?? '');
        if ($needle === '') {
            return ['ok' => false, 'message' => 'Bitte den betroffenen Eintrag angeben.'];
        }

        foreach ($plEntries as $e) {
            if (!is_array($e)) {
                continue;
            }
            $b = app_normalize((string) ($e['band'] ?? ''));
            $t = app_normalize((string) ($e['songTitle'] ?? ''));
            $eid = (string) ($e['episodeId'] ?? '');
            $et = app_normalize((string) ($e['episodeTitle'] ?? ''));
            if (self::entryMatchesNeedle($needle, $b, $t, $eid, $et)) {
                return ['ok' => true];
            }
        }

        $songById = [];
        foreach ($songList as $s) {
            if (is_array($s) && !empty($s['id'])) {
                $songById[(string) $s['id']] = $s;
            }
        }
        foreach ($rjEntries as $e) {
            if (!is_array($e)) {
                continue;
            }
            $sid = (string) ($e['songId'] ?? '');
            $eid = (string) ($e['episodeId'] ?? '');
            $b = '';
            $t = '';
            if ($sid !== '' && isset($songById[$sid])) {
                $b = app_normalize((string) ($songById[$sid]['band'] ?? ''));
                $t = app_normalize((string) ($songById[$sid]['title'] ?? ''));
            }
            if (self::entryMatchesNeedle($needle, $b, $t, $eid, '')) {
                return ['ok' => true];
            }
            if ($sid !== '' && (str_contains($needle, app_normalize($sid)) || str_contains($needle, str_replace('-', ' ', app_normalize($sid))))) {
                return ['ok' => true];
            }
        }

        return [
            'ok' => false,
            'message' => 'Zum genannten Eintrag wurde in Playlist/Rejects nichts Passendes gefunden. Bitte Band, Song und/oder Folgennummer präziser angeben.',
        ];
    }

    private static function entryMatchesNeedle(string $needle, string $band, string $title, string $episodeId, string $episodeTitle): bool
    {
        if ($band !== '' && $title !== '' && str_contains($needle, $band) && str_contains($needle, $title)) {
            return true;
        }
        if ($band !== '' && str_contains($needle, $band) && $episodeId !== '' && preg_match('/\b' . preg_quote($episodeId, '/') . '\b/', $needle)) {
            return true;
        }
        if ($title !== '' && str_contains($needle, $title) && $episodeId !== '' && preg_match('/\b' . preg_quote($episodeId, '/') . '\b/', $needle)) {
            return true;
        }
        if ($episodeTitle !== '' && str_contains($needle, $episodeTitle)) {
            return true;
        }
        $blob = trim($band . ' ' . $title . ' ' . $episodeId . ' ' . $episodeTitle);
        return $blob !== '' && (str_contains($blob, $needle) || str_contains($needle, $blob));
    }

    /**
     * @param list<mixed> $plEntries
     * @param list<mixed> $songList
     * @return array<string,true>
     */
    private static function resolveSongIds(string $band, string $song, array $plEntries, array $songList): array
    {
        $ids = [];
        foreach ($plEntries as $e) {
            if (!is_array($e)) {
                continue;
            }
            if (app_normalize((string) ($e['band'] ?? '')) === $band
                && app_normalize((string) ($e['songTitle'] ?? '')) === $song
                && !empty($e['songId'])) {
                $ids[(string) $e['songId']] = true;
            }
        }
        foreach ($songList as $s) {
            if (!is_array($s)) {
                continue;
            }
            if (app_normalize((string) ($s['band'] ?? '')) === $band
                && app_normalize((string) ($s['title'] ?? '')) === $song
                && !empty($s['id'])) {
                $ids[(string) $s['id']] = true;
            }
        }
        return $ids;
    }

    private static function extractEpisodeId(string $folge): ?int
    {
        if (preg_match('/\b(\d{1,4})\b/', $folge, $m)) {
            return (int) $m[1];
        }
        return null;
    }

    /** @return array<mixed> */
    private static function fetchJson(string $url): array
    {
        $ch = curl_init($url);
        if ($ch === false) {
            throw new RuntimeException('cURL fehlt.');
        }
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_TIMEOUT => 20,
            CURLOPT_HTTPHEADER => ['User-Agent: gag-playlist-webform'],
        ]);
        $raw = curl_exec($ch);
        $status = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        if ($raw === false || $status >= 400) {
            throw new RuntimeException('JSON-Abruf fehlgeschlagen: ' . $url);
        }
        $data = json_decode($raw, true);
        if (!is_array($data)) {
            throw new RuntimeException('Ungültiges JSON: ' . $url);
        }
        return $data;
    }
}
