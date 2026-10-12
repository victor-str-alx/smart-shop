from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),

    path("product/<slug:slug>/add-to-order/", views.add_to_order, name="add_to_order"),
    path("my-order/", views.my_order, name="my_order"),
    path("checkout/", views.checkout, name="checkout"),
    path("order-history/", views.order_history, name="order_history"),
    path("about-recommender/", views.about_recommender, name="about_recommender"),

    # PDF Export
    path("export-order/<int:order_id>/", views.export_order_pdf, name="export_order_pdf"),
    path("export-all-orders/", views.export_all_orders_pdf, name="export_all_orders_pdf"),

    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
]
