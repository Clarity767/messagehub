from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('notes/', views.notes_view, name='notes'),
    path('notes/<int:note_id>/toggle', views.note_toogle, name='note_toggle'),
    path('notes/<int:note_id>/delete', views.note_delete, name='note_delete'),
    path('messages/', views.masseges_inbox, name='masseges_inbox'),
    path('messages/<int:message_id>/', views.messsage_read, name='message_read'),
]