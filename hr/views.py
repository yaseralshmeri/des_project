from rest_framework import viewsets
from .models import Employee, Teacher, EmployeeAttendance, Leave, Salary
from .serializers import (EmployeeSerializer, TeacherSerializer, AttendanceSerializer,
                          LeaveSerializer, SalarySerializer)
from students.permissions import IsAdminOrStaff

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAdminOrStaff]

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAdminOrStaff]

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = EmployeeAttendance.objects.all()

    serializer_class = AttendanceSerializer
    permission_classes = [IsAdminOrStaff]

class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    permission_classes = [IsAdminOrStaff]

class SalaryViewSet(viewsets.ModelViewSet):
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer
    permission_classes = [IsAdminOrStaff]
