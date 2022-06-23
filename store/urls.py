from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.StoreView.as_view(), name="store"),
    path('cart/', views.CartView.as_view(), name="cart"),
    path('search/', views.SearchView.as_view(), name="search"),
    path('checkout/', views.CheckoutView.as_view(), name="checkout"),
    path('update_item/', views.UpdateItemView.as_view(), name="update_item"),
    path('process_order/', views.ProcessOrderView.as_view(), name="process_order"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.LogOutView.as_view(), name="logout"),
    path('register/', views.RegisterView.as_view(), name="register"),
    path('reset_password/', auth_views.PasswordResetView.as_view(
        template_name="store/password_reset.html"), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(
        template_name="store/password_reset_sent.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="store/password_reset_form.html"), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name="store/password_reset_done.html"), name='password_reset_complete')
]
