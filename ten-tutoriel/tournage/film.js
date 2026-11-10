// Tournage du tutoriel TEN Assistant : pilote la vraie interface + capture CDP haute qualité.
const { chromium } = require('playwright')
const fs = require('fs')
const path = require('path')

const S = __dirname
const FRAMES = path.join(S, 'frames')
const PIECES = path.join(S, 'pieces')
const URL = 'http://127.0.0.1:5173/?backend=1'
const W = 1600, H = 900, DSF = 1.2

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

// ---------- calques injectés : curseur, sous-titres, cartes de chapitre ----------
const CALQUES = `
(() => { const init = () => {
  if (window.__film) return; window.__film = true;
  const st = document.createElement('style');
  st.textContent = \`
  #f-cur{position:fixed;left:0;top:0;width:26px;height:26px;z-index:2147483647;pointer-events:none;transform:translate(-3px,-2px);transition:transform .08s;filter:drop-shadow(0 2px 3px rgba(0,0,0,.35))}
  #f-cur.down{transform:translate(-3px,-2px) scale(.85)}
  .f-rip{position:fixed;width:16px;height:16px;margin:-8px 0 0 -8px;border-radius:50%;border:3px solid #ffa400;z-index:2147483646;pointer-events:none;animation:frip .55s ease-out forwards}
  @keyframes frip{to{transform:scale(3.4);opacity:0}}
  #f-cap{position:fixed;left:50%;bottom:34px;transform:translate(-50%,20px);max-width:1080px;z-index:2147483645;pointer-events:none;
    background:rgba(9,27,58,.93);color:#fff;border-radius:16px;padding:16px 26px 17px;font:500 20px/1.42 Inter,system-ui,sans-serif;
    box-shadow:0 18px 50px rgba(5,20,45,.35);opacity:0;transition:opacity .35s, transform .35s;border:1px solid rgba(255,255,255,.12)}
  #f-cap.on{opacity:1;transform:translate(-50%,0)}
  #f-cap.haut{bottom:auto;top:26px}
  #f-cap b{color:#ffb933;font-weight:600}
  #f-cap .k{display:block;font:600 12.5px/1 Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#ffb933;margin-bottom:8px}
  #f-card{position:fixed;inset:0;z-index:2147483640;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;
    background:radial-gradient(1200px 700px at 30% 20%,#1d5fae 0%,#0b2a5b 55%,#071b3d 100%);color:#fff;opacity:0;transition:opacity .45s;pointer-events:none}
  #f-card.on{opacity:1}
  #f-card .n{font:600 15px/1 Inter,sans-serif;letter-spacing:.25em;color:#ffb933;text-transform:uppercase}
  #f-card h1{font:600 64px/1.08 Fraunces,Georgia,serif;margin:0;text-align:center}
  #f-card h1 i{color:#ffb933}
  #f-card p{font:400 23px/1.5 Inter,sans-serif;color:#c8d8f0;margin:0;max-width:900px;text-align:center}
  #f-card img{width:96px;height:96px;border-radius:22px;background:#fff;padding:8px;margin-bottom:10px}
  .f-spot{position:fixed;z-index:2147483644;pointer-events:none;border-radius:14px;box-shadow:0 0 0 4px #ffa400,0 0 0 9999px rgba(7,20,45,.35);transition:all .3s;opacity:0}
  .f-spot.on{opacity:1}
  \`;
  document.documentElement.appendChild(st);
  const cur = document.createElement('div'); cur.id = 'f-cur';
  cur.innerHTML = '<svg viewBox="0 0 24 24" width="26" height="26"><path d="M3 2l7.5 19 2.6-7.6L21 10.8z" fill="#111" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>';
  const cap = document.createElement('div'); cap.id = 'f-cap';
  const card = document.createElement('div'); card.id = 'f-card';
  const spot = document.createElement('div'); spot.className = 'f-spot';
  const add = () => { for (const e of [card, spot, cap, cur]) if (!e.isConnected) document.body.appendChild(e) };
  if (document.body) add(); else document.addEventListener('DOMContentLoaded', add);
  setInterval(add, 500);
  let cx = -50, cy = -50;
  document.addEventListener('mousemove', (e) => { cx = e.clientX; cy = e.clientY; cur.style.left = cx + 'px'; cur.style.top = cy + 'px' }, true);
  document.addEventListener('mousedown', (e) => { cur.classList.add('down'); const r = document.createElement('div'); r.className = 'f-rip'; r.style.left = e.clientX + 'px'; r.style.top = e.clientY + 'px'; document.body.appendChild(r); setTimeout(() => r.remove(), 700) }, true);
  document.addEventListener('mouseup', () => cur.classList.remove('down'), true);
  window.__cap = (html, pos) => { cap.className = pos || ''; cap.innerHTML = html; requestAnimationFrame(() => cap.classList.add('on')) };
  window.__capOff = () => cap.classList.remove('on');
  window.__card = (html) => { card.innerHTML = html; card.classList.add('on') };
  window.__cardOff = () => card.classList.remove('on');
  window.__spot = (sel, pad) => { const el = typeof sel === 'string' ? document.querySelector(sel) : sel; if (!el) return; const b = el.getBoundingClientRect(); pad = pad ?? 8;
    Object.assign(spot.style, { left: (b.left - pad) + 'px', top: (b.top - pad) + 'px', width: (b.width + 2 * pad) + 'px', height: (b.height + 2 * pad) + 'px' }); spot.classList.add('on') };
  window.__spotOff = () => spot.classList.remove('on');
}; if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init(); })();
`

