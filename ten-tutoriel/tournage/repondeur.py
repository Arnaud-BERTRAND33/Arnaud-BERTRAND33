"""IA scriptée pour la vidéo de démonstration.

Elle ne reçoit QUE le texte masqué (étiquettes) produit par le vrai moteur TEN,
et répond avec ces étiquettes : TEN rétablit ensuite les vraies valeurs à l'écran.
"""
import json
import re

ETIQ = re.compile(r"\[[A-Z_]+_\d+\]")


def _champ(texte, libelle):
    m = re.search(rf"^{libelle} : (.+)$", texte, re.M)
    return m.group(1).strip() if m else ""


def _message(texte):
    if "Message de l'avocat :" in texte:
        return texte.rsplit("Message de l'avocat :", 1)[1].strip()
    return texte


def _bloc(nom, contenu):
    return f"\n\n```{nom}\n{json.dumps(contenu, ensure_ascii=False)}\n```"


def repondre(texte: str) -> str:
    # --- tâches annexes de l'application -------------------------------------------------
    if texte.startswith("Tu tiens la note de synthèse"):
        e = ETIQ.findall(texte)
        cl = e[0] if e else "le client"
        return (
            "Faits : bail commercial du 18 décembre 2024 ; loyers des 3e et 4e trimestres 2025 "
            "impayés (10 800 €).\n"
            f"Procédure : commandement visant la clause résolutoire signifié le 17 septembre 2025 "
            f"à la requête de {cl}, resté sans effet ; clause acquise depuis le 17 octobre 2025.\n"
            "Prochaines étapes : assignation en référé (constat de la clause, expulsion, provision) ; "
            "mise en demeure de la caution."
        )
    if "un paragraphe par ligne" in texte and "Message de l'avocat" not in texte:
        return "# Courrier\n\nMadame, Monsieur,\n\nNous revenons vers vous dans ce dossier.\n\nCordialement."
    if "[AJOUT]" in texte or "[MODIFICATION]" in texte or "[SUPPRESSION]" in texte:
        return "Les changements portent sur le montant du loyer et la durée : vérifiez leur cohérence avec la clause d'indexation."

    msg = _message(texte)
    bas = msg.lower()

    # --- Brouillon (hors dossier) ---------------------------------------------------------
    if "Contexte du cabinet (brouillon" in texte:
        dossiers = re.findall(r"^- (.+?) — pièces", texte, re.M)
        nom = dossiers[0] if dossiers else ""
        return (
            "Un seul dossier a une échéance ce mois-ci : le contentieux locatif "
            f"{nom}, avec l'assignation en référé à délivrer avant le 27 novembre.\n\n"
            "Je vous l'ouvre pour que nous puissions avancer."
            + _bloc("actions", [{"action": "ouvrir_dossier", "dossier": nom}])
        ) if nom else "Je ne trouve pas d'échéance ce mois-ci."

    client = _champ(texte, "Client")
    adverse = _champ(texte, "Partie adverse")
    autres = [x.strip() for x in _champ(texte, "Autres personnes").split(",") if x.strip()]
    gerant = autres[0] if autres else "le gérant"
    caution = autres[1] if len(autres) > 1 else "la caution"

    # --- 3. E-mail ------------------------------------------------------------------------
    if "mail" in bas:
        corps = (f"Monsieur,\n\nJe vous informe que la clause résolutoire du bail consenti à {adverse} "
                 "est acquise depuis le 17 octobre 2025. Je vous propose d'assigner en référé avant le "
                 f"27 novembre et j'adresse en parallèle une mise en demeure à la caution, {caution}.\n\n"
                 "Je reste à votre disposition.\n\nBien cordialement")
        return (
            f"J'ai préparé un e-mail à {gerant}, gérant de {client}, pour faire le point. "
            "Il est ouvert en brouillon : rien n'est envoyé sans vous."
            + _bloc("actions", [{"action": "brouillon_email", "a": gerant,
                                 "objet": f"{client} c/ {adverse} - point d'étape", "corps": corps}])
        )

    # --- 1. Analyse ----------------------------------------------------------------------
    if "clause" in bas or "point" in bas or "où en" in bas:
        return (
            "**Où en est-on**\n"
            f"- Le bail du 18 décembre 2024 lie {client} (bailleur) à {adverse} (preneur), "
            "pour un loyer annuel de 21 600 € HT payable par trimestre (Pièce 01, art. 3).\n"
            f"- Le commandement du 17 septembre 2025 réclame 10 800 € de loyers impayés "
            "(3e et 4e trimestres 2025) et vise expressément la clause résolutoire (Pièce 02).\n"
            "- Sans paiement dans le mois, **la clause résolutoire est acquise depuis le "
            "17 octobre 2025** (article L. 145-41 du Code de commerce).\n\n"
            "**Points de vigilance**\n"
            f"- {adverse} peut demander des délais de paiement au juge, qui suspendent les effets "
            "de la clause (article L. 145-41, alinéa 2, du Code de commerce et article 1343-5 du Code civil).\n"
            f"- {caution} s'est portée caution solidaire (Pièce 01, art. 5) : elle peut être "
            "poursuivie pour la totalité de la dette.\n"
            "- Le dépôt de garantie de 5 400 € reste à imputer en fin de bail.\n\n"
            "**Suite proposée**\n"
            "1. Assigner en référé devant le président du tribunal judiciaire : constat de la "
            "clause, expulsion et provision sur les loyers.\n"
            f"2. Mettre en demeure {caution} en sa qualité de caution.\n\n"
            "Je vous ai ajouté l'échéance de l'assignation."
            + _bloc("echeances", [{
                "intitule": "Assignation en référé : constat de la clause résolutoire",
                "date": "2026-11-27", "base_legale": "art. L. 145-41 C. com. ; art. 834 CPC"}])
        )

    # --- 2. Rédaction ---------------------------------------------------------------------
    if "mise en demeure" in bas or "rédige" in bas:
        contenu = "\n".join([
            "# Mise en demeure",
            "Lettre recommandée avec accusé de réception",
            f"Madame {caution},",
            f"J'interviens en qualité de conseil de {client}, bailleur des locaux exploités par {adverse} "
            "en vertu d'un bail commercial du 18 décembre 2024.",
            f"Aux termes de l'article 5 de ce bail, vous vous êtes portée caution solidaire des engagements du preneur.",
            f"Or, malgré un commandement de payer signifié le 17 septembre 2025, {adverse} reste redevable "
            "de la somme de 10 800 euros au titre des loyers des 3e et 4e trimestres 2025.",
            "## Objet de la présente",
            "En conséquence, je vous mets en demeure de régler cette somme sous huit jours à compter de la réception de la présente.",
            "À défaut, mon client se réserve le droit d'engager à votre encontre toute procédure utile, sans autre avis.",
            "Je vous prie d'agréer, Madame, l'expression de mes salutations distinguées.",
        ])
        return (
            f"Voici la mise en demeure adressée à {caution} en sa qualité de caution solidaire. "
            "Elle rappelle le bail, le commandement resté sans effet et laisse un délai de huit jours."
            + _bloc("actions", [{"action": "creer_document",
                                 "titre": f"Mise en demeure caution - {caution}",
                                 "contenu": contenu, "format": "docx"}])
        )

    t = ETIQ.search(msg)
    return f"Voici une première analyse concernant {t.group() if t else 'votre demande'}."
