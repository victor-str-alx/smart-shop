# 🛒 SmartShop - Sistem E-Commerce cu Recomandări ML

Platformă e-commerce modernă cu sistem avansat de recomandări bazat pe Machine Learning, dezvoltată cu Django și PostgreSQL.

## 📋 Cuprins

- [Despre Proiect](#despre-proiect)
- [Caracteristici Principale](#caracteristici-principale)
- [Tehnologii Utilizate](#tehnologii-utilizate)
- [Arhitectura Sistemului](#arhitectura-sistemului)
- [Algoritmi Machine Learning](#algoritmi-machine-learning)
- [Instalare și Configurare](#instalare-și-configurare)
- [Utilizare](#utilizare)
- [Structura Proiectului](#structura-proiectului)
- [Baza de Date](#baza-de-date)
- [Capturi de Ecran](#capturi-de-ecran)

## 📖 Despre Proiect

SmartShop este o aplicație e-commerce completă care implementează algoritmi avansați de Machine Learning pentru a oferi recomandări personalizate utilizatorilor. Sistemul analizează comportamentul de cumpărare și caracteristicile produselor pentru a sugera articole relevante.

### Obiective

- ✅ Implementare sistem de recomandări ML (TF-IDF + Collaborative Filtering)
- ✅ Platformă e-commerce funcțională și intuitivă
- ✅ UI/UX modern și responsive
- ✅ Sistem complet de management comenzi
- ✅ Reviews și ratings pentru produse
- ✅ Export comenzi în format PDF
- ✅ Dashboard cu statistici și grafice

## ⭐ Caracteristici Principale

### 1. Sistem de Recomandări ML

**Content-Based Filtering (TF-IDF)**
- Analizează descrierile și categoriile produselor
- Folosește TF-IDF vectorization pentru similaritate textuală
- Calculează cosine similarity între produse
- Recomandă produse similare cu cele cumpărate anterior

**Collaborative Filtering (User-based)**
- Identifică utilizatori cu preferințe similare
- Construiește matrice user-item pentru pattern-uri de cumpărare
- Folosește cosine similarity pentru a găsi "vecini apropați"
- Recomandă produse cumpărate de utilizatori similari

**Hybrid Recommendations**
- Combină ambele abordări pentru acuratețe maximă
- Balanșează recomandări bazate pe conținut și comportament

### 2. Funcționalități E-Commerce

- **Catalog Produse**: Browsing, filtrare și sortare avansată
- **Categorii Inteligente**: Sugerează categorii asociate bazate pe co-purchase patterns
- **Căutare Avansată**: Suport pentru căutare fără diacritice
- **Coș de Cumpărături**: Management comenzi în timp real
- **Istoric Comenzi**: Vizualizare completă a achizițiilor anterioare
- **Export PDF**: Generare facturi profesionale pentru comenzi
- **Reviews & Ratings**: Sistem complet de evaluare produse
- **Dashboard**: Statistici personale și grafice de vânzări

### 3. UI/UX Modern

- Design responsive (mobile-first)
- Gradient styling și animații fluide
- Card-uri cu hover effects
- Empty states friendly
- Bootstrap Icons integration
- Dark/light color schemes

## 🛠️ Tehnologii Utilizate

### Backend
- **Django 5.2.8** - Web framework
- **PostgreSQL** - Bază de date relațională
- **Python 3.14** - Limbaj de programare

### Machine Learning
- **scikit-learn** - TF-IDF vectorization și cosine similarity
- **NumPy** - Calcule matriciale pentru collaborative filtering

### Frontend
- **Bootstrap 5.3.3** - Framework CSS responsive
- **Bootstrap Icons 1.11.1** - Iconițe moderne
- **Chart.js 4.4.0** - Grafice interactive
- **Custom CSS** - Styling personalizat cu gradients

### Librării Adiționale
- **ReportLab 4.4.5** - Generare PDF-uri
- **Pillow** - Procesare imagini

## 🏗️ Arhitectura Sistemului

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP Requests
       ▼
┌─────────────────┐
│  Django Views   │ ◄─── URL Routing
└────────┬────────┘
         │
    ┌────┴─────┬──────────────┐
    │          │              │
    ▼          ▼              ▼
┌────────┐ ┌────────┐  ┌──────────────┐
│ Models │ │Templates│  │ ML Recommender│
└────┬───┘ └────────┘  └──────┬───────┘
     │                        │
     ▼                        ▼
┌──────────┐          ┌───────────────┐
│PostgreSQL│          │ scikit-learn  │
│ Database │          │    & NumPy    │
└──────────┘          └───────────────┘
```

### Componente Principale

1. **Models Layer** - Definește structura datelor (User, Product, Order, Review, etc.)
2. **Views Layer** - Logica business și procesare requests
3. **Templates Layer** - Rendering HTML cu Bootstrap
4. **Recommender Module** - Algoritmi ML pentru recomandări
5. **Management Commands** - Populare date de test

## 🤖 Algoritmi Machine Learning

### TF-IDF Content-Based Filtering

```python
# Vectorizare text
vectorizer = TfidfVectorizer(
    max_features=100,
    stop_words='english',
    ngram_range=(1, 2)
)

# Calculare similaritate
similarity_scores = cosine_similarity(candidate_vectors, user_vectors)
avg_similarity = similarity_scores.mean(axis=1)

# Top N recomandări
top_indices = avg_similarity.argsort()[-top_n:][::-1]
```

**Cum funcționează:**
1. Extrage descrierile produselor cumpărate de user
2. Creează vectori TF-IDF pentru toate produsele
3. Calculează similaritatea cosinus între produse
4. Returnează produsele cele mai similare

### User-Based Collaborative Filtering

```python
# Construire matrice user-item
matrix = np.zeros((len(users), len(products)))
for user_purchases in all_purchases:
    matrix[user_idx][product_idx] = quantity

# Similaritate între utilizatori
similarities = cosine_similarity(current_user_vector, matrix)[0]

# Găsire utilizatori similari
similar_user_indices = similarities.argsort()[-5:][::-1]
```

**Cum funcționează:**
1. Construiește matrice cu pattern-uri de cumpărare
2. Calculează similaritatea între utilizatori
3. Identifică "vecini" cu gusturi similare
4. Recomandă produse cumpărate de vecini

## 📦 Instalare și Configurare

### Prerequisite

- Python 3.10+
- PostgreSQL 12+
- pip (Python package manager)

### Pași de Instalare

1. **Clonează repository-ul**
```bash
git clone <repository-url>
cd tema_recomandare+aplicatie
```

2. **Creează environment virtual**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. **Instalează dependențele**
```bash
pip install -r requirements.txt
```

4. **Configurează baza de date**

Creează un fișier `config/.env`:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_NAME=smartshop
DATABASE_USER=postgres
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

5. **Aplică migrările**
```bash
python manage.py migrate
```

6. **Creează superuser**
```bash
python manage.py createsuperuser
```

7. **Populează baza de date cu date de test**
```bash
python manage.py populate_data --clear
```

8. **Rulează serverul**
```bash
python manage.py runserver
```

Accesează aplicația la: `http://127.0.0.1:8000/`

## 🎯 Utilizare

### Conturi de Test

După rularea comenzii `populate_data`, sunt create următoarele conturi:

| Username | Password | Profil |
|----------|----------|--------|
| ana_popescu | test123 | Pasionată de electronice |
| ion_ionescu | test123 | Entuziast fashion |
| maria_gheorghe | test123 | Decorator de interior |
| alex_dumitru | test123 | Cititor pasionat |
| elena_stan | test123 | Sportivă |

### Fluxul Utilizatorului

1. **Autentificare** - Login cu unul din conturile de test
2. **Explorare Produse** - Browse catalog, filtrare după categorie, sortare
3. **Căutare** - Caută produse (funcționează fără diacritice!)
4. **Recomandări** - Vezi recomandări personalizate pe homepage
5. **Adăugare în Coș** - Click "Adaugă în coș" pe produse
6. **Checkout** - Finalizare comandă din "Comanda mea"
7. **Istoric** - Vezi comenzi anterioare și descarcă PDF
8. **Dashboard** - Statistici personale și trend-uri
9. **Reviews** - Lasă review-uri pentru produse cumpărate

### Funcționalități Admin

Accesează panoul admin la: `http://127.0.0.1:8000/admin/`

- Gestionare produse și categorii
- Vizualizare comenzi
- Moderare review-uri
- Management utilizatori

## 📁 Structura Proiectului

```
tema_recomandare+aplicatie/
│
├── config/                      # Configurări Django
│   ├── settings.py             # Settings principale
│   ├── urls.py                 # URL routing principal
│   └── .env                    # Environment variables
│
├── shop/                       # Aplicația principală
│   ├── models.py               # Modele DB (Product, Order, Review, etc.)
│   ├── views.py                # Views și logică business
│   ├── urls.py                 # URL patterns pentru shop
│   ├── forms.py                # Formulare Django
│   ├── recommender.py          # Algoritmi ML
│   │
│   ├── templates/shop/         # Template-uri HTML
│   │   ├── base.html          # Template de bază
│   │   ├── product_list.html  # Catalog produse
│   │   ├── product_detail.html # Detalii produs
│   │   ├── my_order.html      # Coș cumpărături
│   │   ├── order_history.html # Istoric comenzi
│   │   └── dashboard.html     # Dashboard statistici
│   │
│   ├── static/shop/            # Fișiere statice
│   │   └── styles.css         # CSS personalizat
│   │
│   └── management/commands/    # Comenzi custom
│       └── populate_data.py   # Populare date test
│
├── accounts/                   # Autentificare
│   ├── views.py               # Login/Register
│   └── templates/             # Template-uri auth
│
├── media/                      # Fișiere încărcate
│   └── products/              # Imagini produse
│
├── requirements.txt            # Dependențe Python
└── README.md                  # Documentație
```

## 🗄️ Baza de Date

### Schema ER (Entity-Relationship)

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│   User   │────────▶│  Order   │────────▶│OrderItem │
│(built-in)│  1:N    │          │  1:N    │          │
└──────────┘         └────┬─────┘         └────┬─────┘
                          │                     │
                          │ N:1                 │ N:1
                          ▼                     ▼
                     ┌──────────┐         ┌──────────┐
                     │ Product  │◀────────│ Category │
                     │          │  N:1    │          │
                     └────┬─────┘         └──────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼  1:N                  ▼  1:N
         ┌────────┐              ┌────────┐
         │ Review │              │ Rating │
         └────────┘              └────────┘
              │                       │
              │ N:1                   │ N:1
              └───────────┬───────────┘
                          ▼
                     ┌────────┐
                     │  User  │
                     └────────┘
```

### Modele Principale

**User** (Django built-in)
- username, email, password
- first_name, last_name

**Category**
- name, slug
- Relații: 1:N cu Product

**Product**
- name, description, price, image, slug
- created_at
- FK: category
- Relații: 1:N cu OrderItem, Review, Rating

**Order**
- user (FK), is_open, created_at
- Metode: total_amount (calculat din items)
- Relații: N:1 cu User, 1:N cu OrderItem

**OrderItem**
- order (FK), product (FK)
- quantity, price (snapshot la momentul comenzii)
- Metode: subtotal

**Review**
- product (FK), user (FK)
- rating, title, content, created_at

**Rating**
- product (FK), user (FK), score (1-5)

## 📊 Capturi de Ecran

### Homepage cu Recomandări
![Homepage](docs/screenshots/homepage.png)
*Catalog produse cu recomandări ML personalizate*

### Dashboard cu Statistici
![Dashboard](docs/screenshots/dashboard.png)
*Grafice interactive și statistici utilizator*

### Detalii Produs cu Reviews
![Product Detail](docs/screenshots/product-detail.png)
*Pagină produs cu reviews și recomandări asociate*

### Export PDF Comandă
![PDF Export](docs/screenshots/pdf-export.png)
*Factură profesională generată automat*

## 🎓 Despre Dezvoltare

Acest proiect a fost dezvoltat ca temă pentru cursul de **Comerț Electronic**, demonstrând:

- Implementare algoritmi Machine Learning
- Dezvoltare aplicație web full-stack
- Design pattern-uri (MVC)
- Baze de date relaționale complexe
- UI/UX modern și responsive
- Export documente PDF
- Vizualizare date cu grafice

### Tehnologii învățate:
✅ Django ORM și QuerySets
✅ TF-IDF și Collaborative Filtering
✅ Bootstrap și CSS modern
✅ PostgreSQL și design DB
✅ Chart.js pentru vizualizări
✅ ReportLab pentru PDF

## 📝 Licență

Acest proiect este dezvoltat în scop educațional.

## 👤 Autor

Dezvoltat pentru cursul de Comerț Electronic
Facultatea de Științe Economice și Gestiunea Afacerilor

---

⭐ Dacă acest proiect ți-a fost util, nu uita să lași un star!
