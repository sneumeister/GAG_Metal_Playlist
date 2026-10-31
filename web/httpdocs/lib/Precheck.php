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
        // songs.json = Liste; falls Objekt mit message o.ä., leere Liste
        $songList = [];
        if (isset($songs[0]) || $songs === []) {
            $songList = $songs;
        } elseif (isset($songs['entries']) && is_array($songs['entries'])) {
            $songList = $songs['entries'];
        }

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

        $bandKey = app_match_key($band);
        $songKey = app_match_key($song);

        foreach ($plEntries as $e) {
            if (!is_array($e)) {
                continue;
            }
            $eb = app_match_key((string) ($e['band'] ?? ''));
            $et = app_match_key((string) ($e['songTitle'] ?? ''));
            if ($eb !== $bandKey || $et !== $songKey) {
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

        $songIds = self::resolveSongIds($bandKey, $songKey, $plEntries, $songList);
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
        $raw = trim((string) ($fields['eintrag'] ?? ''));
        // Folge-Hinweis darf auch im Soll-Zustand stehen
        $haystack = trim($raw . ' ' . (string) ($fields['soll'] ?? ''));
        $needle = app_match_key($haystack);
        if (app_match_key($raw) === '') {
            return ['ok' => false, 'message' => 'Bitte den betroffenen Eintrag angeben.'];
        }

        foreach ($plEntries as $e) {
            if (!is_array($e)) {
                continue;
            }
            $b = app_match_key((string) ($e['band'] ?? ''));
            $t = app_match_key((string) ($e['songTitle'] ?? ''));
            $eid = (string) ($e['episodeId'] ?? '');
            $et = app_match_key((string) ($e['episodeTitle'] ?? ''));
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

        // Katalog: Band+Titel im Freitext → Song-IDs, dann in Rejects/Playlist?
        $matchedSongIds = [];
        foreach ($songList as $s) {
            if (!is_array($s)) {
                continue;
            }
            $b = app_match_key((string) ($s['band'] ?? ''));
            $t = app_match_key((string) ($s['title'] ?? ''));
            if ($b === '' || $t === '') {
                continue;
            }
            if (str_contains($needle, $b) && str_contains($needle, $t)) {
                $matchedSongIds[(string) $s['id']] = true;
            }
        }
        foreach ($plEntries as $e) {
            if (!is_array($e)) {
                continue;
            }
            $sid = (string) ($e['songId'] ?? '');
            if ($sid !== '' && isset($matchedSongIds[$sid])) {
                return ['ok' => true];
            }
        }
        foreach ($rjEntries as $e) {
            if (!is_array($e)) {
                continue;
            }
            $sid = (string) ($e['songId'] ?? '');
            $eid = (string) ($e['episodeId'] ?? '');
            if ($sid !== '' && isset($matchedSongIds[$sid])) {
                return ['ok' => true];
            }
            $b = '';
            $t = '';
            if ($sid !== '' && isset($songById[$sid])) {
                $b = app_match_key((string) ($songById[$sid]['band'] ?? ''));
                $t = app_match_key((string) ($songById[$sid]['title'] ?? ''));
            }
            if (self::entryMatchesNeedle($needle, $b, $t, $eid, '')) {
                return ['ok' => true];
            }
            if ($sid !== '') {
                $sidKey = app_match_key(str_replace('-', ' ', $sid));
                if ($sidKey !== '' && str_contains($needle, $sidKey)) {
                    return ['ok' => true];
                }
            }
        }

        return [
            'ok' => false,
            'message' => 'Zum genannten Eintrag wurde in Playlist/Rejects nichts Passendes gefunden. Bitte Band, Song und/oder Folgennummer präziser angeben.',
        ];
    }

    private static function entryMatchesNeedle(string $needle, string $band, string $title, string $episodeId, string $episodeTitle): bool
    {
        // $needle/$band/$title bereits app_match_key
        if ($band !== '' && $title !== '' && str_contains($needle, $band) && str_contains($needle, $title)) {
            return true;
        }
        if ($band !== '' && str_contains($needle, $band) && $episodeId !== '' && preg_match('/\b' . preg_quote($episodeId, '/') . '\b/', $needle)) {
            return true;
        }
        if ($title !== '' && str_contains($needle, $title) && $episodeId !== '' && preg_match('/\b' . preg_quote($episodeId, '/') . '\b/', $needle)) {
            return true;
        }
        // Band + alle Titelwörter (kurz) im Freitext
        if ($band !== '' && $title !== '' && str_contains($needle, $band)) {
            $words = preg_split('/\s+/', $title) ?: [];
            $words = array_values(array_filter($words, static fn(string $w): bool => strlen($w) >= 3));
            if ($words !== [] && self::allWordsPresent($needle, $words)) {
                return true;
            }
        }
        if ($episodeTitle !== '' && str_contains($needle, $episodeTitle)) {
            return true;
        }
        $blob = trim($band . ' ' . $title . ' ' . $episodeId . ' ' . $episodeTitle);
        return $blob !== '' && (str_contains($blob, $needle) || str_contains($needle, $blob));
    }

    /** @param list<string> $words */
    private static function allWordsPresent(string $needle, array $words): bool
    {
        foreach ($words as $w) {
            if (!str_contains($needle, $w)) {
                return false;
            }
        }
        return true;
    }

    /**
     * @param list<mixed> $plEntries
     * @param list<mixed> $songList
     * @return array<string,true>
     */
    private static function resolveSongIds(string $bandKey, string $songKey, array $plEntries, array $songList): array
    {
        $ids = [];
        foreach ($plEntries as $e) {
            if (!is_array($e)) {
                continue;
            }
            if (app_match_key((string) ($e['band'] ?? '')) === $bandKey
                && app_match_key((string) ($e['songTitle'] ?? '')) === $songKey
                && !empty($e['songId'])) {
                $ids[(string) $e['songId']] = true;
            }
        }
        foreach ($songList as $s) {
            if (!is_array($s)) {
                continue;
            }
            if (app_match_key((string) ($s['band'] ?? '')) === $bandKey
                && app_match_key((string) ($s['title'] ?? '')) === $songKey
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
            CURLOPT_TIMEOUT => 45,
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
