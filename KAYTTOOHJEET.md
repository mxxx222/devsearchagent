# 🚀 DevSearchAgent - Käyttöohjeet

**Projekti**: DevSearchAgent - AI Search Dashboard  
**Versio**: 1.0.0  
**Status**: ✅ **VALMIS JA TOIMIVA**

---

## 🎯 **Nopea Käynnistys**

### 1. Käynnistä Flask App
```bash
cd /Users/herbspotturku/testprojekt22.10.25
source venv/bin/activate
python app.py
```

Tai käytä npm scripteillä:
```bash
npm run start
```

### 2. Avaa Dashboard
Selaimessa:
- **URL**: http://localhost:8080
- Dashboard aukeaa automaattisesti

Tai manuaalisesti:
```bash
open http://localhost:8080
```

---

## 🌐 **Dashboard Ominaisuudet**

### Pääkäyttöliittymä
- **Search Bar**: Hae AI-codaus ja ohjelmointi-aiheita
- **Trending Topics**: Reaaliaikaiset trendit
- **AI Recommendations**: AI-suositukset OpenAI ja Gemini -lähteistä
- **Engagement Metrics**: Tykkäykset, jaot, kommentit
- **Interactive Charts**: Data-visualisoinnit

### API Endpointit
- `GET /api/trending` - Trending topics
- `GET /api/recommendations` - AI suositukset
- `GET /api/engagement/summary` - Yhteenveto
- `POST /api/search` - Haku

---

## 🔧 **Konfiguraatio**

### API-avaimet (Valinnainen)
Edistä toimivuutta lisäämällä `config.env`:
```env
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
TWITTER_BEARER_TOKEN=your_twitter_token
```

Ilman avaimia:
- ✅ Web Dashboard toimii
- ✅ Mock data näytetään
- ⚠️ AI-suositukset rajoitettuja
- ⚠️ Twitter-integraatio rajoitettu

---

## 🧪 **Testaus**

### System Test
```bash
# Flask app käynnissä toisessa terminaalissa
python test_complete_system.py
```

### API Test
```bash
# Test trending
curl http://localhost:8080/api/trending

# Test recommendations
curl http://localhost:8080/api/recommendations

# Test search
curl -X POST http://localhost:8080/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "AI coding"}'
```

---

## 📊 **Tiedot**

### Toimivat Komponentit
- ✅ **Dashboard UI** - Responsiivinen käyttöliittymä
- ✅ **Search API** - Monimoottorinen haku
- ✅ **Trending Detection** - Reaaliaikaiset trendit
- ✅ **Database** - SQLite tallennus
- ✅ **Security** - CSRF, rate limiting
- ✅ **Mobile Support** - Responsiivinen design

### Rajoittavat Tekijät
- ⚠️ **OpenAI/Gemini**: Tarvitsee API-avaimet täyteen toimivuuteen
- ⚠️ **Twitter API**: Tarvitsee Bearer Tokenin
- ℹ️ **Redis**: Ei välttämätön (käyttää in-memory)

---

## 🛠️ **Automaatio (Valinnainen)**

### n8n Workflow
```bash
# Käynnistä n8n
npm run n8n

# Access n8n
open http://localhost:5678

# Import workflow
# Tiedosto: n8n_automation_workflow_fixed.json
```

### Python Automaatio
```bash
# Yksittäinen suoritus
python topic_automation.py --once

# Aikataulu (4 tunnin välein)
python topic_automation.py
```

---

## 📁 **Projekti Rakenne**

```
testprojekt22.10.25/
├── app.py                    # Pääsovellus
├── search/                   # Hakumoottorit
│   ├── engines/             # Google, DuckDuckGo, Bing
│   ├── trending/            # Trendien tunnistus
│   ├── ai/                  # AI-suositukset
│   └── social/              # Sosiaalisen median integraatio
├── templates/               # HTML-mallit
│   └── dashboard.html       # Päädashboard
├── static/                  # CSS, JS
│   ├── css/style.css       # Tyylit
│   └── js/dashboard.js     # JavaScript
└── trending_data.db         # Tietokanta
```

---

## 🎓 **Käyttötapaukset**

### 1. Trendien Seuranta
- Avaa http://localhost:8080
- Tarkastele trending-topicsia
- Seuraa muutoksia

### 2. AI-suositukset
- Avaa "AI Recommendations" -osio
- Filtteroi OpenAI- tai Gemini-lähteellä
- Seuraa new topicsia

### 3. Trendianalyysi
- Katso engagement-mittareita
- Aikajakso: päivittäin, kuukausittain, vuosittain
- Tarkastele top-topicsia

### 4. Haku
- Kirjoita hakusana
- Monimoottorinen haku
- Tarkastele tuloksia

---

## 🔍 **Vianetsintä**

### Localhost ei aukea
```bash
# Pysäytä vanhat prosessit
pkill -9 -f "python.*app.py"

# Käynnistä uudelleen
python app.py
```

### Portti varattu
```bash
# Muuta PORT muuttuja
export PORT=8081
python app.py
```

### Import-virheet
```bash
# Päivitä riippuvuudet
pip install -r requirements.txt
```

---

## 📞 **Tuki**

### Dokumentaatio
- `README.md` - Yleiskuvaus
- `COMPLETE_SYSTEM_STATUS.md` - Status-raportti
- `KORJAUSOHJEET.md` - Korjausohjeet
- `LOPPUVIELEISIA_KORJAUKSIA.md` - Viimeisimmät korjaukset

### Testit
- `test_complete_system.py` - System test
- `test_app.py` - Unit testit
- `test_automation.py` - Automaatio testit

---

## 🎉 **Ready to Go!**

**DevSearchAgent on nyt valmis käyttöön!**

- ✅ Localhost toimii
- ✅ Dashboard näkyy
- ✅ Kaikki API:t toimivat
- ✅ Testauskattavuus kattava
- ✅ Dokumentaatio täydellinen

**Nauti AI-pohjaisesta hakutyökalusta!** 🚀

---

**Viimeksi päivitetty**: 2025-10-23  
**Versio**: 1.0.0  
**Status**: ✅ **VALMIS**

