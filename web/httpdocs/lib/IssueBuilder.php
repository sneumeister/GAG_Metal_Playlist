<?php
declare(strict_types=1);

final class IssueBuilder
{
    /**
     * @param array<string,string> $fields
     * @return array{title:string,body:string,labels:list<string>}
     */
    public static function build(string $type, array $fields): array
    {
        $note = "\n\n---\nEingereicht über Webformular (E-Mail bestätigt).\n";

        return match ($type) {
            'vorschlag' => [
                'title' => self::titleVorschlag($fields),
                'body' => self::bodyVorschlag($fields) . $note,
                'labels' => ['playlist', 'vorschlag'],
            ],
            'korrektur' => [
                'title' => self::titleKorrektur($fields),
                'body' => self::bodyKorrektur($fields) . $note,
                'labels' => ['playlist', 'korrektur'],
            ],
            'sonstiges' => [
                'title' => self::titleSonstiges($fields),
                'body' => self::bodySonstiges($fields) . $note,
                'labels' => ['sonstiges'],
            ],
            default => throw new InvalidArgumentException('Unbekannter Typ.'),
        };
    }

    /** @param array<string,string> $f */
    private static function titleVorschlag(array $f): string
    {
        $band = trim($f['band'] ?? '');
        $song = trim($f['song'] ?? '');
        $folge = trim($f['folge'] ?? '');
        $ep = '';
        if (preg_match('/\b(\d{1,4})\b/', $folge, $m)) {
            $ep = ' (#' . $m[1] . ')';
        }
        return '[Vorschlag] ' . $band . ' – ' . $song . $ep;
    }

    /** @param array<string,string> $f */
    private static function bodyVorschlag(array $f): string
    {
        $stufe = trim($f['stufe'] ?? '');
        if ($stufe === '') {
            $stufe = 'Unsicher';
        }
        return self::sections([
            'Band' => $f['band'] ?? '',
            'Songtitel' => $f['song'] ?? '',
            'GAG-Folge' => $f['folge'] ?? '',
            'Kurze Begründung' => $f['begruendung'] ?? '',
            'Links' => $f['links'] ?? '_No response_',
            'Vermutete Stufe' => $stufe,
            'Weitere Hinweise' => ($f['sonstiges'] ?? '') !== '' ? $f['sonstiges'] : '_No response_',
        ]);
    }

    /** @param array<string,string> $f */
    private static function titleKorrektur(array $f): string
    {
        $eintrag = trim($f['eintrag'] ?? '');
        if (mb_strlen($eintrag) > 60) {
            $eintrag = mb_substr($eintrag, 0, 57) . '…';
        }
        return '[Korrektur] ' . ($eintrag !== '' ? $eintrag : 'Playlist-Eintrag');
    }

    /** @param array<string,string> $f */
    private static function bodyKorrektur(array $f): string
    {
        return self::sections([
            'Was ist falsch?' => $f['fehlerart'] ?? '',
            'Betroffener Eintrag' => $f['eintrag'] ?? '',
            'Soll-Zustand' => $f['soll'] ?? '',
            'Beleg oder Quelle' => ($f['beleg'] ?? '') !== '' ? $f['beleg'] : '_No response_',
            'Weitere Hinweise' => ($f['sonstiges'] ?? '') !== '' ? $f['sonstiges'] : '_No response_',
        ]);
    }

    /** @param array<string,string> $f */
    private static function titleSonstiges(array $f): string
    {
        $kurz = trim($f['kurz'] ?? '');
        if (mb_strlen($kurz) > 70) {
            $kurz = mb_substr($kurz, 0, 67) . '…';
        }
        return '[Sonstiges] ' . ($kurz !== '' ? $kurz : 'Feedback');
    }

    /** @param array<string,string> $f */
    private static function bodySonstiges(array $f): string
    {
        return self::sections([
            'Bereich' => $f['bereich'] ?? '',
            'Kurzbeschreibung' => $f['kurz'] ?? '',
            'Details' => $f['details'] ?? '',
            'Weitere Hinweise' => ($f['sonstiges'] ?? '') !== '' ? $f['sonstiges'] : '_No response_',
        ]);
    }

    /** @param array<string,string> $sections */
    private static function sections(array $sections): string
    {
        $parts = [];
        foreach ($sections as $label => $value) {
            $value = trim($value);
            if ($value === '') {
                $value = '_No response_';
            }
            $parts[] = '### ' . $label . "\n\n" . $value;
        }
        return implode("\n\n", $parts);
    }
}
