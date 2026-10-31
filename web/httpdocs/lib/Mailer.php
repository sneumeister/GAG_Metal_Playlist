<?php
declare(strict_types=1);

final class MailerException extends RuntimeException
{
    /** @var string */
    public $phase;

    public function __construct(string $message, string $phase = 'smtp', ?Throwable $previous = null)
    {
        parent::__construct($message, 0, $previous);
        $this->phase = $phase;
    }
}

final class Mailer
{
    /** @param array<string,mixed> $smtp */
    public static function send(array $smtp, string $to, string $toName, string $subject, string $body): void
    {
        $host = (string) ($smtp['host'] ?? '');
        $port = (int) ($smtp['port'] ?? 465);
        $user = (string) ($smtp['user'] ?? '');
        $pass = (string) ($smtp['pass'] ?? '');
        $from = (string) ($smtp['from'] ?? $user);
        $fromName = (string) ($smtp['fromName'] ?? $from);
        $enc = (string) ($smtp['encryption'] ?? 'ssl');

        if ($host === '' || $user === '' || $pass === '' || str_starts_with($pass, 'YOUR_')) {
            throw new MailerException(
                'SMTP ist unvollständig konfiguriert (Host/User/Passwort in private/config.php prüfen).',
                'config'
            );
        }

        $remote = ($enc === 'ssl' ? 'ssl://' : '') . $host . ':' . $port;
        $errno = 0;
        $errstr = '';
        $fp = @stream_socket_client($remote, $errno, $errstr, 30, STREAM_CLIENT_CONNECT);
        if ($fp === false) {
            throw new MailerException(
                'SMTP-Server nicht erreichbar (' . $host . ':' . $port . ')'
                . ($errstr !== '' ? ': ' . $errstr : '')
                . '. Host/Port/SSL bzw. Firewall prüfen.',
                'connect'
            );
        }
        stream_set_timeout($fp, 30);

        try {
            self::expect($fp, 220, 'connect');
            self::cmd($fp, 'EHLO gag-playlist.local', 250, 'handshake');
            self::cmd($fp, 'AUTH LOGIN', 334, 'auth');
            self::cmd($fp, base64_encode($user), 334, 'auth');
            self::cmd($fp, base64_encode($pass), 235, 'auth');
            self::cmd($fp, 'MAIL FROM:<' . $from . '>', 250, 'from');
            self::cmd($fp, 'RCPT TO:<' . $to . '>', 250, 'recipient');
            self::cmd($fp, 'DATA', 354, 'data');

            $headers = [
                'Date: ' . date('r'),
                'From: ' . self::encodeAddress($fromName, $from),
                'To: ' . self::encodeAddress($toName, $to),
                'Subject: ' . self::encodeHeader($subject),
                'MIME-Version: 1.0',
                'Content-Type: text/plain; charset=UTF-8',
                'Content-Transfer-Encoding: 8bit',
            ];
            $data = implode("\r\n", $headers) . "\r\n\r\n" . self::dotStuff($body) . "\r\n.";
            fwrite($fp, $data . "\r\n");
            self::expect($fp, 250, 'data');
            self::cmd($fp, 'QUIT', 221, 'quit');
        } finally {
            fclose($fp);
        }
    }

    /** @param resource $fp */
    private static function cmd($fp, string $line, int $expectCode, string $phase): void
    {
        fwrite($fp, $line . "\r\n");
        self::expect($fp, $expectCode, $phase);
    }

    /** @param resource $fp */
    private static function expect($fp, int $code, string $phase): void
    {
        $resp = '';
        while (($line = fgets($fp, 515)) !== false) {
            $resp .= $line;
            if (isset($line[3]) && $line[3] === ' ') {
                break;
            }
        }
        $got = (int) substr($resp, 0, 3);
        if ($got !== $code) {
            throw new MailerException(self::friendly($phase, $got, trim($resp)), $phase);
        }
    }

    private static function friendly(string $phase, int $got, string $resp): string
    {
        $snip = self::safeSmtpSnippet($resp);
        return match ($phase) {
            'auth' => 'SMTP-Anmeldung fehlgeschlagen (vermutlich falsches Postfach-Passwort oder User).'
                . ($snip !== '' ? ' Server: ' . $snip : ''),
            'recipient' => 'Empfänger vom SMTP-Server abgelehnt (Adresse ungültig oder nicht zustellbar).'
                . ($snip !== '' ? ' Server: ' . $snip : ''),
            'from' => 'Absender vom SMTP-Server abgelehnt (From/User in der Config prüfen).'
                . ($snip !== '' ? ' Server: ' . $snip : ''),
            'connect' => 'SMTP-Begrüßung fehlgeschlagen.'
                . ($snip !== '' ? ' Server: ' . $snip : ''),
            'data' => 'SMTP hat die Mail-Daten nicht akzeptiert.'
                . ($snip !== '' ? ' Server: ' . $snip : ''),
            default => 'SMTP-Fehler (Phase ' . $phase . ', Code ' . $got . ').'
                . ($snip !== '' ? ' Server: ' . $snip : ''),
        };
    }

    /** SMTP-Text ohne Credential-Leaks kürzen. */
    private static function safeSmtpSnippet(string $resp): string
    {
        $resp = preg_replace('/[A-Za-z0-9+\/=]{20,}/', '[…]', $resp) ?? $resp;
        $resp = preg_replace('/\b\S+@\S+\b/', '[Adresse]', $resp) ?? $resp;
        if (strlen($resp) > 160) {
            $resp = substr($resp, 0, 157) . '…';
        }
        return $resp;
    }

    private static function encodeAddress(string $name, string $email): string
    {
        $name = trim($name);
        if ($name === '' || $name === $email) {
            return '<' . $email . '>';
        }
        return self::encodeHeader($name) . ' <' . $email . '>';
    }

    private static function encodeHeader(string $value): string
    {
        if (preg_match('/^[\x20-\x7E]+$/', $value)) {
            return $value;
        }
        return '=?UTF-8?B?' . base64_encode($value) . '?=';
    }

    private static function dotStuff(string $body): string
    {
        $body = str_replace(["\r\n", "\r"], "\n", $body);
        $body = str_replace("\n", "\r\n", $body);
        return preg_replace('/^\./m', '..', $body) ?? $body;
    }
}
