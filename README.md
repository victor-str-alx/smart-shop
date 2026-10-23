# Smart Shop — E-commerce Platform with Machine Learning Recommendations

## Overview

Smart Shop is a Django e-commerce application backed by PostgreSQL. It combines standard online shopping workflows with a hybrid product recommendation system and a sales analytics dashboard.

The project is particularly relevant to a data-oriented portfolio because it brings together structured business data, product interactions, recommendations, and visual reporting.

## Main Features

- Product catalogue with categories, search, and filtering
- Shopping cart and order management
- Product reviews and ratings
- Personalised product recommendations
- Sales analytics dashboard
- PDF invoice generation
- User accounts and authentication

## Technology Stack

| Area | Technologies |
|---|---|
| Backend | Python, Django 5.2.8 |
| Database | PostgreSQL |
| Recommendation system | scikit-learn, NumPy |
| Frontend | HTML, CSS, JavaScript, Bootstrap 5.3.3 |
| Visualisation | Chart.js 4.4.0 |
| PDF generation | ReportLab |
| Image processing | Pillow |

## Recommendation Approach

The project describes a hybrid recommendation approach combining:

- **Content-based filtering**, using product text representations with TF-IDF and cosine similarity.
- **User-based collaborative filtering**, using patterns in user preferences and interactions.
- **Weighted combination**, with the described design assigning 60% to content-based filtering and 40% to collaborative filtering.

Recommendation quality depends on the data available and how the system is evaluated; the weights alone do not establish model performance.

## Data Analytics Perspective

E-commerce data can help explore questions such as product performance, order trends, customer feedback, and recommendation behaviour. The repository also describes an analytics dashboard. Specific findings should only be reported after reviewing actual dashboard calculations and the data they use.

## Architecture

The application follows Django's Model-View-Template (MVT) pattern. Django models define data structures, views handle requests and application logic, templates render the interface, and PostgreSQL stores application records.

## Project Value

Smart Shop demonstrates a combination of application development, relational data, visual reporting, and recommendation concepts. It is a useful bridge between my existing software background and my developing interest in data analysis.
