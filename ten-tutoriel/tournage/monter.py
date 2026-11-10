import json, subprocess, sys, os
S = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{S}/frames.json"))
idx = d["index"]
lignes = []
for i, (nom, t) in enumerate(idx):
    dur = (idx[i + 1][1] - t) if i + 1 < len(idx) else 2.0
    lignes.append(f"file 'frames/{nom}'\nduration {max(dur, 0.001):.4f}")
lignes.append(f"file 'frames/{idx[-1][0]}'")
open(f"{S}/liste.txt", "w").write("\n".join(lignes) + "\n")
sortie = sys.argv[1]
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{S}/liste.txt",
                "-vf", "fps=30,scale=1920:1080:flags=lanczos,format=yuv420p",
                "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-movflags", "+faststart", sortie], check=True, cwd=S)
t0 = idx[0][1]
for nom, t in d["marques"]:
    print(f"{t - t0:7.1f}s  {nom}")
