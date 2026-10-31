<?php
declare(strict_types=1);
?><!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mitmachen – GAG Metal Playlist</title>
  <link rel="stylesheet" href="assets/form.css">
</head>
<body>
  <main class="wrap">
    <header class="hero">
      <p class="brand">GAG Metal Playlist</p>
      <h1>Mitmachen</h1>
      <p class="lead">Songvorschlag, Korrektur oder anderes Feedback – ohne GitHub-Login. Nach Absenden landet ein Issue im öffentlichen Repo.<br>Alternativ mit Ihrem GitHub-Account direkt den <a href="https://github.com/sneumeister/GAG_Metal_Playlist/issues/new/choose">Issue anlegen</a>.</p>
    </header>

    <form id="mitmachen" class="form" novalidate>
      <input type="text" name="website" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">

      <label class="field">
        <span class="label">Art</span>
        <select name="type" id="type" required>
          <option value="vorschlag">Playlist: Vorschlag</option>
          <option value="korrektur">Playlist: Korrektur</option>
          <option value="sonstiges">Sonstiges</option>
        </select>
      </label>

      <div class="panel" data-type="vorschlag">
        <p class="hint">Nur Vorschläge mit erkennbarem Bezug (Person, Schlacht, Ereignis, Ort oder konkrete Sage/Figur). Lose Themenparallelen werden in der Regel abgelehnt.</p>
        <label class="field">
          <span class="label">Band <abbr title="Pflicht">*</abbr></span>
          <input name="band" type="text" maxlength="120" placeholder="z. B. Sabaton" autocomplete="off">
        </label>
        <label class="field">
          <span class="label">Songtitel <abbr title="Pflicht">*</abbr></span>
          <input name="song" type="text" maxlength="160" placeholder="z. B. The Last Stand" autocomplete="off">
        </label>
        <label class="field">
          <span class="label">GAG-Folge <abbr title="Pflicht">*</abbr></span>
          <input name="folge" type="text" maxlength="200" placeholder="z. B. 104 oder Crécy – Chronik eines Versagens" autocomplete="off">
        </label>
        <label class="field">
          <span class="label">Kurze Begründung <abbr title="Pflicht">*</abbr></span>
          <textarea name="begruendung" rows="4" maxlength="4000" placeholder="Welcher konkrete Bezug?"></textarea>
        </label>
        <label class="field">
          <span class="label">Links</span>
          <textarea name="links" rows="2" maxlength="2000" placeholder="Optional: Spotify, YouTube, Wiki …"></textarea>
        </label>
        <label class="field">
          <span class="label">Vermutete Stufe</span>
          <select name="stufe">
            <option value="Unsicher">Unsicher</option>
            <option value="A – denselben Kerngegenstand">A – denselben Kerngegenstand</option>
            <option value="B – gemeinsamer Rahmen, anderer Fokus">B – gemeinsamer Rahmen, anderer Fokus</option>
            <option value="C – thematische/assoziative Nähe">C – thematische/assoziative Nähe</option>
          </select>
        </label>
        <label class="field">
          <span class="label">Weitere Hinweise</span>
          <textarea name="sonstiges" rows="2" maxlength="2000"></textarea>
        </label>
      </div>

      <div class="panel" data-type="korrektur" hidden>
        <p class="hint">Melde einen Fehler in der bestehenden Playlist. Neue Songs gehören unter „Vorschlag“.</p>
        <label class="field">
          <span class="label">Was ist falsch? <abbr title="Pflicht">*</abbr></span>
          <select name="fehlerart">
            <option value="">Bitte wählen …</option>
            <option>Tippfehler (Band, Titel, Text)</option>
            <option>Falsche Folge zugeordnet</option>
            <option>Matching zu schwach oder falsch</option>
            <option>Stufe A/B/C anpassen oder auf Reject setzen</option>
            <option>Link kaputt oder falsch (Spotify/YouTube)</option>
            <option>Eintrag sollte entfernt werden</option>
            <option>Sonstiges</option>
          </select>
        </label>
        <label class="field">
          <span class="label">Betroffener Eintrag <abbr title="Pflicht">*</abbr></span>
          <input name="eintrag" type="text" maxlength="240" placeholder="z. B. Sabaton – The Last Stand / Folge 123" autocomplete="off">
        </label>
        <label class="field">
          <span class="label">Soll-Zustand <abbr title="Pflicht">*</abbr></span>
          <textarea name="soll" rows="3" maxlength="4000" placeholder="Was sollte stattdessen gelten?"></textarea>
        </label>
        <label class="field">
          <span class="label">Beleg oder Quelle</span>
          <textarea name="beleg" rows="2" maxlength="2000"></textarea>
        </label>
        <label class="field">
          <span class="label">Weitere Hinweise</span>
          <textarea name="sonstiges" rows="2" maxlength="2000"></textarea>
        </label>
      </div>

      <div class="panel" data-type="sonstiges" hidden>
        <p class="hint">Für neue Songs und Korrekturen bitte die speziellen Formulare. Hier alles andere.</p>
        <label class="field">
          <span class="label">Bereich <abbr title="Pflicht">*</abbr></span>
          <select name="bereich">
            <option value="">Bitte wählen …</option>
            <option>Darstellung / HTML</option>
            <option>Export (Markdown/HTML)</option>
            <option>Datenmodell / JSON</option>
            <option>Dokumentation</option>
            <option>Prozess / Mitmachen</option>
            <option>Sonstiges</option>
          </select>
        </label>
        <label class="field">
          <span class="label">Kurzbeschreibung <abbr title="Pflicht">*</abbr></span>
          <input name="kurz" type="text" maxlength="160" placeholder="Ein Satz, worum es geht" autocomplete="off">
        </label>
        <label class="field">
          <span class="label">Details <abbr title="Pflicht">*</abbr></span>
          <textarea name="details" rows="4" maxlength="4000"></textarea>
        </label>
        <label class="field">
          <span class="label">Weitere Hinweise</span>
          <textarea name="sonstiges" rows="2" maxlength="2000"></textarea>
        </label>
      </div>

      <fieldset class="confirm">
        <legend>Bestätigung</legend>
        <div class="hint">
          <p>Einmal-Code anfordern, um Missbrauch zu verhindern.</p>
          <p>Das Formular kann nur durch Eingabe des an Ihre E-Mail-Adresse versendeten Einmal-Codes versendet werden.</p>
          <p>Der Einmal-Code hat 20&nbsp;min Gültigkeit. Danach muss ein neuer Code angefordert werden.</p>
        </div>
        <label class="field">
          <span class="label">E-Mail <abbr title="Pflicht">*</abbr></span>
          <input name="email" type="email" maxlength="200" autocomplete="email" required placeholder="für den Bestätigungscode">
        </label>
        <p class="privacy">Datenschutzhinweis: Die E-Mail-Adresse wird ausschließlich zum Versenden des Einmal-Codes verwendet. Sie wird nirgends gespeichert und zu sonst nichts verwendet.</p>
        <div class="row">
          <button type="button" id="btn-code" class="btn secondary">Code anfordern</button>
          <label class="field grow">
            <span class="label">Code <abbr title="Pflicht">*</abbr></span>
            <input name="code" id="code" type="text" maxlength="8" minlength="8" autocomplete="one-time-code" spellcheck="false" placeholder="8 Zeichen" required>
          </label>
        </div>
      </fieldset>

      <p id="status" class="status" role="status" aria-live="polite" hidden></p>

      <div class="actions">
        <button type="submit" id="btn-submit" class="btn primary">Absenden</button>
        <a class="quiet" href="https://github.com/sneumeister/GAG_Metal_Playlist">Zum Repo</a>
      </div>
    </form>
  </main>
  <script src="assets/form.js" defer></script>
</body>
</html>
