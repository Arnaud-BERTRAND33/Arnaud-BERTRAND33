# TEN Assistant — tutoriel vidéo

`TEN-Assistant-tutoriel.mp4` : prise en main complète (≈ 5 min 50, 1920×1080, sous-titrée, sans voix).

Chapitres : accueil et bouclier · créer un dossier · fiche dossier · déposer les pièces (Word, PDF, e-mail) ·
vérifier le masquage · poser une question / « Ce que voit l'IA » · faire rédiger un Word · brouillon d'e-mail ·
échéances · Brouillon · bibliothèque, réglages et journal.

Tournage : vraie interface et vrai moteur de masquage TEN, documents fictifs. Les réponses de l'IA sont
**scriptées** (`tournage/repondeur.py`) : elles ne reçoivent que le texte masqué, et TEN rétablit les vrais noms.

## Refaire la vidéo
Depuis le dépôt TEN-Assistant (moteur installé dans `moteur/.venv`, `npm install` dans `interface/`) :
1. `npx vite --port 5173` dans `interface/`
2. `bash tournage/relancer.sh` (backend démo sur 127.0.0.1:8765)
3. `node tournage/film.js` puis `python3 tournage/monter.py sortie.mp4`
