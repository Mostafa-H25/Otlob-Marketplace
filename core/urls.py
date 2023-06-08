from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),

    path('browse/', views.BrowseView.as_view(), name='browse'),




    path('category/create/', views.CategoryCreateView.as_view(),
         name='category_create'),

    path('category/<slug:slug>/',
         views.CategoryDetailView.as_view(), name='category_detail'),

    path('category/<slug:slug>/delete/',
         views.CategoryDeleteView.as_view(), name='category_delete'),

    path('category/<slug:slug>/update/',
         views.CategoryUpdateView.as_view(), name='category_update'),

    path('category/', views.CategoryListView.as_view(), name='categories'),

    path('sub-category/create/', views.SubcategoryCreateView.as_view(),
         name='subcategory_create'),

    path('sub-category/<slug:slug>/delete/',
         views.SubcategoryDeleteView.as_view(), name='subcategory_delete'),

    path('sub-category/<slug:slug>/update/',
         views.SubcategoryUpdateView.as_view(), name='subcategory_update'),

    path('sub-category/<slug:slug>',
         views.SubcategoryDetailView.as_view(), name='subcategory_detail'),

    #     path('sub-category/',
    #          views.SubcategoryListView.as_view(), name='subcategories'),

    path('brand/add/', views.BrandCreateView.as_view(), name='brand_add'),

    path('brand/<slug:slug>/delete',
         views.BrandDeleteView.as_view(), name='brand_delete'),

    path('brand/<slug:slug>/update/',
         views.BrandUpdateView.as_view(), name='brand_update'),

    #     path('brand/', views.BrandListView.as_view(), name='brands'),







    path('coupon/use/', views.UseCouponView.as_view(), name='coupon_use'),

    path('coupon/<uuid:pk>/update',
         views.CouponUpdateView.as_view(), name='coupon_update'),

    path('coupon/', views.CouponListView.as_view(), name='coupons'),

    path('coupon/create/', views.CouponCreateView.as_view(), name='coupon_create'),

    path('product/<slug:slug>/add_to_cart/',
         views.add_to_cart, name='add_to_cart'),

    path('product/<slug:slug>/delete/',
         views.ItemDeleteView.as_view(), name='product_delete'),

    path('product/<slug:slug>/update/',
         views.ItemUpdateView.as_view(), name='product_update'),

    path('product/create/', views.ItemCreateView.as_view(), name='product_create'),

    path('product/<slug:slug>/', views.ItemDetailView.as_view(), name='product'),

    path('order-summary/<uuid:pk>/delete/',
         views.delete_order, name='order_delete'),

    path('delete-item/<slug:slug>/',
         views.delete_order_item, name='item_delete'),

    path('increase-item/<slug:slug>/',
         views.increase_order_item, name='item_increase'),

    path('decrease-item/<slug:slug>/',
         views.decrease_order_item, name='item_decrease'),

    path('order-summary/',
         views.OrderSummaryView.as_view(), name='order_summary'),

    path('checkout/<uuid:pk>/', views.CheckoutView.as_view(), name='checkout'),

    path('payment/<payment_method>/', views.PaymentView.as_view(), name='payment'),

    path('create-checkout-session/',
         views.CreateCheckoutSessionView.as_view(), name='checkout_create'),

    path('success/',
         views.SuccessView.as_view(), name='payment_success'),

    path('cancel/',
         views.CancelView.as_view(), name='payment_cancel'),

    path('orders/', views.OrderFollowupView.as_view(), name='order_followup'),

    #     path('create-stripe-account',
    #          views.StripeAccountView.as_view(), name='create-stripe'),
]
