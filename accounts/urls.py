from accounts import views
from django.contrib.auth import views as auth_views
from django.urls import path
#from django.conf import settings
#from django.conf.urls.static import static


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name="accounts/login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name="accounts/logout.html"), name='logout'),
    path('register/', views.register, name='register'),
    path('edit/', views.edit, name="edit"),
    path('password-change/',
         auth_views.PasswordChangeView.as_view(template_name="accounts/password_change_form.html"),
         name='password_change'),
    path('password-change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name="accounts/password_change_done.html"),
         name='password_change_done'),
    path('pwd-reset/',
         auth_views.PasswordResetView.as_view(template_name="accounts/password_reset_form.html", html_email_template_name="accounts/password_reset_email.html"),
         name='password_reset'),
    path('pwd-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_confirm.html"),
         name='password_reset_done'),
    path('pwd-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm_done.html"),
         name='password_reset_confirm'),
    path('pwd-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"),
         name='password_reset_complete'),
]

#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
