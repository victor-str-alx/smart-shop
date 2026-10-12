# Documentație Tehnică - SmartShop

## 1. Diagrama Bazei de Date (ER Diagram)

### Entități și Relații

```
┌────────────────────────────────────────┐
│              USER (Django Auth)         │
│────────────────────────────────────────│
│ PK: id (int)                           │
│    username (varchar)                  │
│    email (varchar)                     │
│    password (hash)                     │
│    first_name (varchar)                │
│    last_name (varchar)                 │
│    date_joined (datetime)              │
└───────────┬────────────────────────────┘
            │
            │ 1:N (are multe comenzi)
            ▼
┌────────────────────────────────────────┐
│              ORDER                      │
│────────────────────────────────────────│
│ PK: id (int)                           │
│ FK: user_id → USER.id                  │
│    is_open (boolean)                   │
│    created_at (datetime)               │
│                                        │
│ Computed: total_amount()               │
└───────────┬────────────────────────────┘
            │
            │ 1:N (conține multe articole)
            ▼
┌────────────────────────────────────────┐
│           ORDER_ITEM                    │
│────────────────────────────────────────│
│ PK: id (int)                           │
│ FK: order_id → ORDER.id                │
│ FK: product_id → PRODUCT.id            │
│    quantity (int)                      │
│    price (decimal) // snapshot         │
│                                        │
│ Computed: subtotal()                   │
└───────────┬────────────────────────────┘
            │
            │ N:1 (referă un produs)
            ▼
┌────────────────────────────────────────┐
│             PRODUCT                     │
│────────────────────────────────────────│
│ PK: id (int)                           │
│ FK: category_id → CATEGORY.id          │
│    name (varchar)                      │
│    slug (varchar, unique)              │
│    description (text)                  │
│    price (decimal)                     │
│    image (imagefield)                  │
│    created_at (datetime)               │
└───────────┬────────────────────────────┘
            │
    ┌───────┴────────┬──────────────┐
    │                │              │
    │ N:1            │ 1:N          │ 1:N
    ▼                ▼              ▼
┌─────────┐    ┌─────────┐    ┌─────────┐
│CATEGORY │    │ REVIEW  │    │ RATING  │
│─────────│    │─────────│    │─────────│
│PK: id   │    │PK: id   │    │PK: id   │
│ name    │    │FK: prod │    │FK: prod │
│ slug    │    │FK: user │    │FK: user │
└─────────┘    │ rating  │    │ score   │
               │ title   │    │(1-5)    │
               │ content │    └─────────┘
               │ created │
               └─────────┘
```

### Cardinalități

| Relație | Tip | Descriere |
|---------|-----|-----------|
| User → Order | 1:N | Un utilizator poate avea multe comenzi |
| Order → OrderItem | 1:N | O comandă conține multe articole |
| Product → OrderItem | 1:N | Un produs poate fi în multe comenzi |
| Category → Product | 1:N | O categorie conține multe produse |
| Product → Review | 1:N | Un produs poate avea multe review-uri |
| Product → Rating | 1:N | Un produs poate avea multe rating-uri |
| User → Review | 1:N | Un utilizator poate lăsa multe review-uri |
| User → Rating | 1:N | Un utilizator poate da multe rating-uri |

## 2. Arhitectura Aplicației

### 2.1 Arhitectură MVC (Model-View-Template)

