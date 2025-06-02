# AnydayTool

Ein intelligentes Familien-Management-Tool für Finanzen, Organisation und mehr – mit Fokus auf aktuelle Lage und Zukunftsprognosen.

---

## Inhaltsverzeichnis

* [Über dieses Projekt](#über-dieses-projekt)
* [Funktionen](#funktionen)
    * [Finanzplanung & Übersicht](#finanzplanung--übersicht)
    * [Dashboard & Organisation](#dashboard--organisation)
    * [Datenmanagement & Prognosen](#datenmanagement--prognosen)
    * [Zusätzliche Module](#zusätzliche-module)
* [Vision & langfristige Ziele](#vision--langfristige-ziele)
* [Technologien](#technologien)
* [Installation und Nutzung](#installation-und-nutzung)
* [Beitrag leisten](#beitrag-leisten)
* [Lizenz](#lizenz)
* [Kontakt](#kontakt)

---

## Über dieses Projekt

Das AnydayTool ist eine innovative Web-App, die Familien dabei unterstützen soll, ihren Alltag effizienter zu managen. Im Gegensatz zu herkömmlichen Tools konzentriert sich das AnydayTool nicht auf die detaillierte Erfassung vergangener Ausgaben, sondern auf die **aktuelle finanzielle Situation und zukunftsorientierte Prognosen**. Es bietet eine kollaborative Plattform für Familienmitglieder und ist modular aufgebaut, um zukünftig weitere Lebensbereiche abzudecken – von Gesundheit bis hin zur Versicherungsübersicht. Das Hauptziel ist es, Familien **finanzielle, zeitliche und lokale Freiheit** zu ermöglichen.

---

## Funktionen

### Finanzplanung & Übersicht

* **Login-Funktion:** Sichere Anmeldung für jedes Familienmitglied.
* **Kollaborative Datenbanken:** Möglichkeit zur Zusammenarbeit an gemeinsamen Finanzdatenbanken, um die Familienfinanzen transparent zu verwalten.
* **Wiederkehrende Fixkosten:**
    * Eingabe von wiederkehrenden Fixkosten als Basis für die Statistik.
    * Abfrage des tatsächlich bezahlten Betrags, um Abweichungen zu erfassen und Prognosen zu verbessern.
    * Anpassung des Betrags bei Bedarf.
* **Betragseingabe mit Unsicherheit:**
    * Möglichkeit, bei jeder Betragseingabe (Einnahmen, Ausgaben) anzugeben, ob der Betrag exakt oder eine geschätzte Spanne ist.
    * Der Grad der Unsicherheit fliesst sinnvoll in die Prognosen ein und beeinflusst den Unsicherheitswert.
    * Regelmässige Abfrage des tatsächlich bezahlten/eingenommenen Betrags zur Verfeinerung zukünftiger Prognosen.
* **Fokus auf Gegenwart & Zukunft:**
    * **Kein detailliertes Tracking vergangener Ausgaben:** Konzentration auf die aktuelle und zukünftige Finanzlage.
    * **Momentane Vermögensaufnahme:** Jederzeitige Erfassung des aktuellen Gesamtvermögens (Bankkonten, Portfolios, andere Vermögenswerte).
    * **Aktuelle & Geplante variable Ausgaben:** Erfassung der variablen Ausgaben bis zum Monatsende und zukünftiger geplanter variabler Ausgaben.
    * **Ad-hoc Finanzübersicht:** Die Möglichkeit, jederzeit die momentane finanzielle Situation zu erfassen und daraus Prognosen für die Zukunft zu generieren.
* **Besondere/Bemerkenswerte Ausgaben:**
    * Gezielte Abfrage von "bemerkenswerten" Ausgaben (z.B. Sofa, Flüge, Ferien).
    * Kategorisierung und Tracking dieser speziellen Ausgaben.
    * **Automatische Schätzung variabler Ausgaben:** Normale variable Ausgaben werden durch mathematische Modelle/Methoden geschätzt, basierend auf "Vermögensveränderung", "Einkommen" und "bemerkenswerten, ausserordentlichen Ausgaben".

### Dashboard & Organisation

* **Zentrales Dashboard:** Eine übersichtliche Startseite mit allen aktuellen Aufgaben, Übersichten und relevanten Informationen.
* **Dump Sheet:**
    * Eine Funktion zum schnellen Notieren von ungeordneten Informationen.
    * Das Tool fragt später (bei Bedarf regelmässig in kleinen "Päckchen") Notiz für Notiz nach, wofür diese gedacht war.
    * Möglichkeit, die Notiz korrekt einzuordnen (z.B. zu Finanzeinnahmen, Erinnerungen, Aufgaben etc.).

### Datenmanagement & Prognosen

* **Prognosen:**
    * Gesamtvermögens-Prognose, unterteilt in Einnahmen- und Ausgabenprognosen (fix, variabel, besondere/bemerkenswerte).
    * Cashflow-Übersicht, -Statistik und -Grafik inklusive Prognose.
* **Intelligente Prognosemodelle:**
    * Einbeziehung historischer und geplanter Daten in die Prognosen, auch wenn keine exakten erwarteten Ausgaben vorliegen.
    * Plausible und sinnvolle Schätzung variabler Ausgaben und Einnahmen anhand historischer Werte.
    * Prognose der variablen Ausgaben und Einnahmen in die Zukunft, solange die geschätzten Fehlerwerte oder Unsicherheitswerte akzeptabel sind.
    * Anwendung geeigneter mathematischer Modelle, die historische und geplante zukünftige Eingaben mathematisch sinnvoll in die Prognose einbeziehen.
    * **Algorithmus-Optimierung:** Automatische Abgleichung der mathematischen Prognosen mit den Realitätsdaten.
    * **Modell-Tipps:** Das System gibt Tipps, welches mathematische Modell für den Benutzer bisher am besten funktioniert hat.

### Zusätzliche Module

* **Modulare Anwendungen:** Die Startseite bietet verschiedene Anwendungen, die alle Aspekte des täglichen Familienlebens organisieren.
* **Ein-/Ausblendbare Module:** Anwendungen wie die Finanz-App, Gesundheitsübersicht, Versicherungsübersicht, Tagebuch etc. können je nach Bedarf ein- und ausgeblendet werden.
* **Wochen-, Monats- und Jahresübersichten:**
    * Automatisierte Erstellung von Rückblenden und Zukunftsaussichten.
    * Diese Übersichten können automatisch mit einer KI aus allen eingegebenen Daten generiert werden.
    * Zusammenfassung aller wichtigen Daten für einen schnellen Überblick.

---

## Vision & langfristige Ziele

Das AnydayTool ist der erste Schritt auf dem Weg zur **vollständigen finanziellen, zeitlichen und lokalen Freiheit** für meine Familie. Beginnend mit der Finanzplanung, soll es zu einem umfassenden Management-Tool ausgebaut werden, das verschiedene Lebensbereiche abdeckt und eine intelligente, vorausschauende Unterstützung bietet.

---

## Technologien

Das Projekt wird voraussichtlich die folgenden Technologien verwenden:

* **Frontend (Webseite):** HTML, CSS, JavaScript (mit einem modernen Framework wie **React** oder **Vue.js** für eine dynamische und interaktive Benutzeroberfläche).
* **Backend:** **Python** mit einem robusten Web-Framework (z.B. **Flask** oder **Django** für komplexere Anforderungen).
* **Datenbank:** **PostgreSQL** oder **SQLite** (für die Entwicklung, später PostgreSQL für Skalierbarkeit und komplexe Datenstrukturen).
* **Mathematische Modellierung:** Python-Bibliotheken wie **NumPy**, **Pandas**, **SciPy** und **scikit-learn** für die Prognosemodelle und den Abgleich mit Realitätsdaten.
* **Künstliche Intelligenz (KI):** Für die automatische Generierung von Übersichten und Modell-Empfehlungen.
* **Versionskontrolle:** **Git** und **GitHub** für ein sauberes Versionsmanagement und zur Vermeidung von Datenverlust.
* **Deployment:** **PythonAnywhere** als kostengünstige und effektive Hosting-Lösung.

---

## Installation und Nutzung

Detaillierte Anweisungen zur Installation und lokalen Nutzung werden hier nach Projektfortschritt bereitgestellt. Ziel ist die Veröffentlichung auf PythonAnywhere.

### Lokale Entwicklungsumgebung einrichten
*Voraussetzungen:* **Python**, **VS Code** und **Git** sind auf deinem System installiert.

1.  **Projektordner erstellen:**
    * Öffne deinen Dateimanager (Explorer unter Windows, Finder unter macOS).
    * Erstelle einen neuen Ordner an einem beliebigen Ort, z.B. `C:\Projekte\AnydayTool` (Windows) oder `/Users/DeinName/Projekte/AnydayTool` (macOS).
2.  **Projekt in VS Code öffnen:**
    * Öffne **Visual Studio Code**.
    * Klicke auf **"File" (Datei)** -> **"Open Folder..." (Ordner öffnen...)**
    * Navigiere zu dem soeben erstellten `AnydayTool`-Ordner und klicke auf **"Select Folder" (Ordner auswählen)**.
3.  **Terminal in VS Code öffnen:**
    * In VS Code: Klicke auf **"Terminal"** in der oberen Menüleiste -> **"New Terminal" (Neues Terminal)**. Ein Terminal-Fenster öffnet sich unten in VS Code und ist bereits im `AnydayTool`-Ordner.
4.  **Virtuelle Umgebung erstellen:**
    * Im VS Code Terminal, gib ein und drücke Enter:
        ```bash
        python -m venv venv
        ```
    * *(Warte, bis der Vorgang abgeschlossen ist. Ein neuer Ordner namens `venv` erscheint in deinem Projektordner.)*
5.  **Virtuelle Umgebung aktivieren:**
    * **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    * **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    * *(Du siehst `(venv)` vor deinem Prompt, was anzeigt, dass die virtuelle Umgebung aktiv ist.)*
6.  **Flask installieren (erste Abhängigkeit):**
    * Stelle sicher, dass `(venv)` im Terminal-Prompt steht.
    * Gib ein und drücke Enter:
        ```bash
        pip install Flask
        ```

### Erste Flask-Anwendung erstellen (Minimalbeispiel)

1.  **`app.py` erstellen:**
    * Klicke im VS Code auf das **"New File" (Neue Datei)** Symbol im Explorer-Bereich (linker Seitenleiste) neben deinem `AnydayTool`-Ordner.
    * Gib den Namen `app.py` ein und drücke Enter.
2.  **Code einfügen:**
    * Kopiere den folgenden Code in die `app.py`-Datei:
        ```python
        # app.py
        from flask import Flask, render_template, request, redirect, url_for, session
        import os

        app = Flask(__name__)
        # Für Sessions ist ein geheimer Schlüssel notwendig
        # In einer Produktionsumgebung sollte dies eine feste, sichere Zeichenkette sein
        app.secret_key = os.urandom(24) 

        # Eine einfache Startseite für das Dashboard
        @app.route('/')
        def index():
            return render_template('dashboard.html')

        if __name__ == '__main__':
            app.run(debug=True)
        ```
3.  **`templates` Ordner erstellen:**
    * Klicke im VS Code Explorer auf das **"New Folder" (Neuer Ordner)** Symbol im Explorer-Bereich neben deinem `AnydayTool`-Ordner.
    * Gib den Namen `templates` ein und drücke Enter.
4.  **`dashboard.html` erstellen:**
    * Klicke im VS Code Explorer mit der rechten Maustaste auf den neu erstellten `templates`-Ordner.
    * Wähle **"New File" (Neue Datei)**.
    * Gib den Namen `dashboard.html` ein und drücke Enter.
5.  **HTML-Code einfügen:**
    * Kopiere den folgenden HTML-Code in die `dashboard.html`-Datei:
        ```html
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AnydayTool - Dashboard</title>
            <style>
                body { font-family: sans-serif; text-align: center; margin-top: 50px; background-color: #f4f7f6; color: #333; }
                h1 { color: #2c3e50; }
                p { font-size: 1.1em; }
                .container { max-width: 800px; margin: 0 auto; padding: 20px; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Willkommen bei deinem AnydayTool Dashboard, Renato!</h1>
                <p>Hier starten wir mit deiner Finanzplanung.</p>
                <p>Diese Seite wird zukünftig alle wichtigen Funktionen für dein Familien-Management bündeln.</p>
            </div>
        </body>
        </html>
        ```
6.  **Flask-Anwendung starten:**
    * Gehe zurück zum VS Code Terminal (stelle sicher, dass die virtuelle Umgebung aktiv ist).
    * Gib ein und drücke Enter:
        ```bash
        python app.py
        ```
    * Du solltest eine Ausgabe sehen, die `* Running on http://127.0.0.1:5000` enthält.
7.  **Webseite im Browser öffnen:**
    * Öffne deinen Webbrowser.
    * Gib in die Adressleiste ein: `http://127.0.0.1:5000` und drücke Enter.
    * Du solltest die Überschrift "Willkommen bei deinem AnydayTool Dashboard, Renato!" sehen.

### Versionskontrolle mit Git und GitHub einrichten

1.  **Git-Repository initialisieren:**
    * Gehe im VS Code Terminal in deinen `AnydayTool`-Ordner.
    * Gib ein und drücke Enter:
        ```bash
        git init
        ```
2.  **`README.md` hinzufügen:**
    * Klicke im VS Code Explorer auf das **"New File" (Neue Datei)** Symbol im Explorer-Bereich neben deinem `AnydayTool`-Ordner.
    * Gib den Namen `README.md` ein und drücke Enter.
    * Füge diesen Markdown-Code, den ich dir gerade gebe, in diese Datei ein und speichere sie.
3.  **`.gitignore` erstellen:**
    * Klicke im VS Code Explorer auf das **"New File" (Neue Datei)** Symbol.
    * Gib den Namen `.gitignore` ein und drücke Enter.
    * Füge die folgenden Zeilen in die `.gitignore`-Datei ein und speichere sie:
        ```
        venv/
        __pycache__/
        *.pyc
        .env
        ```
4.  **Dateien zu Git hinzufügen und ersten Commit machen:**
    * Im VS Code Terminal:
        ```bash
        git add .
        ```
        ```bash
        git commit -m "Initial commit: Setup basic Flask app for AnydayTool and README"
        ```
5.  **GitHub-Repository erstellen:**
    * Gehe zu [https://github.com/](https://github.com/) und logge dich ein.
    * Klicke auf das **"+"** Zeichen oben rechts und wähle **"New repository" (Neues Repository)**.
    * **Repository name:** Gib `AnydayTool` ein.
    * **Description (optional):** Gib eine kurze Beschreibung ein, z.B. "Ein intelligentes Familien-Management-Tool".
    * Wähle **"Public" (Öffentlich)**.
    * **WICHTIG:** Kreuze **NICHT** "Add a README file", "Add .gitignore", oder "Choose a license" an, da wir diese bereits lokal erstellt haben.
    * Klicke auf **"Create repository" (Repository erstellen)**.
6.  **Lokales Repository mit GitHub verbinden und pushen:**
    * Kopiere die beiden Zeilen, die dir GitHub vorschlägt, im Stil von:
        ```bash
        git remote add origin [https://github.com/DeinGitHubName/AnydayTool.git](https://github.com/DeinGitHubName/AnydayTool.git)
        git branch -M main
        git push -u origin main
        ```
        *(Ersetze `DeinGitHubName` durch deinen tatsächlichen GitHub-Benutzernamen.)*
    * Füge diese Befehle in dein **VS Code Terminal** ein und drücke nach jeder Zeile Enter.
    * Möglicherweise wirst du aufgefordert, deine GitHub-Anmeldeinformationen einzugeben.

---

## Beitrag leisten

Vorschläge und Verbesserungen sind willkommen! Bitte eröffne ein Issue oder sende einen Pull Request.

**Wichtiger Hinweis:** Dieses Repository ist öffentlich. Änderungen dürfen vorgeschlagen werden, aber der Code darf ohne meine Zustimmung ausserhalb der Weiterentwicklung nicht veröffentlicht oder kommerziell genutzt werden. Für die Weiterentwicklung darf der Code jedoch verwendet werden.

---

## Lizenz

Dieses Projekt steht unter der [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/). Dies bedeutet, dass der Code für die Weiterentwicklung verwendet werden darf, aber eine kommerzielle Nutzung oder Veröffentlichung ohne explizite Zustimmung nicht gestattet ist.

---

## Kontakt



Momentaner Startprompt zur Überprüfung inklusive neuer Ideen:

Dashboard-Optimierung: 
 Ich schreibe hier nochmals meinen ursprünglichen Prompt, damit du überprüfen kannst, ob alles so umgesetzt wurde: 

 Ich möchte eine neue Web-App kreieren für mich und meine Familie mit verschiedenen Funktionen fürs Familien-Management. Ich möchte starten mit einer Finanzplanung- und Übersichts-Anwendung.  
  Es soll keine klassische Budget-Aufstellung sein, sondern hauptsächlich folgende Informationen erfragen und darstellen:  
  - login-Funktion für jedes Familienmitglied und Möglichkeit der Zusammenarbeit an gemeinsamen Datenbanken  

  - ich möchte wiederkehrende Fixkosten eingeben können, mit der die Statistik meiner App arbeitet, aber ich möchte dann jeweils gefragt werden, ob der effektiv bezahlte Betrag auch wirklich der geplante Betrag war und gegebenfalls möchte ich den Betrag dann auch anpassen können.
- Ich möchte bei jeder Betragseingabe auch eingeben können, ob der Betrag der Eingabe exakt ist oder eine geschätzte Betragsspanne ist. Je nachdem wie gross die Unsicherheitsspanne ist, soll dieses Ergebnis sinnvoll in die Prognose einfliessen. So wird wahrscheinlich der Unsicherheitswert beeinflusst. So oder so möchte ich immer gefragt werden, wie hoch der Wert wirklich war, um die Zukunftsprognose zu verbessern.
  - Ein Dashboard wäre super mit allen aktuellen Aufgaben oder Übersichten.
  - Ich möchte keine vergangenen Ausgaben eintragen. Ich möchte den Fokus auf die momentane und zukünftige finanzielle Situation lenken. Ich möchte also jederzeit eingeben können, wie viel das Vermögen momentan ist: jedes Bankkonto und Portfolios und andere Vermögenswerte werden abgefragt. Auch sollen die aktuellen variablen Ausgaben bis zum Monatsende abgefragt werden und die zukünftigen, schon geplanten variablen Ausgaben erfragt werden. Mein Traum ist es, jederzeit, wann immer ich möchte, also nicht nur am Monatsende die momentane finanzielle Situation zu erfassen und daraus Prognosen für die Zukunft machen zu können mit passenden mathematischen Modellen. 

- Die Prognosen ist die Gesamtvermögens-Prognose und diese in die Teilbereiche unterteilt: Einnahmen und Ausgabenprognose, jeweils fix, variabel und besondere/bemerkenswerte

- Ich möchte zusätzlich eine Cashflow-Übersicht, Statistik, Grafik inklusive Prognose.

Ich möchte kein detailliertes Ausgaben-Kategorie-Tracking. Ich möchte nur die Frage nach "bemerkenswerten" Ausgaben. Z.B. wenn ein Sofa oder Flüge/Ferien gebucht werden. nach diesen iese "speziellen" Ausgaben möchte ich gefragt werden, damit diese Kategorisiert und getrackt werden können. Dabei ist mein Ziel, dass die App meine "normalen, variablen" Ausgaben schätzt, indem die normalen variablen Ausgaben durch die Variablen "Vermögensveränderung", "Einkommen" und "bemerkenswerte, ausserordentliche Ausgaben" mit geeigneten Mathematischen Modellen/Methoden berechnet/geschätzt werden. 



 Ich möchte meine Webseite über pythonanywhere veröffentlichen (hauptsache kostenlos), ausser du hast bessere Varianten. 

 Ich möchte, dass du sowohl die historischen Daten als auch die geplanten Daten der Datenbank mit in die Prognose mit einbeziehst, wenn keine exakten, erwarteten Ausgaben vorliegen. Z.B. die variablen Ausgaben und Einnahmen sollen anhand der historischen Werten plausibel und sinnvoll errechnet und geschätzt werden und so weit in die Zukunft aufgeteilt nach den Kategorien prognostiziert werden, dass es noch Sinn macht und die geschätzten Fehlerwerte oder Unsicherheitswerte noch akzeptabel sind. Die Schätzungen sollen anhand geeigneter mathematischen Modellen geschehen, welche die historischen und geplanten zukünftigen Eingaben mitberücksichtigen und mathematisch sinnvoll in die Prognose einbeziehen.

Weitere Ideen:

• Neuer Name: AnydayTool
• Idee: Die mathematischen Prognosen mit den Realitätsdaten durch den Algorithmus automatisch abgleichen lassen und so Tipps geben lassen, welches mathematisches Modell für mich am besten funktioniert hat bis jetzt.
• Dump Sheet zum schnellen Niederschreiben von Infos. Das Tool fragt dann später nach (wenn nötig regelmässig in kleinen Päckchen) Notiz für Notiz nach, wofür dies gedacht war und ich kann dann die Notiz korrekt einordnen (also z.B. zu den Finanzeinnahmen oder zu den Erinnerungen etc.)
• Die Startseite bietet verschiedene Anwendungen an, die alles bieten, was fürs tägliche Leben sinnvoll ist zum Organisieren. Z.B. die Finanz-App, die sich mit anderen Nutzern verbinden lässt, dann die Gesundheits-Übersicht, eine Versicherungs-Übersicht, ein Tagebuch, etc. Die Anwendungen lassen sich einblenden und bei Nichtgebrauch auch ausblenden.
• Es gibt die Möglichkeit, eine Wochen-, Monats und Jahresübersicht zu machen, die eine Rückblende und eine Zukunftsaussicht macht. Diese Übersicht kann automatisch mit einer AI mit allen eingegebenen Daten generiert werden. Damit werden alle wichtigen Daten zusammengefasst und in einem schnellen Überblick dargestellt.
