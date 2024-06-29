from django.contrib import admin
from .models import Student, Lecturer, Account, Class, Subject, Face, Attendance_Form, Attendance_Mark, SubjectEnrollment

admin.site.register(Student)
admin.site.register(Lecturer)
admin.site.register(Account)
admin.site.register(Class)
admin.site.register(Subject)
admin.site.register(Face)
admin.site.register(Attendance_Form)
admin.site.register(Attendance_Mark)
admin.site.register(SubjectEnrollment)