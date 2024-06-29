from django.db import models

class Student(models.Model):
    Student_ID = models.AutoField(primary_key=True)
    Name_Student = models.CharField(max_length=100)
    Email = models.EmailField()
    Birthday = models.DateField()

    def __str__(self):
        return self.Name_Student

class Lecturer(models.Model):
    Lecturer_ID = models.AutoField(primary_key=True)
    Name_Lecturer = models.CharField(max_length=100)
    Email = models.EmailField()
    Birthday = models.DateField()

    def __str__(self):
        return self.Name_Lecturer

class Account(models.Model):
    Account_ID = models.AutoField(primary_key=True)
    Username = models.CharField(max_length=100)
    Password = models.CharField(max_length=100)
    Student_ID = models.ForeignKey(Student, null=True, blank=True, on_delete=models.SET_NULL)
    Lecturer_ID = models.ForeignKey(Lecturer, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.Username

class Class(models.Model):
    Class_ID = models.AutoField(primary_key=True)
    Class_Name = models.CharField(max_length=100)

    def __str__(self):
        return self.Class_Name

class Subject(models.Model):
    Subject_ID = models.AutoField(primary_key=True)
    Subject_Name = models.CharField(max_length=100)
    Students = models.ManyToManyField(Student, through='SubjectEnrollment')
    Class_ID = models.ForeignKey(Class, on_delete=models.CASCADE)
    Lecturer_ID = models.ForeignKey(Lecturer, on_delete=models.CASCADE)

    def __str__(self):
        return self.Subject_Name

class SubjectEnrollment(models.Model):
    Student = models.ForeignKey(Student, on_delete=models.CASCADE)
    Subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

class Face(models.Model):
    Face_ID = models.AutoField(primary_key=True)
    Face_Name = models.CharField(max_length=100)
    Face_Img = models.ImageField(upload_to='faces/')
    Student_ID = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return self.Face_Name

class Attendance_Form(models.Model):
    Attendance_Form_ID = models.AutoField(primary_key=True)
    Date = models.DateField()
    Moment = models.CharField(max_length=50)
    Status = models.CharField(max_length=50)
    Latitude=models.DecimalField(max_digits=19,decimal_places=15,default=0)
    Longitude=models.DecimalField(max_digits=19,decimal_places=15,default=0)
    Radius = models.IntegerField(default=0,)
    Time_Create=models.DateTimeField(auto_now_add=True)
    Subject_ID = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self):
        time_create_str = self.Time_Create.strftime("%H:%M:%S")
        return f"{self.Date} - {self.Moment} - {self.Status} - {time_create_str}"
    
class Attendance_Mark(models.Model):
    Attendance_Mark_ID = models.AutoField(primary_key=True)
    Status_Attendance = models.BooleanField()
    Time_Late = models.BooleanField()
    Time_Attendance=models.DateTimeField(auto_now_add=True)
    Student_ID = models.ForeignKey(Student, on_delete=models.CASCADE)
    Face_ID = models.ForeignKey(Face, on_delete=models.CASCADE)
    Attendance_Form_ID = models.ForeignKey(Attendance_Form, on_delete=models.CASCADE)

    def __str__(self):
        time_attendance_str = self.Time_Attendance.strftime("%H:%M:%S")
        return f"Attendance {self.Attendance_Mark_ID} - {self.Status_Attendance} - {time_attendance_str} - {self.Time_Late}"