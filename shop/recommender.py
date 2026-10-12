"""
Advanced recommendation algorithms using machine learning techniques.
"""
from django.db.models import Count, Avg, Q
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .models import Product, Order, OrderItem, Rating


def get_tfidf_content_recommendations(user, excluded_product_ids=None, top_n=6):
    """
    Content-based recommendations using TF-IDF on product descriptions.
    Analyzes text similarity between products the user has purchased and all other products.

    Args:
        user: The user to generate recommendations for
        excluded_product_ids: List of product IDs to exclude from recommendations
        top_n: Number of recommendations to return

    Returns:
        QuerySet of recommended products
    """
    if not user.is_authenticated:
        return Product.objects.none()

    # Get products the user has purchased
    user_products = Product.objects.filter(
        order_items__order__user=user,
        order_items__order__is_open=False
    ).distinct()

    if not user_products.exists():
        return Product.objects.none()

    # Get all products with descriptions
    all_products = Product.objects.filter(
        description__isnull=False
    ).exclude(description__exact='')

    if excluded_product_ids:
        all_products = all_products.exclude(id__in=excluded_product_ids)

    # Exclude products the user has already purchased
    all_products = all_products.exclude(
        id__in=user_products.values_list('id', flat=True)
    )

    if not all_products.exists():
        return Product.objects.none()

    # Combine all products for TF-IDF
    all_product_list = list(user_products) + list(all_products)

    # Create text corpus: combine name, description, and category
    corpus = []
    for product in all_product_list:
        text = f"{product.name} {product.description} {product.category.name}"
        corpus.append(text)

    # Calculate TF-IDF vectors
    vectorizer = TfidfVectorizer(
        max_features=100,
        stop_words='english',
        ngram_range=(1, 2)
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        # Not enough data to generate recommendations
        return Product.objects.none()

    # Calculate cosine similarity
    user_products_count = user_products.count()
    user_vectors = tfidf_matrix[:user_products_count]
    candidate_vectors = tfidf_matrix[user_products_count:]

    # Calculate similarity scores (average similarity to all user products)
    similarity_scores = cosine_similarity(candidate_vectors, user_vectors)
    avg_similarity = similarity_scores.mean(axis=1)

    # Get top N product indices
    top_indices = avg_similarity.argsort()[-top_n:][::-1]

    # Convert QuerySet to list for indexing
    all_products_list = list(all_products)

    # Map back to product IDs (convert numpy int64 to Python int)
    recommended_product_ids = [all_products_list[int(i)].id for i in top_indices]

    # Return products in the order of recommendation scores
    preserved_order = {pk: i for i, pk in enumerate(recommended_product_ids)}
    recommended_products = Product.objects.filter(id__in=recommended_product_ids)

    return sorted(recommended_products, key=lambda p: preserved_order[p.id])


def get_collaborative_filtering_recommendations(user, excluded_product_ids=None, top_n=6):
    """
    User-based collaborative filtering using cosine similarity.
    Finds similar users and recommends products they've purchased.

    Args:
        user: The user to generate recommendations for
        excluded_product_ids: List of product IDs to exclude from recommendations
        top_n: Number of recommendations to return

    Returns:
        QuerySet of recommended products
    """
    if not user.is_authenticated:
        return Product.objects.none()

    # Get user's purchased products
    user_purchased = set(
        Product.objects.filter(
            order_items__order__user=user,
            order_items__order__is_open=False
        ).values_list('id', flat=True)
    )

    if not user_purchased:
        return Product.objects.none()

    # Get all products
    all_products = list(Product.objects.values_list('id', flat=True))
    product_id_to_idx = {pid: idx for idx, pid in enumerate(all_products)}

    # Get all users who have made purchases
    users_with_orders = set(
        Order.objects.filter(is_open=False).values_list('user_id', flat=True)
    )

    if len(users_with_orders) < 2:
        return Product.objects.none()

    # Build user-item matrix
    user_list = list(users_with_orders)
    user_id_to_idx = {uid: idx for idx, uid in enumerate(user_list)}

    # Create matrix: users x products
    matrix = np.zeros((len(user_list), len(all_products)))

    # Fill matrix with purchase data
    order_items = OrderItem.objects.filter(
        order__is_open=False,
        order__user_id__in=users_with_orders
    ).values('order__user_id', 'product_id')

    for item in order_items:
        user_idx = user_id_to_idx[item['order__user_id']]
        product_idx = product_id_to_idx[item['product_id']]
        matrix[user_idx, product_idx] = 1

    # Get current user's index
    if user.id not in user_id_to_idx:
        return Product.objects.none()

    current_user_idx = user_id_to_idx[user.id]
    current_user_vector = matrix[current_user_idx].reshape(1, -1)

    # Calculate cosine similarity with all other users
    similarities = cosine_similarity(current_user_vector, matrix)[0]
    similarities[current_user_idx] = -1  # Exclude self

    # Get top 5 similar users
    similar_user_indices = similarities.argsort()[-5:][::-1]

    # Aggregate products from similar users
    product_scores = {}
    for user_idx in similar_user_indices:
        similarity_score = similarities[user_idx]
        if similarity_score <= 0:
            continue

        # Get products this similar user has purchased
        for product_idx, purchased in enumerate(matrix[user_idx]):
            if purchased == 1:
                product_id = all_products[product_idx]
                # Skip products current user already has
                if product_id not in user_purchased:
                    product_scores[product_id] = product_scores.get(product_id, 0) + similarity_score

    if not product_scores:
        return Product.objects.none()

    # Sort by score and get top N
    sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)
    recommended_product_ids = [pid for pid, _ in sorted_products[:top_n]]

    if excluded_product_ids:
        recommended_product_ids = [
            pid for pid in recommended_product_ids
            if pid not in excluded_product_ids
        ]

    # Return products in recommendation order
    preserved_order = {pk: i for i, pk in enumerate(recommended_product_ids)}
    recommended_products = Product.objects.filter(id__in=recommended_product_ids)

    return sorted(recommended_products, key=lambda p: preserved_order[p.id])


def get_hybrid_recommendations(user, top_n=6):
    """
    Hybrid recommendation system combining multiple approaches.
    Combines TF-IDF content-based, collaborative filtering, and popularity.

    Args:
        user: The user to generate recommendations for
        top_n: Number of recommendations to return

    Returns:
        Dictionary with 'content_based' and 'collaborative' recommendations
    """
    content_recs = get_tfidf_content_recommendations(user, top_n=top_n)
    collaborative_recs = get_collaborative_filtering_recommendations(user, top_n=top_n)

    return {
        'content_based': content_recs,
        'collaborative': collaborative_recs
    }


def get_popular_products(category=None, top_n=5):
    """
    Get popular products based on sales and ratings.

    Args:
        category: Optional category to filter by
        top_n: Number of products to return

    Returns:
        QuerySet of popular products
    """
    products = Product.objects.annotate(
        total_sold=Count('orderitem'),
        avg_rating=Avg('ratings__score')
    )

    if category:
        products = products.filter(category=category)

    # Combine sales and rating for popularity score
    # Products with sales get priority, then rating as tiebreaker
    products = products.filter(total_sold__gt=0).order_by('-total_sold', '-avg_rating')

    return products[:top_n]
