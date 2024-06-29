from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import logout
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.utils.timezone import make_aware
from django.db.models import Count, Q
from datetime import datetime, timedelta
from geopy.distance import geodesic
from deepface import DeepFace
import os
from .models import Account, Attendance_Form, Attendance_Mark, Student, Subject, SubjectEnrollment, Face, Lecturer, Class
from .forms import SelectSubjectForm



def student_dashboard(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')

    student = get_object_or_404(Student, pk=student_id)
    subjects = student.subject_set.all()

    return render(request, 'attendance/student_dashboard.html', {'subjects': subjects})

def student_attendance(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')

    student = get_object_or_404(Student, pk=student_id)
    selected_subject_id = request.GET.get('subject')
    attendance_marks = Attendance_Mark.objects.filter(Student_ID=student)
    
    if selected_subject_id:
        attendance_marks = attendance_marks.filter(Attendance_Form_ID__Subject_ID=selected_subject_id)
        total_forms = Attendance_Form.objects.filter(Subject_ID=selected_subject_id, attendance_mark__Student_ID=student).distinct().count()
    else:
        total_forms = Attendance_Form.objects.filter(attendance_mark__Student_ID=student).distinct().count()
    
    total_attendance = attendance_marks.filter(Status_Attendance=True).count()

    # Sửa lại điều kiện kiểm tra đủ điều kiện thi
    if selected_subject_id:
        if total_forms < 3:
            exam_eligibility_message = "Chưa Đủ Phiếu Điểm Danh Nên Không Thể Kiểm Tra"
            allowed_to_take_exam = False
        else:
            # Đếm số buổi đi học mà sinh viên đã đi trễ
            total_late_attendance = attendance_marks.filter(Status_Attendance=True, Time_Late=True).count()
            if total_attendance < 2 or total_late_attendance > 3:
                exam_eligibility_message = "Sinh Viên Đã Vắng Quá Số Buổi Quy Định Hoặc Đi Trễ Quá 3 Buổi"
                allowed_to_take_exam = False
            else:
                exam_eligibility_message = "Đủ Điều Kiện Thi"
                allowed_to_take_exam = True
    else:
        exam_eligibility_message = None
        allowed_to_take_exam = None

    subjects = Subject.objects.all()
    selected_subject_name = subjects.get(pk=selected_subject_id).Subject_Name if selected_subject_id else None

    if request.method == 'POST' and 'check_exam' in request.POST:
        return render(request, 'attendance/student_attendance.html', {
            'attendance_marks': attendance_marks,
            'allowed_to_take_exam': allowed_to_take_exam,
            'check_exam_result': True,
            'subjects': subjects,
            'selected_subject_id': selected_subject_id,
            'selected_subject_name': selected_subject_name,
            'exam_eligibility_message': exam_eligibility_message,
        })
    
    return render(request, 'attendance/student_attendance.html', {
        'attendance_marks': attendance_marks,
        'subjects': subjects,
        'selected_subject_id': selected_subject_id,
        'selected_subject_name': selected_subject_name,
        'exam_eligibility_message': exam_eligibility_message,
    })



def logout_view(request):
    logout(request)
    return redirect('login')

def create_attendance_form(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        moment = request.POST.get('moment')
        status = request.POST.get('status')
        subject_id = request.POST.get('subject')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        radius = request.POST.get('radius')

        try:
            subject = Subject.objects.get(pk=subject_id)
            
            # Create Attendance_Form
            attendance_form = Attendance_Form.objects.create(
                Date=date,
                Moment=moment,
                Status=status,
                Latitude=latitude,
                Longitude=longitude,
                Radius=radius,
                Time_Create=timezone.now(),
                Subject_ID=subject,
            )
            
            # Get enrolled students for the subject
            subject_enrollments = SubjectEnrollment.objects.filter(Subject=subject)
            
            # Create Attendance_Mark for each enrolled student
            for enrollment in subject_enrollments:
                student = enrollment.Student
                face = student.face_set.first()  # Get the first face of the student
                
                # Create Attendance_Mark
                Attendance_Mark.objects.create(
                    Status_Attendance=False,
                    Time_Late=False,
                    Attendance_Form_ID=attendance_form,  # Use the Attendance_Form instance
                    Student_ID=student,
                    Face_ID=face,
                )
            
            # Success message
            messages.success(request, 'Đã tạo form điểm danh thành công.')
            return redirect('create_attendance_form')
        
        except Subject.DoesNotExist:
            # Error message if subject does not exist
            messages.error(request, 'Môn học không tồn tại.')
    
    # Fetch all subjects for the form
    subjects = Subject.objects.all()
    return render(request, 'attendance/create_attendance_form.html', {'subjects': subjects})

def lecturer_dashboard(request):
    return render(request, 'attendance/lecturer_dashboard.html')

def select_subject(request):
    message = None
    if request.method == 'POST':
        form = SelectSubjectForm(request.POST)
        if form.is_valid():
            subject_id = form.cleaned_data['subject'].pk

            # Lấy phiếu điểm danh mới nhất của môn học vừa tạo dựa trên Date và Time_Create
            latest_form = Attendance_Form.objects.filter(Subject_ID=subject_id).order_by('-Date', '-Time_Create').first()
            
            if not latest_form:
                message = "Chưa có form điểm danh nào khả dụng cho môn học này."
            else:
                return redirect('mark_attendance', attendance_form_id=latest_form.Attendance_Form_ID)
    else:
        form = SelectSubjectForm()
    
    return render(request, 'attendance/select_subject.html', {'form': form, 'message': message})

def select_subject(request):
    message = None
    if request.method == 'POST':
        form = SelectSubjectForm(request.POST)
        if form.is_valid():
            subject_id = form.cleaned_data['subject'].pk

            # Lấy phiếu điểm danh mới nhất của môn học vừa tạo dựa trên Date và Time_Create
            latest_form = Attendance_Form.objects.filter(Subject_ID=subject_id).order_by('-Date', '-Time_Create').first()
            
            if not latest_form:
                message = "Chưa có form điểm danh nào khả dụng cho môn học này."
            else:
                return redirect('mark_attendance', attendance_form_id=latest_form.Attendance_Form_ID)
    else:
        form = SelectSubjectForm()
    
    return render(request, 'attendance/select_subject.html', {'form': form, 'message': message})



def mark_attendance(request, attendance_form_id):
    attendance_form = get_object_or_404(Attendance_Form, pk=attendance_form_id)
    student_id = request.session.get('student_id')
    if not student_id:
        return JsonResponse({'success': False, 'message': "Bạn cần đăng nhập để điểm danh."})

    student = get_object_or_404(Student, pk=student_id)
    
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        image = request.FILES.get('image')

        if not latitude or not longitude:
            return JsonResponse({'success': False, 'message': "Vị trí của bạn không được xác định."})

        latitude = float(latitude)
        longitude = float(longitude)

        # Kiểm tra khoảng cách giữa sinh viên và vị trí điểm danh
        student_location = (latitude, longitude)
        form_location = (attendance_form.Latitude, attendance_form.Longitude)
        distance = geodesic(student_location, form_location).meters

        if distance > attendance_form.Radius:
            return JsonResponse({'success': False, 'message': "Bạn cần đứng gần vị trí điểm danh để điểm danh."})

        # Lưu trữ hình ảnh tạm thời
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        image_path = os.path.join(temp_dir, image.name)
        with open(image_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        # So sánh khuôn mặt
        face = Face.objects.filter(Student_ID=student).first()
        if not face:
            return JsonResponse({'success': False, 'message': "Không tìm thấy khuôn mặt của sinh viên."})

        try:
            result = DeepFace.verify(img1_path=image_path, img2_path=face.Face_Img.path, model_name='VGG-Face')
            if result["verified"]:
                # Cập nhật trạng thái điểm danh
                current_time = timezone.now()
                attendance_mark, created = Attendance_Mark.objects.get_or_create(
                    Student_ID=student, 
                    Attendance_Form_ID=attendance_form,
                    defaults={'Face_ID': face, 'Status_Attendance': True, 'Time_Attendance': current_time, 'Time_Late': False}
                )
                if not created:
                    attendance_mark.Status_Attendance = True
                    attendance_mark.Time_Attendance = current_time

                # Sử dụng trực tiếp Time_Create của attendance_form
                time_create = attendance_form.Time_Create

                # Kiểm tra thời gian điểm danh
                time_difference = current_time - time_create

                if time_difference.total_seconds() > 300:  # 300 giây = 5 phút
                    attendance_mark.Time_Late = True
                else:
                    attendance_mark.Time_Late = False
                attendance_mark.save()

                # Chuẩn bị thông điệp trả về
                message = f"Điểm danh thành công vào lúc {attendance_mark.Time_Attendance.strftime('%H:%M:%S')}."
                if attendance_mark.Time_Late:
                    message += " Bạn đã điểm danh trễ."
                
                return JsonResponse({'success': True, 'message': message})
            else:
                return JsonResponse({'success': False, 'message': "Điểm danh không thành công. Khuôn mặt không khớp."})
        finally:
            os.remove(image_path)
    else:
        return render(request, 'attendance/mark_attendance.html', {'attendance_form': attendance_form})
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            account = Account.objects.get(Username=username, Password=password)
            if account.Student_ID:
                request.session['student_id'] = account.Student_ID.pk
                return redirect('student_dashboard')
            elif account.Lecturer_ID:
                request.session['lecturer_id'] = account.Lecturer_ID.pk  # Lưu lecturer_id vào session
                return redirect('lecturer_dashboard')
        except Account.DoesNotExist:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng!')
    return render(request, 'attendance/login.html')

def lecturer_subjects(request):
    lecturer_id = request.session.get('lecturer_id')  # Lấy lecturer_id từ session
    if not lecturer_id:
        return redirect('login')  # Nếu không có session, chuyển hướng đến trang login
    
    lecturer = get_object_or_404(Lecturer, pk=lecturer_id)  # Lấy đối tượng Lecturer từ primary key
    
    # Lấy tất cả các môn học mà giảng viên này dạy
    subjects_taught = Subject.objects.filter(Lecturer_ID=lecturer)
    
    # Duyệt qua từng môn học để lấy danh sách sinh viên trong mỗi môn học và lớp học tương ứng
    subject_data = []
    for subject in subjects_taught:
        enrolled_students = Student.objects.filter(subjectenrollment__Subject=subject)
        subject_info = {
            'subject_name': subject.Subject_Name,
            'class_name': subject.Class_ID.Class_Name,  # Lấy tên lớp học từ Class_ID
            'enrolled_students': enrolled_students,
        }
        subject_data.append(subject_info)
    
    return render(request, 'attendance/lecturer_subjects.html', {'subject_data': subject_data})


