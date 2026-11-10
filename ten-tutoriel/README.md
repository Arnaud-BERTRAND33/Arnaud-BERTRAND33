# TEN Assistant — tutoriel vidéo

`TEN-Assistant-tutoriel.mp4` : prise en main complète (≈ 6 min 48, 1920×1080, sous-titrée, musique d'ambiance originale), tournée sur la version `942c5b0` de TEN-Assistant (interface v2).

Chapitres : accueil et bouclier · créer un dossier · fiche dossier · déposer les pièces (Word, PDF, e-mail) ·
vérifier le masquage · poser une question / « Ce que voit l'IA » · faire rédiger (Word, e-mail) ·
devis & honoraires, statistiques · échéances en relief · Brouillon · bibliothèque et sources officielles ·
compte (ChatGPT / Claude, Lexis Poly, apparence, journal).

Musique : composition originale générée par `tournage/musique.py` (synthèse, aucun échantillon externe, libre de droits).

Tournage : vraie interface et vrai moteur de masquage TEN, documents fictifs. Les réponses de l'IA sont
**scriptées** (`tournage/repondeur.py`) : elles ne reçoivent que le texte masqué, et TEN rétablit les vrais noms.

## Refaire la vidéo
Depuis le dépôt TEN-Assistant (moteur installé dans `moteur/.venv`, `npm install` dans `interface/`) :
1. `npx vite --port 5173` dans `interface/`
2. `bash tournage/relancer.sh` (backend démo sur 127.0.0.1:8765)
3. `node tournage/film.js` puis `python3 tournage/monter.py muet.mp4`
4. `python tournage/musique.py <durée> musique.wav` puis mixage ffmpeg (loudnorm -17 LUFS)