```
┌─────────────────────────────────────────────┐
│           PRESENTATION LAYER                 │
│  ┌─────────────────────────────────────┐   │
│  │     Browser (HTML/CSS/JS)            │   │
│  │  - Bootstrap 5.3.3                   │   │
│  │  - Chart.js 4.4.0                    │   │
│  │  - Custom CSS with Gradients         │   │
│  └──────────────┬──────────────────────┘   │
└─────────────────┼──────────────────────────┘
                  │ HTTP Requests/Responses
┌─────────────────▼──────────────────────────┐
│           APPLICATION LAYER                 │
│  ┌────────────────────────────────────┐    │
│  │         Django URLs                 │    │
│  │    (Routing & Dispatching)         │    │
│  └──────────────┬─────────────────────┘    │
│                 │                           │
│  ┌──────────────▼─────────────────────┐    │
│  │         Django Views                │    │
│  │  - product_list()                   │    │
│  │  - product_detail()                 │    │
│  │  - my_order() / checkout()          │    │
│  │  - order_history()                  │    │
│  │  - dashboard()                      │    │
│  │  - export_order_pdf()               │    │
│  └──────────┬───────────┬──────────────┘    │
└─────────────┼───────────┼──────────────────┘
              │           │
     ┌────────┴──┐    ┌───┴──────────┐
     │           │    │              │
┌────▼───────┐   │    │  ┌──────────▼────┐
│  TEMPLATES │   │    │  │  RECOMMENDER  │
│  (Django)  │   │    │  │    MODULE     │
│            │   │    │  │               │
│ - base.html│   │    │  │ - TF-IDF      │
│ - product_*│   │    │  │ - Collab Filt │
│ - order_*  │   │    │  │ - Hybrid      │
│ - dashboard│   │    │  └───────────────┘
└────────────┘   │    │
                 │    │
┌────────────────▼────▼──────────────────────┐
│            DATA LAYER                       │
│  ┌────────────────────────────────────┐    │
│  │       Django ORM                    │    │
│  │  - QuerySets                        │    │
│  │  - Model Methods                    │    │
│  │  - Managers                         │    │
│  └──────────────┬─────────────────────┘    │
│                 │                           │
│  ┌──────────────▼─────────────────────┐    │
│  │      PostgreSQL Database            │    │
│  │  - Relational tables                │    │
│  │  - Indexes                          │    │
│  │  - Constraints                      │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│          EXTERNAL SERVICES                   │
│  - Media Storage (File System)              │
│  - PDF Generation (ReportLab)               │
│  - ML Libraries (scikit-learn, NumPy)       │
└─────────────────────────────────────────────┘
```

### 2.2 Flow Diagram - Procesul de Recomandare

```
START
  │
  ▼
┌─────────────────┐
│ User accesează  │
│   Homepage      │
└────────┬────────┘
         │
    ┌────▼─────┐
    │Autentif? │
    └────┬─────┘
         │
    ┌────▼─────────────┐
    │ DA           NU   │
    │                   │
    ▼                   ▼
┌────────────┐    ┌───────────┐
│Verifică    │    │Afișează   │
│comenzi     │    │produse    │
│anterioare  │    │generale   │
└─────┬──────┘    └───────────┘
      │                 │
      ▼                 │
┌───────────┐           │
│Are comenzi?│          │
└─────┬──────┘          │
      │                 │
  ┌───▼───┐             │
  │DA  NU │             │
  │       │             │
  ▼       ▼             │
┌────┐ ┌─────┐          │
│    │ │     │          │
│    │ │  └──┴──────────┘
│    │ │
│    │ │  RECOMANDĂRI ML
│    │ │  ───────────────
│    ▼ ▼
│  ┌────────────────────────┐
│  │1. Content-Based (TF-IDF)│
│  │─────────────────────────│
│  │ - Extrage produse       │
│  │   cumpărate anterior    │
│  │ - Vectorizare TF-IDF    │
│  │   pe descrieri          │
│  │ - Calcul cosine         │
│  │   similarity            │
│  │ - Top N similare        │
│  └──────────┬──────────────┘
│             │
│             ▼
│  ┌────────────────────────┐
│  │2. Collaborative Filter │
│  │─────────────────────────│
│  │ - Construire matrice    │
│  │   user-item             │
│  │ - Găsire utilizatori    │
│  │   similari              │
│  │ - Produse ale vecinilor│
│  │ - Top N recomandate     │
│  └──────────┬──────────────┘
│             │
│             ▼
│  ┌────────────────────────┐
│  │3. Agregare Rezultate   │
│  │─────────────────────────│
│  │ - Combinare cele 2      │
│  │   abordări              │
│  │ - Eliminare duplicate   │
│  │ - Sortare după score    │
│  └──────────┬──────────────┘
│             │
└─────────────┘
              │
              ▼
    ┌──────────────────┐
    │ Afișare produse  │
    │  recomandate pe  │
    │    homepage      │
    └──────────────────┘
              │
              ▼
            END
```

### 2.3 Sequence Diagram - Plasare Comandă

