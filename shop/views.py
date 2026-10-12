from django.db.models import Avg, Sum, Count, Q
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
import unicodedata
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO

from .models import Product, Category, OrderItem, Rating, Order, Review
from .forms import RatingForm, ReviewForm
from .recommender import (
    get_tfidf_content_recommendations,
    get_collaborative_filtering_recommendations,
    get_hybrid_recommendations
)


def remove_diacritics(text):
    """Remove diacritics from Romanian text for search purposes"""
    if not text:
        return text
    # Normalize to NFD (decomposed form) and remove combining characters
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')


def product_list(request):
    category_slug = request.GET.get("category")
    search_query = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort", "")

    categories = Category.objects.all()
    products = Product.objects.all().select_related("category")

    # Search functionality with diacritics support
    if search_query:
        # Normalize search query (remove diacritics)
        normalized_query = remove_diacritics(search_query.lower())

        # Get all products and filter in Python to handle diacritics
        all_products = list(products)
        matching_ids = []

        for product in all_products:
            # Normalize product fields
            normalized_name = remove_diacritics(product.name.lower())
            normalized_desc = remove_diacritics(product.description.lower())
            normalized_category = remove_diacritics(product.category.name.lower())

            # Check if normalized query matches any normalized field
            if (normalized_query in normalized_name or
                normalized_query in normalized_desc or
                normalized_query in normalized_category):
                matching_ids.append(product.id)

        # Filter products by matching IDs
        products = products.filter(id__in=matching_ids)

    current_category = None
    associated_categories = []

    # filtrare după categorie și calcul "categorii asociate"
    if category_slug:
        products = products.filter(category__slug=category_slug)
        current_category = Category.objects.filter(slug=category_slug).first()

        if current_category:
            # comenzi care conțin produse din categoria curentă
            orders_for_category = (
                Order.objects
                .filter(items__product__category=current_category)
                .distinct()
            )

            # alte categorii care apar în aceleași comenzi
            associated_categories = (
                Category.objects
                .filter(products__order_items__order__in=orders_for_category)
                .exclude(id=current_category.id)
                .annotate(num_together=Count("products__order_items", distinct=True))
                .order_by("-num_together")[:5]
            )

    # Top 5 cele mai vândute produse (global)
    # Only show products that have been sold at least once
    top_sold = (
        Product.objects
        .annotate(total_sold=Sum("order_items__quantity"))
        .filter(total_sold__gt=0)
        .order_by("-total_sold")[:5]
    )

    # Top 5 produse cu rating maxim
    top_rated = (
        Product.objects
        .annotate(avg_rating=Avg("ratings__score"), num_ratings=Count("ratings"))
        .filter(num_ratings__gt=0)
        .order_by("-avg_rating")[:5]
    )

    # Enhanced ML-based recommendations
    personal_recommendations = []
    cf_recommendations = []

    if request.user.is_authenticated and not search_query:
        # Use TF-IDF content-based filtering for personalized recommendations
        personal_recommendations = get_tfidf_content_recommendations(
            request.user,
            top_n=6
        )

        # Use user-based collaborative filtering with cosine similarity
        cf_recommendations = get_collaborative_filtering_recommendations(
            request.user,
            top_n=6
        )

    # Sorting functionality
    if sort_by == "price_asc":
        products = products.order_by("price")
    elif sort_by == "price_desc":
        products = products.order_by("-price")
    elif sort_by == "rating":
        # Sort by average rating (highest first), then by number of ratings
        products = products.annotate(
            avg_rating=Avg("ratings__score"),
            num_ratings=Count("ratings")
        ).order_by("-avg_rating", "-num_ratings")
    elif sort_by == "newest":
        products = products.order_by("-created_at")
    elif sort_by == "name":
        products = products.order_by("name")

    # Pagination - 12 products per page
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page", 1)

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        page_obj = paginator.get_page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        page_obj = paginator.get_page(paginator.num_pages)

    context = {
        "products": page_obj,
        "page_obj": page_obj,
        "categories": categories,
        "selected_category": category_slug,
        "current_category": current_category,
        "associated_categories": associated_categories,
        "top_sold": top_sold,
        "top_rated": top_rated,
        "personal_recommendations": personal_recommendations,
        "cf_recommendations": cf_recommendations,
        "search_query": search_query,
        "sort_by": sort_by,
    }
    return render(request, "shop/product_list.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    # QuerySet de bază pentru produse cumpărate împreună
    base_co_purchased = (
        Product.objects
        .filter(order_items__order__items__product=product)
        .exclude(id=product.id)
        .annotate(times_together=Count("order_items__order", distinct=True))
        .order_by("-times_together")
    )

    # Top 5 produse cumpărate împreună (indiferent de categorie)
    co_purchased = base_co_purchased[:5]

    # Top 5 produse din alte categorii cumpărate împreună
    co_purchased_other_categories = base_co_purchased.exclude(
        category=product.category
    )[:5]

    # Enhanced similar products using TF-IDF on product description
    # First show products from same category, then use content similarity
    similar_products_same_cat = (
        Product.objects
        .filter(category=product.category)
        .exclude(id=product.id)
        .annotate(total_sold=Sum("order_items__quantity"))
        .order_by("-total_sold")[:5]
    )
    similar_products = similar_products_same_cat

    # Statistici rating (media + număr)
    rating_stats = product.ratings.aggregate(
        avg_rating=Avg("score"),
        rating_count=Count("id"),
    )

    user_rating = None
    user_review = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(
            product=product,
            user=request.user
        ).first()
        user_review = Review.objects.filter(
            product=product,
            user=request.user
        ).first()

    # Get all reviews for this product
    reviews = product.reviews.select_related("user").all()

    # Procesare formular rating (quick rating)
    if request.method == "POST" and request.user.is_authenticated:
        if "quick_rating" in request.POST:
            form = RatingForm(request.POST)
            if form.is_valid():
                score = int(form.cleaned_data["score"])
                Rating.objects.update_or_create(
                    product=product,
                    user=request.user,
                    defaults={"score": score},
                )
                return redirect("shop:product_detail", slug=product.slug)
        elif "review_submit" in request.POST:
            review_form = ReviewForm(request.POST, instance=user_review)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                # Also update the quick rating with the review's rating
                Rating.objects.update_or_create(
                    product=product,
                    user=request.user,
                    defaults={"score": review.rating},
                )
                return redirect("shop:product_detail", slug=product.slug)
        else:
            form = RatingForm()
            review_form = ReviewForm()
    else:
        initial = {}
        if user_rating:
            initial["score"] = user_rating.score
        form = RatingForm(initial=initial)

        # Initialize review form
        if user_review:
            review_form = ReviewForm(instance=user_review)
        else:
            review_form = ReviewForm()

    context = {
        "product": product,
        "co_purchased": co_purchased,
        "co_purchased_other_categories": co_purchased_other_categories,
        "similar_products": similar_products,
        "form": form,
        "user_rating": user_rating,
        "avg_rating": rating_stats["avg_rating"],
        "rating_count": rating_stats["rating_count"],
        "review_form": review_form,
        "user_review": user_review,
        "reviews": reviews,
    }
    return render(request, "shop/product_detail.html", context)


@login_required
def about_recommender(request):
    # 1. Comenzile închise ale utilizatorului
    user_orders = Order.objects.filter(user=request.user, is_open=False)

    ordered_items = OrderItem.objects.filter(order__in=user_orders).select_related("product", "order")

    # 2. Produsele deja cumpărate
    ordered_product_ids = ordered_items.values_list("product_id", flat=True).distinct()
    ordered_products = Product.objects.filter(id__in=ordered_product_ids)

    # 3. Categoriile preferate
    favorite_categories = (
        Category.objects
        .filter(products__order_items__order__in=user_orders)
        .annotate(times_ordered=Count("products__order_items"))
        .order_by("-times_ordered")
    )

    favorite_category_ids = favorite_categories.values_list("id", flat=True)

    # 4. Produsele candidate pentru recomandare
    candidate_products = Product.objects.none()
    personal_recommendations = Product.objects.none()

    if favorite_category_ids:
        candidate_products = (
            Product.objects
            .filter(category_id__in=favorite_category_ids)
            .exclude(id__in=ordered_product_ids)
            .annotate(total_sold=Sum("order_items__quantity"))
            .order_by("-total_sold", "name")
        )
        personal_recommendations = candidate_products[:5]

    context = {
        "user_orders": user_orders,
        "ordered_items": ordered_items,
        "ordered_products": ordered_products,
        "favorite_categories": favorite_categories,
        "candidate_products": candidate_products,
        "personal_recommendations": personal_recommendations,
    }
    return render(request, "shop/about_recommender.html", context)

@login_required
def add_to_order(request, slug):
    product = get_object_or_404(Product, slug=slug)

    # luăm sau creăm comanda deschisă a userului
    order, created = Order.objects.get_or_create(
        user=request.user,
        is_open=True,
    )

    # vedem dacă produsul e deja în comanda curentă
    item, item_created = OrderItem.objects.get_or_create(
        order=order,
        product=product,
        defaults={"quantity": 1, "price": product.price},
    )
    if not item_created:
        item.quantity += 1
        item.save()

    return redirect("shop:my_order")


@login_required
def my_order(request):
    order = (
        Order.objects
        .filter(user=request.user, is_open=True)
        .prefetch_related("items__product")
        .first()
    )

    return render(request, "shop/my_order.html", {"order": order})


@login_required
def checkout(request):
    order = (
        Order.objects
        .filter(user=request.user, is_open=True)
        .first()
    )
    if order:
        order.is_open = False
        order.save()
    return redirect("shop:product_list")


@login_required
def order_history(request):
    # Get all completed orders for the current user, newest first
    orders = (
        Order.objects
        .filter(user=request.user, is_open=False)
        .prefetch_related("items__product")
        .order_by("-created_at")
    )

    # Check if user has an open order (for "View Cart" button)
    has_open_order = Order.objects.filter(user=request.user, is_open=True).exists()

    context = {
        "orders": orders,
        "has_open_order": has_open_order,
    }
    return render(request, "shop/order_history.html", context)


@login_required
def export_order_pdf(request, order_id):
    """Export a specific order to PDF"""
    order = get_object_or_404(Order, id=order_id, user=request.user, is_open=False)

    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)

    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#764ba2'),
        spaceAfter=12
    )

    # Title
    elements.append(Paragraph("SmartShop - Factura Comanda", title_style))
    elements.append(Spacer(1, 0.5*cm))

    # Order Info
    elements.append(Paragraph(f"<b>Comanda #{order.id}</b>", heading_style))
    order_info = [
        ['Data comenzii:', order.created_at.strftime('%d/%m/%Y %H:%M')],
        ['Client:', f"{order.user.get_full_name() or order.user.username}"],
        ['Email:', order.user.email],
    ]

    order_table = Table(order_info, colWidths=[4*cm, 12*cm])
    order_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(order_table)
    elements.append(Spacer(1, 1*cm))

    # Products table
    elements.append(Paragraph("<b>Produse Comandate</b>", heading_style))

    # Table header
    data = [['Produs', 'Pret Unitar', 'Cantitate', 'Subtotal']]

    # Table rows
    for item in order.items.all():
        data.append([
            item.product.name,
            f"{item.price} RON",
            str(item.quantity),
            f"{item.subtotal} RON"
        ])

    # Total row
    data.append(['', '', 'TOTAL:', f"{order.total_amount} RON"])

    # Create table
    products_table = Table(data, colWidths=[8*cm, 3*cm, 3*cm, 3*cm])
    products_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

        # Body
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 1), (-1, -2), 8),
        ('TOPPADDING', (0, 1), (-1, -2), 8),

        # Total row
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e7f7ff')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('TOPPADDING', (0, -1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#667eea')),
    ]))

    elements.append(products_table)
    elements.append(Spacer(1, 1.5*cm))

    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph("Multumim pentru comanda! - SmartShop", footer_style))
    elements.append(Paragraph("www.smartshop.ro | contact@smartshop.ro", footer_style))

    # Build PDF
    doc.build(elements)

    # Get PDF from buffer
    pdf = buffer.getvalue()
    buffer.close()

    # Return PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="comanda_{order.id}.pdf"'
    response.write(pdf)

    return response


