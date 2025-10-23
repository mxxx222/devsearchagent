# 📦 npm ja n8n Asennus ja Käyttö

## ✅ Asennus Valmis!

npm ja n8n ovat nyt asennettu ja konfiguroitu projektisi käyttöön.

### 🔧 Asennettu:

- **Node.js**: v24.10.0 ✅
- **npm**: v11.6.0 ✅  
- **n8n**: v1.116.2 ✅
- **Lisäpaketit**: axios, nodemon, concurrently ✅

## 🚀 Käyttöohjeet

### 1. n8n Käynnistys

```bash
# Tavallinen käynnistys
n8n start

# Tai käytä mukautettua scriptiä
node start_n8n.js

# Tai npm scriptillä
npm run n8n
```

**n8n on saatavilla osoitteessa**: `http://localhost:5678`

### 2. Workflow Tuonti

1. Avaa n8n selaimessa: `http://localhost:5678`
2. Klikkaa **"Import from file"**
3. Valitse tiedosto: `n8n_automation_workflow.json`
4. Klikkaa **"Import"**

### 3. npm Scriptit

```bash
# Käynnistä Flask sovellus
npm start

# Kehitystilassa
npm run dev

# Automaatio (4h päivitykset)
npm run automation

# Automaation testaus
npm run automation-test

# Testit
npm test

# Asenna Python riippuvuudet
npm run install-deps

# Täysi setup
npm run setup
```

## 🔧 n8n Konfiguraatio

### Ympäristömuuttujat

n8n käyttää seuraavia oletusasetuksia:

- **Host**: localhost
- **Port**: 5678
- **Protocol**: http
- **Editor URL**: http://localhost:5678

### Workflow Ominaisuudet

Luotu workflow sisältää:

1. **Cron Trigger** - Ajastettu 4 tunnin välein
2. **API Kutsut** - Flask sovelluksen API:ihin
3. **Tietojen Käsittely** - AI suositusten ja trending topicien analysointi
4. **Ilmoitukset** - Slack ja email ilmoitukset
5. **Tietokanta** - Tulosten tallennus
6. **Lokitus** - Suorituksen seuranta

## 📊 API Endpointit

Workflow käyttää seuraavia API endpointteja:

- `POST /api/recommendations/trigger` - AI suositusten generointi
- `GET /api/twitter/analyze` - Twitter trendien analysointi
- `POST /api/scheduler/trigger` - Topic haku
- `GET /api/recommendations` - AI suositusten haku
- `GET /api/trending` - Trending topicien haku
- `GET /api/twitter/search` - Twitter tweetien haku

## 🔒 Turvallisuus

### Rate Limiting
- **API kutsut**: 20-30 kutsu minuutissa
- **Input validointi**: Kaikki syötteet validoidaan
- **CSRF suojaus**: Aktiivinen

### Credentials
Tallenna herkät tiedot n8n credential storeen:
- Slack webhook URL
- Email SMTP asetukset
- Tietokanta yhteystiedot

## 🧪 Testaus

### 1. Testaa n8n

```bash
# Käynnistä n8n
npm run n8n

# Avaa selaimessa
open http://localhost:5678
```

### 2. Testaa Workflow

```bash
# Testaa automaatiota
npm run automation-test

# Täysi testaus
npm test
```

### 3. Testaa API:t

```bash
# Testaa Flask API:t
curl http://localhost:8080/api/recommendations

# Testaa Twitter API:t
curl http://localhost:8080/api/twitter/trending
```

## 🔧 Vianmääritys

### Yleiset Ongelmat

1. **Port 5678 käytössä**
   ```bash
   # Tarkista käyttäjä
   lsof -i :5678
   
   # Tapa prosessi
   kill -9 <PID>
   ```

2. **n8n ei käynnisty**
   ```bash
   # Asenna uudelleen
   npm uninstall -g n8n
   npm install -g n8n
   ```

3. **Workflow ei toimi**
   - Tarkista API endpointit
   - Varmista että Flask sovellus pyörii
   - Tarkista credentialit

### Logit

- **n8n logit**: Näkyvät terminaalissa
- **Flask logit**: `app.log` tiedostossa
- **Automaatio logit**: `automation_log.json`

## 📈 Suorituskyky

### Optimoinnit

1. **n8n Asetukset**
   - Käytä Redis cacheä
   - Konfiguroi worker prosessit
   - Optimoi workflow suoritus

2. **API Kutsut**
   - Käytä batch kutsuja
   - Implementoi retry logiikka
   - Cache tuloksia

3. **Tietokanta**
   - Käytä indeksejä
   - Optimoi kyselyt
   - Käytä connection pooling

## 🚀 Tuotantoon Siirtäminen

### 1. n8n Tuotantoasetukset

```bash
# Aseta tuotantoympäristö
export N8N_ENV=production
export N8N_SECURE_COOKIE=true
export N8N_HOST=your-domain.com
export N8N_PORT=443
export N8N_PROTOCOL=https
```

### 2. SSL/TLS

```bash
# Käytä HTTPS:ää
export N8N_PROTOCOL=https
export N8N_SSL_KEY=/path/to/private.key
export N8N_SSL_CERT=/path/to/certificate.crt
```

### 3. Tietokanta

```bash
# Käytä PostgreSQL:ää
export DB_TYPE=postgresdb
export DB_POSTGRESDB_HOST=your-db-host
export DB_POSTGRESDB_PORT=5432
export DB_POSTGRESDB_DATABASE=n8n
export DB_POSTGRESDB_USER=n8n
export DB_POSTGRESDB_PASSWORD=your-password
```

## 📚 Lisätietoja

### Hyödylliset Linkit

- [n8n Dokumentaatio](https://docs.n8n.io/)
- [n8n Community](https://community.n8n.io/)
- [n8n GitHub](https://github.com/n8n-io/n8n)

### Tuki

Jos kohtaat ongelmia:

1. Tarkista logit
2. Testaa API:t erikseen
3. Varmista credentialit
4. Tarkista verkkoyhteys

## 🎉 Valmis!

npm ja n8n ovat nyt valmiina käyttöön! Voit:

1. **Käynnistää n8n**: `npm run n8n`
2. **Tuo workflow**: `n8n_automation_workflow.json`
3. **Testata automaatiota**: `npm run automation-test`
4. **Seurata tuloksia**: n8n interfacessa

**Onnea automaation kanssa!** 🚀
