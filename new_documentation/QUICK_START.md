# ⚡ Quick Start Guide - SmartShop

## 🚀 Start în 3 Pași

### 1. Activează Environment
```bash
.venv\Scripts\activate
```

### 2. Pornește Serverul
```bash
python manage.py runserver
```

### 3. Accesează Aplicația
```
http://127.0.0.1:8000/
```

---

## 👤 Login Rapid

**Username:** `ana_popescu`
**Password:** `test123`

*Ana are cele mai multe comenzi → recomandări ML bogate!*

---

## 🎯 Features Quick Tour

### Homepage
- ✅ Recomandări ML personalizate
- ✅ Top Vânzări (sidebar)
- ✅ Filtrare & sortare

### Dashboard
1. Click pe username (top-right)
2. Select "Dashboard"
3. Vezi statistici + grafice

### Export PDF
1. Click "Istoric comenzi"
2. Click "Descarcă PDF" pe orice comandă
3. SAU "Exportă Toate (PDF)"

### Search
- Caută "geaca" → găsește "Geacă" (fără diacritice!)

---

## 🔄 Reset Date
```bash
python manage.py populate_data --clear
```

Regenerează:
- 7 utilizatori
- 44 produse
- 25+ comenzi
- 30-50 reviews

---

## 📁 Documente Importante

- **README.md** - Documentație completă
- **DOCUMENTATIE_TEHNICA.md** - Diagrame & detalii
- **GHID_PREZENTARE.md** - Structură PowerPoint
- **INSTRUCTIUNI_FINALIZARE.md** - Ghid susținere
- **SUMAR_PROIECT.md** - Ce ai realizat

---

## ⚠️ Troubleshooting

**Eroare "No module named django":**
```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

**Eroare database:**
```bash
python manage.py migrate
```

**Port ocupat:**
```bash
python manage.py runserver 8001
```

---

## ✅ Status Check
```bash
python manage.py check
```

Ar trebui să vezi: `System check identified no issues (0 silenced).`

---

**GATA! Proiectul rulează! 🎉**