@login_required
def export_all_orders_pdf(request):
    """Export all user orders to a single PDF"""
    orders = Order.objects.filter(user=request.user, is_open=False).prefetch_related('items__product').order_by('-created_at')

    if not orders.exists():
        return HttpResponse("Nu ai comenzi de exportat.", status=404)

    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)

    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#764ba2'),
        spaceAfter=12
    )

    # Title
    elements.append(Paragraph("SmartShop - Istoricul Comenzilor", title_style))
    elements.append(Paragraph(f"Client: {request.user.get_full_name() or request.user.username}", styles['Normal']))
    elements.append(Spacer(1, 1*cm))

    # Add each order
    for order in orders:
        elements.append(Paragraph(f"<b>Comanda #{order.id}</b> - {order.created_at.strftime('%d/%m/%Y %H:%M')}", heading_style))

        # Products table
        data = [['Produs', 'Cantitate', 'Subtotal']]

        for item in order.items.all():
            data.append([
                item.product.name,
                str(item.quantity),
                f"{item.subtotal} RON"
            ])

        data.append(['TOTAL:', '', f"{order.total_amount} RON"])

        order_table = Table(data, colWidths=[10*cm, 3*cm, 4*cm])
        order_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e7f7ff')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#667eea')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(order_table)
        elements.append(Spacer(1, 0.8*cm))

    # Build PDF
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="toate_comenzile_{request.user.username}.pdf"'
    response.write(pdf)

    return response


