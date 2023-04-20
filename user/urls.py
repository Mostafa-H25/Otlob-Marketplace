from django.urls import path

from django.contrib.auth import views as auth_views
from . import views

app_name = 'auth'

urlpatterns = [
    path('register/', views.register, name='register'),

    path('login/', views.UpdatedLoginView.as_view(), name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='user/password_change.html'), name='password_change'),

    path('password-change/done', auth_views.PasswordChangeDoneView.as_view(
        template_name='user/password_change_done.html'), name='password_change_done'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='user/password_reset.html'), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='user/password_reset_done.html'), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),

    path('reset/done', auth_views.PasswordResetCompleteView.as_view(
        template_name='user/reset_done.html'), name='password_reset_complete'),

    path('profile/<slug:slug>/',
         views.UserProfileView.as_view(), name='profile'),

    path('profile/<slug:slug>/update',
         views.profile_update, name='profile_update'),

    path('profile/<int:pk>/delete',
         views.UserDeleteView.as_view(), name='profile_delete'),

    path('inbox/', views.InboxView.as_view(), name='inbox'),

    path('conversation/<slug:slug>/create', views.create_conversation,
         name='conversation_create'),

    path('conversation/<uuid:pk>',
         views.ConversationView.as_view(), name='conversation'),
]