```
User        Browser      Django View    Database    ML Module
 │             │              │            │            │
 │ Click pe    │              │            │            │
 │ "Adaugă în  │              │            │            │
 │ coș"        │              │            │            │
 ├────────────►│              │            │            │
 │             │ POST         │            │            │
 │             │ add_to_order │            │            │
 │             ├─────────────►│            │            │
 │             │              │ SELECT     │            │
 │             │              │ Order      │            │
 │             │              ├───────────►│            │
 │             │              │◄───────────┤            │
 │             │              │            │            │
 │             │              │ INSERT     │            │
 │             │              │ OrderItem  │            │
 │             │              ├───────────►│            │
 │             │              │◄───────────┤            │
 │             │              │            │            │
 │             │◄─────────────┤            │            │
 │             │ Redirect     │            │            │
 │◄────────────┤              │            │            │
 │             │              │            │            │
 │ Navigare    │              │            │            │
 │ la "Comanda │              │            │            │
 │ mea"        │              │            │            │
 ├────────────►│              │            │            │
 │             │ GET          │            │            │
 │             │ my_order     │            │            │
 │             ├─────────────►│            │            │
 │             │              │ SELECT     │            │
 │             │              │ Order      │            │
 │             │              │ with Items │            │
 │             │              ├───────────►│            │
 │             │              │◄───────────┤            │
 │             │              │            │            │
 │             │◄─────────────┤            │            │
 │             │ HTML         │            │            │
 │◄────────────┤              │            │            │
 │             │              │            │            │
 │ Click       │              │            │            │
 │ "Finalizează│              │            │            │
 │ Comanda"    │              │            │            │
 ├────────────►│              │            │            │
 │             │ POST         │            │            │
 │             │ checkout     │            │            │
 │             ├─────────────►│            │            │
 │             │              │ UPDATE     │            │
 │             │              │ Order      │            │
 │             │              │ is_open=   │            │
 │             │              │ False      │            │
 │             │              ├───────────►│            │
 │             │              │◄───────────┤            │
 │             │              │            │            │
 │             │              │  Trigger   │            │
 │             │              │  Retrain   │            │
 │             │              │  Model     │            │
 │             │              ├────────────┼───────────►│
 │             │              │            │◄───────────┤
 │             │              │            │            │
 │             │◄─────────────┤            │            │
 │             │ Redirect     │            │            │
 │◄────────────┤              │            │            │
 │             │              │            │            │
```

## 3. Algoritmi Machine Learning - Detalii Tehnice

### 3.1 TF-IDF Content-Based Filtering

**Input:**
- Lista produselor cumpărate anterior de user
- Toate produsele din catalog (candidates)

**Proces:**
1. Extragere text: `description + " " + category`
2. Creare corpus: `user_products + candidate_products`
3. Vectorizare TF-IDF:
   ```python
   TfidfVectorizer(
       max_features=100,      # Top 100 termeni
       stop_words='english',  # Elimină cuvinte comune
       ngram_range=(1, 2)     # Unigrams și bigrams
   )
   ```
4. Split vectori:
   - `user_vectors = tfidf_matrix[:len(user_products)]`
   - `candidate_vectors = tfidf_matrix[len(user_products):]`
5. Cosine similarity:
   ```python
   similarity = cosine_similarity(candidate_vectors, user_vectors)
   avg_similarity = similarity.mean(axis=1)
   ```
6. Sortare și selecție Top N

**Output:**
- Lista de produse ordonate după similaritate
- Score pentru fiecare recomandare

**Complexitate:**
- Timp: O(n * m * f) unde n=candidates, m=user_products, f=features
- Spațiu: O(n * f) pentru matrice TF-IDF

### 3.2 User-Based Collaborative Filtering

**Input:**
- User ID curent
- Toate comenzile din sistem

**Proces:**
1. Construire user-item matrix:
   ```python
   matrix = np.zeros((num_users, num_products))
   for order in orders:
       matrix[user_idx][product_idx] = quantity
   ```
2. Extragere vector user curent:
   ```python
   current_user_vector = matrix[current_user_idx].reshape(1, -1)
   ```
3. Calcul similaritate cu toți userii:
   ```python
   similarities = cosine_similarity(current_user_vector, matrix)[0]
   ```
4. Găsire top K vecini:
   ```python
   similar_user_indices = similarities.argsort()[-5:][::-1]
   ```
