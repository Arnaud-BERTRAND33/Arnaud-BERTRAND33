# Vidéo publicitaire TEN France Bordeaux

- `TEN-France-Bordeaux-pub.mp4` : vidéo finale (86 s, 1920x1080, 25 i/s, musique originale synthétisée).
- `source/film.html` : animation (HTML/CSS + three.js), pilotée image par image via `window.seek(t)`.
- `source/music.py` : génération de la musique (`python3 music.py 86 music.wav`).
- `source/render.js` : rendu Playwright des images (`node render.js frames <début> <fin> 25`, avec `film.html` servi en HTTP local sur le port 8765).

Assemblage : `ffmpeg -framerate 25 -i frames/%05d.jpg -i music.wav -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -shortest out.mp4`

## Version 30 s verticale (style « ville 3D »)

- `TEN-France-Bordeaux-30s-vertical.mp4` : 1080x1920, 30 i/s, 30 s.
- `source-30s/film.html` : scène three.js (ville, chemins lumineux, effet de lueur) + textes ; utilise les fichiers de `source/assets` (copier `assets/` à côté, avec `assets/jsm` issu du paquet npm `three@0.160.0`, dossier `examples/jsm`).
- `source-30s/music30.py` : musique (`python3 music30.py music30.wav`).
- `source-30s/render_v.js` : rendu (`node render_v.js frames 0 900 30`, page servie sur le port 8766).
