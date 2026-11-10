"""Backend démo vidéo : vraie API TEN + IA scriptée (réponses rédigées à l'avance)."""
import json, os, re, sys, shutil
from pathlib import Path
import uvicorn
sys.path.insert(0, os.path.dirname(__file__))
from ten.app.api import creer_api
from ten.app.application import Application
from ten.app.config import Config
from ten.app.ia.faux import FauxFournisseur
from ten.securite.crypto import ProtecteurFactice
from repondeur import repondre
os.startfile = lambda p: None  # démo Linux : pas de messagerie à ouvrir

LOG = Path(os.environ.get("TEN_LOG", "/tmp/ten-ia.log"))

def journal(texte):
    import time; time.sleep(float(os.environ.get("TEN_DELAI", "0")))
    with LOG.open("a") as f:
        f.write("\n\n=========== ENVOI ===========\n" + texte)
    r = repondre(texte)
    with LOG.open("a") as f:
        f.write("\n----------- REPONSE -----------\n" + r)
    return r

racine = Path(os.environ["TEN_DEV_DONNEES"])
if os.environ.get("TEN_RESET"):
    shutil.rmtree(racine, ignore_errors=True)
fx = FauxFournisseur(journal)
fx.nom = 'codex'
app = Application.demarrer(Config.pour_tests(racine), fournisseur=fx,
                           protecteur=ProtecteurFactice())
app.comptes_ia = lambda: {'codex': {'disponible': True, 'connecte': True}, 'claude': {'disponible': True, 'connecte': False}, 'actif': app.reglages.fournisseur}
uvicorn.run(creer_api(app, jeton="dev", dossier_ui=None), host="127.0.0.1", port=8765, log_level="warning")
