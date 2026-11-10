# Vidéo publicitaire TEN France Bordeaux

- `TEN-France-Bordeaux-pub.mp4` : vidéo finale (86 s, 1920x1080, 25 i/s, musique originale synthétisée).
- `source/film.html` : animation (HTML/CSS + three.js), pilotée image par image via `window.seek(t)`.
- `source/music.py` : génération de la musique (`python3 music.py 86 music.wav`).
- `source/render.js` : rendu Playwright des images (`node render.js frames <début> <fin> 25`, avec `film.html` servi en HTTP local sur le port 8765).

Assemblage : `ffmpeg -framerate 25 -i frames/%05d.jpg -i music.wav -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -shortest out.mp4`