5. Colectare produse ale vecinilor (necu mpărate de user curent)
6. Sortare după frecvență și similaritate

**Output:**
- Produse recomandate bazate pe comportamentul vecinilor
- Score combinat (similaritate user * popularitate produs)

**Complexitate:**
- Timp: O(u * p) pentru construire matrice + O(u^2 * p) pentru similaritate
- Spațiu: O(u * p) pentru matrice completă

### 3.3 Hybrid Approach

**Strategie:**
1. Rulează ambii algoritmi în paralel
2. Combină rezultatele:
   - Weight content-based: 60%
   - Weight collaborative: 40%
3. Elimină duplicate
4. Sortare finală după score combinat

**Avantaje:**
- Rezolvă "cold start problem" pentru utilizatori noi (content-based)
- Descoperă pattern-uri unexpected (collaborative)
- Acuratețe mai bună decât metodele individuale

## 4. Optimizări Implementate

### 4.1 Database Query Optimization

```python
# ✅ Bună practică - Prefetch related
products = Product.objects.all() \
    .select_related('category') \
    .prefetch_related('ratings', 'reviews')

# ✅ Agregări în database
top_sold = Product.objects \
    .annotate(total_sold=Sum('order_items__quantity')) \
    .filter(total_sold__gt=0) \
    .order_by('-total_sold')[:5]
```

### 4.2 Caching Strategies

- QuerySet results sunt cache-ate în view
- TF-IDF matrix nu se recalculează pentru fiecare request
- Vectori sunt stocați temporar în memorie

### 4.3 Frontend Performance

- Lazy loading pentru imagini
- Minificare CSS custom
- CDN pentru Bootstrap și Chart.js
- Paginare pentru liste lungi (12 produse/pagină)

## 5. Securitate

### Măsuri Implementate

1. **CSRF Protection**: Token-uri pentru toate formularele
2. **SQL Injection**: Django ORM parametrizează query-urile
3. **XSS Prevention**: Template auto-escaping
4. **Authentication**: `@login_required` decorators
5. **Authorization**: Users pot vedea doar propriile comenzi
6. **Password Security**: Django hash-uri cu PBKDF2

### Environment Variables

```python
# settings.py
SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
DATABASE_PASSWORD = env('DATABASE_PASSWORD')
```

## 6. Testing

### Date de Test

Comanda `populate_data` creează:
- 7 utilizatori cu pattern-uri diverse
- 44 produse în 8 categorii
- 25+ comenzi distribute temporal
- 30-50 review-uri realiste
- Categorii asociate bazate pe co-purchases

### Manual Testing Checklist

- [ ] Login/Logout funcționează
- [ ] Căutare returnează rezultate corecte
- [ ] Filtrare după categorie
- [ ] Sortare după preț, rating, dată
- [ ] Adăugare produse în coș
- [ ] Finalizare comandă
- [ ] Export PDF individual
- [ ] Export PDF toate comenzile
- [ ] Recomandări ML apar pentru useri cu comenzi
- [ ] Dashboard afișează statistici corecte
- [ ] Grafic vânzări se randează

## 7. Deployment Considerations

### Production Checklist

```python
# settings.py pentru production
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files
STATIC_ROOT = '/var/www/smartshop/static/'
MEDIA_ROOT = '/var/www/smartshop/media/'
```

### Recommended Stack

- **Web Server**: Nginx
- **WSGI Server**: Gunicorn
- **Database**: PostgreSQL 14+
- **Caching**: Redis (pentru session și query cache)
- **Storage**: AWS S3 (pentru media files)
- **Monitoring**: Sentry (error tracking)

## 8. Future Enhancements

### Planned Features

1. **Advanced ML**:
   - Matrix factorization (SVD)
   - Deep learning with neural networks
   - A/B testing pentru algoritmi

2. **E-Commerce**:
   - Payment gateway integration (Stripe)
   - Email notifications
   - Wishlist functionality
   - Product comparison
   - Advanced search (Elasticsearch)

3. **Analytics**:
   - Google Analytics integration
   - Conversion funnel tracking
   - Heatmaps (Hotjar)

4. **Performance**:
   - Redis caching layer
   - Celery pentru task-uri async
   - CDN pentru static files

---

**Versiune:** 1.0
**Data:** Decembrie 2025
**Autor:** Proiect Comerț Electronic
