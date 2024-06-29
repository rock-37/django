from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='home'),
    path('login/', views.login, name='login'),
    path('lecturer_dashboard/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('create_attendance_form/', views.create_attendance_form, name='create_attendance_form'),
    path('student_attendance/', views.student_attendance, name='student_attendance'),
    path('logout/', views.logout_view, name='logout'),
    path('select_subject/', views.select_subject, name='select_subject'),
    path('mark_attendance/<int:attendance_form_id>/', views.mark_attendance, name='mark_attendance'),
    path('lecturer_subjects/', views.lecturer_subjects, name='lecturer_subjects'),

]


    
    