async function main() {
  fs.rmSync(FRAMES, { recursive: true, force: true })
  fs.mkdirSync(FRAMES, { recursive: true })
  const browser = await chromium.launch()
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: DSF, locale: 'fr-FR', timezoneId: 'Europe/Paris' })
  await ctx.addInitScript(CALQUES)
  const page = await ctx.newPage()
  page.on('pageerror', (e) => console.log('PAGEERR', e.message))

  // --- capture CDP ---
  const cdp = await ctx.newCDPSession(page)
  const index = []
  let n = 0
  cdp.on('Page.screencastFrame', async (f) => {
    const nom = String(n++).padStart(6, '0') + '.jpg'
    fs.writeFileSync(path.join(FRAMES, nom), Buffer.from(f.data, 'base64'))
    index.push([nom, f.metadata.timestamp])
    cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }).catch(() => {})
  })
  const marques = []
  const t0 = Date.now() / 1000
  const marque = (nom) => marques.push([nom, Date.now() / 1000])

  // --- outils de mise en scène ---
  let mx = W / 2, my = H / 2
  const bouger = async (x, y, ms = 650) => {
    const pas = Math.max(8, Math.round(ms / 16))
    const x0 = mx, y0 = my
    for (let i = 1; i <= pas; i++) {
      const t = i / pas, e = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2
      await page.mouse.move(x0 + (x - x0) * e, y0 + (y - y0) * e)
      await sleep(ms / pas)
    }
    mx = x; my = y
  }
  const vers = async (loc, ms, dx = 0, dy = 0) => {
    await loc.scrollIntoViewIfNeeded()
    const b = await loc.boundingBox()
    if (!b) throw new Error('introuvable : ' + loc)
    await bouger(b.x + b.width / 2 + dx, b.y + b.height / 2 + dy, ms)
    return b
  }
  const cliquer = async (loc, { ms = 650, apres = 500 } = {}) => {
    await vers(loc, ms)
    await sleep(180)
    await page.mouse.down(); await sleep(90); await page.mouse.up()
    await sleep(apres)
  }
  const taper = async (loc, texte, delai = 32) => {
    await cliquer(loc, { apres: 200 })
    for (const c of texte) {
      if (c === '\n') await page.keyboard.press('Shift+Enter')
      else await page.keyboard.type(c)
      await sleep(delai + Math.random() * 25)
    }
  }
  const cap = async (html, ms = 3500, pos) => { await page.evaluate(([h, p]) => window.__cap(h, p), [html, pos]); await sleep(ms) }
  const capOff = async (ms = 350) => { await page.evaluate(() => window.__capOff()); await sleep(ms) }
  const spot = async (sel, pad) => { await page.evaluate(([s, p]) => window.__spot(s, p), [sel, pad]) }
  const spotLoc = async (loc, pad) => { const h = await loc.elementHandle(); await page.evaluate(([e, p]) => window.__spot(e, p), [h, pad]) }
  const spotOff = async () => page.evaluate(() => window.__spotOff())
  const chapitre = async (num, titre, sous, ms = 2600) => {
    marque('chapitre ' + num + ' ' + titre)
    await capOff(0)
    await page.evaluate(([a, b, c]) => window.__card(`<div class="n">Étape ${a}</div><h1>${b}</h1><p>${c}</p>`), [num, titre, sous])
    await sleep(ms)
  }
  const finChapitre = async () => { await page.evaluate(() => window.__cardOff()); await sleep(600) }
  const menu = (txt) => page.locator('.side .nav a').filter({ hasText: new RegExp('^' + txt) }).first()

  const onglet = (re) => page.getByRole('tab').filter({ hasText: re }).first()
  const envoyer = async (texte, attente, delai = 26) => {
    await taper(page.getByLabel('Votre demande'), texte, delai)
    await sleep(350)
    await cliquer(page.getByRole('button', { name: 'Envoyer' }), { apres: 400 })
    if (attente) await page.locator(attente).last().waitFor({ timeout: 60000 })
  }

  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: W * DSF, maxHeight: H * DSF, everyNthFrame: 1 })

  // ================= INTRO =================
  await page.goto(URL)
  await page.evaluate(() => window.__card(`<img src="/src/logo.webp"><h1>Bienvenue dans <i>TEN Assistant</i></h1><p>L'intelligence artificielle sur vos dossiers, sans jamais transmettre les données de vos clients.</p>`))
  await sleep(4200)
  await finChapitre()
  await sleep(4000)
  await page.waitForSelector('text=Que puis-je faire', { timeout: 30000 })
  await sleep(800)
  await bouger(700, 300, 900)

  // ================= ACCUEIL =================
  marque('accueil')
  await cap(`<span class="k">L'accueil</span>Votre journée en un coup d'œil : demande rapide, dossiers, échéances, et le compteur des <b>données protégées</b>.`, 4600)
  await vers(page.locator('.side').getByText('Bouclier actif').first(), 900)
  await spotLoc(page.locator('.side').getByText('Bouclier actif').first().locator('xpath=..'), 10)
  await cap(`<span class="k">Le bouclier</span><b>Vert</b> : la protection est active. Avant chaque envoi, noms, adresses et numéros sont remplacés par des étiquettes. <b>Aucune donnée réelle ne quitte ce PC.</b>`, 6000)
  await spotOff(); await capOff()

  // ================= 1. CRÉER UN DOSSIER =================
  await chapitre(1, 'Créer un dossier', 'Un dossier par affaire : sa fiche, ses pièces, ses conversations, ses honoraires.')
  await finChapitre()
  await cliquer(menu('Dossiers'), { apres: 900 })
  await cliquer(page.getByRole('button', { name: /Nouveau dossier/ }), { apres: 700 })
  await taper(page.getByLabel('Nom du dossier'), 'SCI Berthelot Immobilier c/ Boulangerie Soulier', 36)
  await sleep(400)
  await cliquer(page.getByRole('button', { name: 'Créer', exact: true }), { apres: 1300 })
  await cap(`Le dossier est créé. Ouvrons-le.`, 1600)
  await cliquer(page.locator('.dcard').filter({ hasText: 'Boulangerie Soulier' }).first(), { apres: 1500 })
  await capOff()

  // ================= 2. FICHE =================
  await chapitre(2, 'Remplir la fiche dossier', 'Le réglage le plus important pour la confidentialité.')
  await finChapitre()
  await cliquer(onglet(/^Fiche dossier/), { apres: 1000 })
  await cap(`<span class="k">La fiche dossier</span>Tout ce que vous saisissez ici est masqué <b>de façon certaine</b>, sous toutes ses formes : majuscules, « M. Soulier », « A. Soulier »…`, 5000, 'haut')
  const champ = (lib) => page.locator('label.f').filter({ has: page.locator('span', { hasText: new RegExp('^' + lib) }) }).locator('input, textarea, select').first()
  await taper(champ('Client'), 'SCI Berthelot Immobilier')
  await taper(champ('Adversaire'), 'Boulangerie Soulier')
  const type = champ('Type de dossier')
  if (await type.count()) { await vers(type, 600); await type.selectOption('Immobilier'); await sleep(500) }
  await taper(champ('Juridiction'), 'Tribunal judiciaire de Toulouse', 22)
  await taper(champ('Avocat en charge'), 'Maître Claire Delmas', 28)
  await taper(champ('Autres personnes'), 'Gilles Montferrand\nAmandine Soulier', 30)
  await taper(champ('Sociétés'), 'SCI Berthelot Immobilier\nBoulangerie Soulier', 22)
  await capOff()
  const cats = page.getByText('Catégories masquées').first()
  await vers(cats, 700)
  await spotLoc(cats.locator('xpath=..'), 6)
  await cap(`Choisissez les catégories à masquer. Montants et dates restent visibles : l'IA en a besoin pour raisonner.`, 4600, 'haut')
  await spotOff(); await capOff()
  await cliquer(page.getByRole('button', { name: 'Enregistrer la fiche' }), { apres: 1500 })

  // ================= 3. PIÈCES =================
  await chapitre(3, 'Déposer les pièces', 'Word, Excel, PDF, PDF scannés, photos, e-mails Outlook…')
  await finChapitre()
  await cliquer(onglet(/^Pièces/), { apres: 900 })
  const [chooser] = await Promise.all([
    page.waitForEvent('filechooser'),
    cliquer(page.getByRole('button', { name: /Ajouter des pièces/ }), { apres: 100 }),
  ])
  await cap(`Ajoutez vos pièces : ici un <b>bail en Word</b>, un <b>commandement de payer en PDF</b> et un <b>e-mail du client</b>.`, 1500, 'haut')
  await chooser.setFiles([
    path.join(PIECES, 'Bail commercial - Boulangerie Soulier.docx'),
    path.join(PIECES, 'Commandement de payer 17-09-2025.pdf'),
    path.join(PIECES, 'Mail du client - loyers.eml'),
  ])
  await page.locator('.prow').filter({ hasText: 'Mail du client' }).waitFor({ timeout: 60000 })
  await sleep(2000)
  await cap(`Chaque pièce est lue <b>sur votre ordinateur</b>, chiffrée, puis masquée automatiquement. Rien n'est encore parti.`, 4300, 'haut')
  await capOff()

  // ================= 4. VÉRIFICATION =================
  await chapitre(4, 'Vérifier le masquage', "Vous gardez toujours la main sur ce qui part vers l'IA.")
  await finChapitre()
  const ligne = (nom) => page.locator('.prow').filter({ hasText: nom }).first()
  await cliquer(ligne('Bail commercial').getByRole('button', { name: 'Aperçu' }), { apres: 2500 })
  await cap(`Les éléments masqués sont surlignés, <b>une couleur par catégorie</b> : personnes, sociétés, adresses, identifiants.`, 4600, 'haut')
  const ent = (txt) => page.locator('.ent').filter({ hasText: txt }).first()
  await vers(ent('Gilles MONTFERRAND'), 900)
  await cap(`Survolez un élément : vous voyez l'étiquette qui le remplace. L'IA ne lira que <b>[PERSONNE_2]</b>.`, 4400, 'haut')
  await vers(ent('850 112 236'), 700); await sleep(1400)
  await vers(ent('FR76'), 900); await sleep(1600)
  await capOff()
  await cliquer(ent('RCS de Toulouse'), { apres: 900 })
  await cap(`<b>Un clic</b> sur un élément pour qu'il ne soit pas masqué, ou pour le reclasser.`, 3300, 'haut')
  await cliquer(page.locator('.selpop button').filter({ hasText: 'Ne pas masquer' }), { apres: 1200 })
  await capOff()
  const mot = 'boulangerie-pâtisserie'
  const geo = (m) => page.evaluate((m) => {
    const w = document.createTreeWalker(document.querySelector('.verif-overlay'), NodeFilter.SHOW_TEXT)
    let n; while ((n = w.nextNode())) { const i = n.textContent.indexOf(m); if (i >= 0) { const rg = document.createRange(); rg.setStart(n, i); rg.setEnd(n, i + m.length); const rs = rg.getClientRects(); const a = rs[0], z = rs[rs.length - 1]; return { x1: a.left + 2, y1: a.top + a.height / 2, x2: z.right - 2, y2: z.top + z.height / 2, top: a.top } } }
    return null
  }, m)
  const g0 = await geo(mot)
  if (g0 && (g0.top < 150 || g0.top > 760)) { await page.mouse.wheel(0, g0.top - 450); await sleep(900) }
  const g = await geo(mot)
  if (g) {
    await cap(`Un élément oublié ? <b>Sélectionnez-le</b> dans le document pour le masquer.`, 1200, 'haut')
    await bouger(g.x1, g.y1, 800)
    await page.mouse.down()
    await bouger(g.x2, g.y2, 900)
    await page.mouse.up()
    await sleep(1400)
    await cliquer(page.locator('.selpop button').filter({ hasText: 'Identifiants' }), { apres: 1400 })
    await capOff()
  }
  const valider = page.locator('.big-send')
  await vers(valider, 800)
  await cap(`Contrôle fait : validez. La pièce passe <b>« Vérifiée »</b> et l'IA pourra la lire.`, 3300, 'haut')
  await cliquer(valider, { apres: 1700 })
  await capOff()
  for (const nom of ['Commandement de payer', 'Mail du client']) {
    await cliquer(ligne(nom).getByRole('button', { name: 'Aperçu' }), { apres: 2500 })
    if (nom === 'Mail du client') { await cap(`Les e-mails aussi : expéditeur, adresse, téléphone… tout est repéré.`, 3600, 'haut'); await capOff() }
    await cliquer(page.locator('.big-send'), { apres: 1400 })
  }
  await sleep(700)

  // ================= 5. CONVERSATION =================
  await chapitre(5, "Poser une question à l'IA", "Comme à un collaborateur : l'IA connaît tout le dossier.")
  await finChapitre()
  await cliquer(onglet(/^Conversations/), { apres: 1000 })
  await envoyer("Le preneur n'a toujours pas payé. Fais le point : la clause résolutoire est-elle acquise ? Quelle suite donner ?")
  await cap(`TEN masque la demande et les pièces, envoie la version masquée, puis <b>rétablit les vraies valeurs</b> dans la réponse.`, 3000, 'haut')
  await page.waitForSelector('.bubble >> text=Où en est-on', { timeout: 60000 })
  await sleep(1100)
  await capOff()
  await cap(`La réponse cite les pièces et les textes, avec <b>les vrais noms</b> de vos parties.`, 3800, 'haut')
  await page.mouse.wheel(0, 400); await sleep(1500)
  await page.mouse.wheel(0, 500); await sleep(1400)
  await capOff()
  const ajout = page.getByRole('button', { name: 'Ajouter', exact: true }).first()
  if (await ajout.count()) {
    await vers(ajout, 800)
    await cap(`L'IA a repéré un <b>délai</b> : un clic pour l'ajouter à vos échéances.`, 3000, 'haut')
    await cliquer(ajout, { apres: 1300 })
    await capOff()
  }
  const bascule = page.getByRole('switch').first()
  await vers(bascule, 900)
  await cap(`Et voici <b>exactement ce que l'IA a reçu</b>…`, 1700, 'haut')
  await cliquer(bascule, { apres: 800 })
  await page.mouse.wheel(0, -2000); await sleep(800)
  await cap(`Aucun nom, aucune adresse, aucun numéro : seulement des étiquettes comme <b>[SOCIETE_1]</b> ou <b>[PERSONNE_3]</b>.`, 5400, 'haut')
  await capOff()
  await cliquer(bascule, { apres: 1100 })

  // ================= 6. RÉDACTION =================
  await chapitre(6, 'Faire rédiger', 'Courriers, actes, e-mails : prêts à relire, avec les vrais noms.')
  await finChapitre()
  await envoyer('Rédige une mise en demeure à Madame Soulier, en sa qualité de caution.', '.production', 28)
  await sleep(800)
  const prod = page.locator('.production').last()
  await prod.scrollIntoViewIfNeeded()
  await vers(prod, 900)
  await spotLoc(prod, 8)
  await cap(`Le Word est prêt, <b>avec les vrais noms</b>, et rangé dans les pièces du dossier. Les originaux ne sont jamais modifiés.`, 5000, 'haut')
  await spotOff(); await capOff()
  await envoyer('Prépare aussi un mail au client pour lui faire le point.', '.bubble >> text=préparé un e-mail', 30)
  await sleep(900)
  await cap(`L'e-mail s'ouvre en <b>brouillon dans Outlook</b>. Rien n'est jamais envoyé sans vous.`, 4000, 'haut')
  await capOff()
  const pastille = page.locator('.choix-modele').first()
  if (await pastille.count()) {
    await cliquer(pastille, { apres: 900 })
    await cap(`Choisissez l'IA et le niveau de réflexion : <b>Rapide</b> pour une question simple, <b>Approfondi</b> ou <b>Maximum</b> pour une analyse longue.`, 4600, 'haut')
    await page.keyboard.press('Escape'); await sleep(200)
    if (await page.locator('.menu-modele').count()) await cliquer(pastille, { apres: 400 })
    await capOff()
  }

  // ================= 7. DEVIS & HONORAIRES =================
  await chapitre(7, 'Devis et honoraires', "L'IA rédige le devis, TEN suit l'acceptation, la facturation et l'encaissement.")
  await finChapitre()
  await envoyer('Prépare un devis forfaitaire de 2 500 € HT pour la procédure de référé.', '.production', 28)
  await sleep(1200)
  await cap(`Le devis est rédigé et <b>enregistré dans le dossier</b>.`, 3200, 'haut')
  await capOff()
  await cliquer(onglet(/^Devis/), { apres: 1400 })
  await cap(`L'onglet <b>Devis & honoraires</b> suit chaque devis : accepté, facturé, encaissé.`, 3800, 'haut')
  const accepte = page.getByRole('button', { name: /Accepté/ }).first()
  if (await accepte.count()) { await cliquer(accepte, { apres: 1600 }) }
  await capOff()
  await cliquer(menu('Statistiques'), { apres: 1800 })
  await cap(`<span class="k">Statistiques</span>Honoraires acceptés, facturés, encaissés, mois par mois. Et l'activité de vos dossiers.`, 5000)
  await capOff()

  // ================= 8. ÉCHÉANCES =================
  await chapitre(8, 'Suivre les échéances', "Tous les délais de vos dossiers, y compris ceux repérés par l'IA.")
  await finChapitre()
  await cliquer(menu('Échéances'), { apres: 1800 })
  await cap(`Vos cinq prochaines semaines <b>en relief</b> : plus la pile est haute, plus la journée est chargée.`, 4500)
  await page.mouse.wheel(0, 600); await sleep(1500)
  await cap(`Chaque échéance avec sa <b>date</b> et sa <b>base légale</b>, ici l'assignation en référé.`, 4000)
  await capOff()

  // ================= 9. BROUILLON =================
  await chapitre(9, 'Le Brouillon', 'Une question rapide, hors dossier.')
  await finChapitre()
  await cliquer(menu('Brouillon'), { apres: 1300 })
  await envoyer('Quels dossiers ont une échéance ce mois-ci ?', null, 34)
  await cap(`Le Brouillon connaît vos dossiers et vos échéances, et peut <b>ouvrir un dossier pour vous</b>.`, 4600)
  await capOff(800)
  await sleep(1500)

  // ================= 10. BIBLIOTHÈQUE & COMPTE =================
  await chapitre(10, 'Bibliothèque et compte', 'Vos modèles, les sources officielles, vos IA, Lexis Poly.')
  await finChapitre()
  await cliquer(menu('Bibliothèque'), { apres: 1400 })
  await cap(`La <b>Bibliothèque</b> : vos modèles (papier à en-tête…) et les <b>sources juridiques officielles</b> en accès libre, à portée de clic.`, 5000)
  await capOff()
  await cliquer(menu('Compte'), { apres: 1500 })
  await cap(`<span class="k">Compte</span>Choisissez votre IA : <b>ChatGPT</b>, <b>Claude</b> ou une clé API. Seules les demandes masquées leur sont envoyées.`, 5200)
  await capOff()
  const som = (t) => page.getByText(t, { exact: true }).first()
  if (await som('Lexis Poly').count()) {
    await cliquer(som('Lexis Poly'), { apres: 1300 })
    await cap(`Reliez <b>Lexis Poly</b> : fiches préremplies, documents importés et masqués, temps saisis… et rien n'est écrit dans Poly sans votre validation.`, 5600)
    await capOff()
  }
  if (await som('Apparence').count()) {
    await cliquer(som('Apparence'), { apres: 900 })
    const sombre = page.locator('.cpt-theme').filter({ hasText: 'Sombre' }).first()
    if (await sombre.count()) {
      await cliquer(sombre, { apres: 900 })
      await cap(`Thème clair ou sombre, au choix.`, 2600)
      await capOff()
      await cliquer(page.locator('.cpt-theme').filter({ hasText: 'Clair' }).first(), { apres: 900 })
    }
  }
  const jr = page.getByText('Journal des envois').first()
  if (await jr.count()) {
    await cliquer(jr, { apres: 1300 })
    await cap(`Le <b>journal</b> : chaque envoi y est noté avec le nombre d'éléments masqués, jamais son contenu.`, 4800)
    await capOff()
  }
  await cliquer(menu('Accueil'), { apres: 2000 })
  await cap(`De retour à l'accueil : <b>votre journée en bref</b>, vos échéances en relief, vos dossiers… <b>TEN Assistant est prêt.</b>`, 5200)
  await capOff()

  // ================= FIN =================
  marque('fin')
  await page.evaluate(() => window.__card(`<img src="/src/logo.webp"><h1>À vous de jouer</h1><p>Créez un dossier, remplissez la fiche, déposez vos pièces, vérifiez… et posez votre première question.</p>`))
  await sleep(5500)

  await cdp.send('Page.stopScreencast')
  await sleep(300)
  fs.writeFileSync(path.join(S, 'frames.json'), JSON.stringify({ index, marques, t0 }))
  console.log('images :', index.length, 'durée :', (index.at(-1)[1] - index[0][1]).toFixed(1), 's')
  await browser.close()
}

main().catch((e) => { console.error(e); process.exit(1) })