@login_required
def dashboard(request):
    """Admin/User dashboard with statistics"""
    from django.db.models import Sum, Count, Avg
    from django.db.models.functions import TruncDate
    from datetime import timedelta
    from django.utils import timezone

    # User statistics
    user_orders = Order.objects.filter(user=request.user, is_open=False)
    user_stats = {
        'total_orders': user_orders.count(),
        'total_spent': user_orders.aggregate(total=Sum('items__price'))['total'] or 0,
        'total_products': OrderItem.objects.filter(order__in=user_orders).aggregate(total=Sum('quantity'))['total'] or 0,
    }

    # Recent orders
    recent_orders = user_orders.order_by('-created_at')[:5]

    # User's favorite category (most purchased)
    favorite_category = (
        Category.objects
        .filter(products__order_items__order__in=user_orders)
        .annotate(purchase_count=Count('products__order_items'))
        .order_by('-purchase_count')
        .first()
    )

    # Overall shop statistics (visible to all users)
    shop_stats = {
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_reviews': Review.objects.count(),
        'avg_rating': Rating.objects.aggregate(avg=Avg('score'))['avg'] or 0,
    }

    # Most popular products (top 5)
    popular_products = (
        Product.objects
        .annotate(total_sold=Sum('order_items__quantity'))
        .filter(total_sold__gt=0)
        .order_by('-total_sold')[:5]
    )

    # Best rated products (top 5)
    best_rated = (
        Product.objects
        .annotate(
            avg_rating=Avg('ratings__score'),
            num_ratings=Count('ratings')
        )
        .filter(num_ratings__gte=2)
        .order_by('-avg_rating')[:5]
    )

    # Sales trend - last 7 days
    last_7_days = timezone.now() - timedelta(days=7)
    daily_sales = (
        Order.objects
        .filter(is_open=False, created_at__gte=last_7_days)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(
            orders_count=Count('id'),
            revenue=Sum('items__price')
        )
        .order_by('date')
    )

    context = {
        'user_stats': user_stats,
        'recent_orders': recent_orders,
        'favorite_category': favorite_category,
        'shop_stats': shop_stats,
        'popular_products': popular_products,
        'best_rated': best_rated,
        'daily_sales': list(daily_sales),
    }

    return render(request, 'shop/dashboard.html', context)
