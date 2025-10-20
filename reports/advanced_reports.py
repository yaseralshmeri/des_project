"""
Advanced Reporting System for University Management System
نظام التقارير المتقدم لنظام إدارة الجامعة
"""

import os
import io
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Sum, Q
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import xlsxwriter
from io import BytesIO
import base64
import logging

# تجنب تحذيرات matplotlib
import matplotlib
matplotlib.use('Agg')
plt.style.use('default')

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    مولد التقارير المتقدم مع دعم أنواع متعددة من التقارير والتنسيقات
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_arabic_styles()
        
        # إعداد matplotlib للعربية
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Tahoma']
        plt.rcParams['axes.unicode_minus'] = False
        
        # إعداد seaborn
        sns.set_style("whitegrid")
        sns.set_palette("husl")
    
    def setup_arabic_styles(self):
        """إعداد الأنماط للنصوص العربية"""
        try:
            # إنشاء أنماط مخصصة للعربية
            self.arabic_title = ParagraphStyle(
                'ArabicTitle',
                parent=self.styles['Title'],
                fontName='Helvetica-Bold',
                fontSize=18,
                alignment=2,  # Right alignment for Arabic
                textColor=colors.darkblue,
                spaceAfter=20
            )
            
            self.arabic_heading = ParagraphStyle(
                'ArabicHeading',
                parent=self.styles['Heading1'],
                fontName='Helvetica-Bold',
                fontSize=14,
                alignment=2,
                textColor=colors.darkgreen,
                spaceAfter=12
            )
            
            self.arabic_normal = ParagraphStyle(
                'ArabicNormal',
                parent=self.styles['Normal'],
                fontName='Helvetica',
                fontSize=12,
                alignment=2,
                leading=18
            )
            
        except Exception as e:
            logger.error(f"Error setting up Arabic styles: {str(e)}")
    
    def generate_student_report(self, filters=None, format='pdf'):
        """
        إنشاء تقرير الطلاب الشامل
        """
        try:
            from students.models import Student, User
            from academic.models import Enrollment
            
            # تطبيق الفلاتر
            queryset = Student.objects.select_related('user', 'department')
            
            if filters:
                if filters.get('department'):
                    queryset = queryset.filter(department_id=filters['department'])
                if filters.get('status'):
                    queryset = queryset.filter(status=filters['status'])
                if filters.get('academic_level'):
                    queryset = queryset.filter(academic_level=filters['academic_level'])
                if filters.get('date_from'):
                    queryset = queryset.filter(created_at__gte=filters['date_from'])
                if filters.get('date_to'):
                    queryset = queryset.filter(created_at__lte=filters['date_to'])
            
            students = queryset.all()
            
            # إحصائيات أساسية
            stats = {
                'total_students': students.count(),
                'active_students': students.filter(status='ACTIVE').count(),
                'by_department': students.values('department__name').annotate(
                    count=Count('id')
                ).order_by('-count'),
                'by_academic_level': students.values('academic_level').annotate(
                    count=Count('id')
                ).order_by('-count'),
                'enrollment_trend': self._get_enrollment_trend(students)
            }
            
            # إنشاء التقرير حسب التنسيق المطلوب
            if format == 'pdf':
                return self._generate_student_pdf_report(students, stats)
            elif format == 'excel':
                return self._generate_student_excel_report(students, stats)
            elif format == 'csv':
                return self._generate_student_csv_report(students)
            else:
                return self._generate_student_json_report(students, stats)
                
        except Exception as e:
            logger.error(f"Error generating student report: {str(e)}")
            raise
    
    def generate_academic_report(self, filters=None, format='pdf'):
        """
        إنشاء تقرير أكاديمي شامل
        """
        try:
            from academic.models import Enrollment, Grade
            from courses.models import Course
            
            # الحصول على البيانات الأكاديمية
            enrollments = Enrollment.objects.select_related(
                'student__user', 'course', 'semester'
            ).filter(is_active=True)
            
            if filters:
                if filters.get('semester'):
                    enrollments = enrollments.filter(semester_id=filters['semester'])
                if filters.get('course'):
                    enrollments = enrollments.filter(course_id=filters['course'])
                if filters.get('department'):
                    enrollments = enrollments.filter(
                        student__department_id=filters['department']
                    )
            
            # إحصائيات أكاديمية
            stats = {
                'total_enrollments': enrollments.count(),
                'by_course': enrollments.values('course__name').annotate(
                    count=Count('id')
                ).order_by('-count'),
                'success_rate': self._calculate_success_rate(enrollments),
                'grade_distribution': self._get_grade_distribution(enrollments),
                'attendance_stats': self._get_attendance_statistics(enrollments)
            }
            
            if format == 'pdf':
                return self._generate_academic_pdf_report(enrollments, stats)
            elif format == 'excel':
                return self._generate_academic_excel_report(enrollments, stats)
            else:
                return self._generate_academic_json_report(enrollments, stats)
                
        except Exception as e:
            logger.error(f"Error generating academic report: {str(e)}")
            raise
    
    def generate_financial_report(self, filters=None, format='pdf'):
        """
        إنشاء تقرير مالي شامل
        """
        try:
            # من المفترض أن يكون لدينا نماذج مالية
            # هذا مثال افتراضي
            stats = {
                'total_revenue': 1250000,  # مثال
                'total_expenses': 890000,
                'net_profit': 360000,
                'by_category': [
                    {'name': 'رسوم دراسية', 'amount': 1000000},
                    {'name': 'رسوم تسجيل', 'amount': 150000},
                    {'name': 'رسوم أخرى', 'amount': 100000}
                ],
                'monthly_trend': self._get_financial_trend()
            }
            
            if format == 'pdf':
                return self._generate_financial_pdf_report(stats)
            elif format == 'excel':
                return self._generate_financial_excel_report(stats)
            else:
                return JsonResponse(stats)
                
        except Exception as e:
            logger.error(f"Error generating financial report: {str(e)}")
            raise
    
    def generate_attendance_report(self, filters=None, format='pdf'):
        """
        إنشاء تقرير الحضور والغياب
        """
        try:
            # افتراض وجود نموذج الحضور
            stats = {
                'overall_attendance_rate': 85.5,
                'by_course': [
                    {'course': 'البرمجة المتقدمة', 'attendance_rate': 92.3},
                    {'course': 'قواعد البيانات', 'attendance_rate': 87.1},
                    {'course': 'هندسة البرمجيات', 'attendance_rate': 79.4}
                ],
                'by_department': [
                    {'department': 'علوم الحاسوب', 'attendance_rate': 88.2},
                    {'department': 'الهندسة', 'attendance_rate': 83.7}
                ],
                'trend_data': self._get_attendance_trend()
            }
            
            if format == 'pdf':
                return self._generate_attendance_pdf_report(stats)
            elif format == 'excel':
                return self._generate_attendance_excel_report(stats)
            else:
                return JsonResponse(stats)
                
        except Exception as e:
            logger.error(f"Error generating attendance report: {str(e)}")
            raise
    
    def _generate_student_pdf_report(self, students, stats):
        """إنشاء تقرير PDF للطلاب"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=72)
            
            story = []
            
            # عنوان التقرير
            title = Paragraph("تقرير الطلاب الشامل", self.arabic_title)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # معلومات التقرير
            report_info = f"""
            <b>تاريخ التقرير:</b> {timezone.now().strftime('%Y-%m-%d %H:%M')}<br/>
            <b>إجمالي الطلاب:</b> {stats['total_students']}<br/>
            <b>الطلاب النشطون:</b> {stats['active_students']}<br/>
            """
            story.append(Paragraph(report_info, self.arabic_normal))
            story.append(Spacer(1, 20))
            
            # إحصائيات حسب القسم
            if stats['by_department']:
                story.append(Paragraph("توزيع الطلاب حسب القسم", self.arabic_heading))
                
                dept_data = [['القسم', 'عدد الطلاب']]
                for dept in stats['by_department']:
                    dept_data.append([
                        dept['department__name'] or 'غير محدد',
                        str(dept['count'])
                    ])
                
                dept_table = Table(dept_data)
                dept_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(dept_table)
                story.append(Spacer(1, 20))
            
            # إنشاء مخطط بياني
            chart_path = self._create_student_chart(stats)
            if chart_path and os.path.exists(chart_path):
                story.append(Paragraph("الرسم البياني للتوزيع", self.arabic_heading))
                img = Image(chart_path, width=400, height=300)
                story.append(img)
                story.append(Spacer(1, 20))
                
                # حذف الملف المؤقت
                os.remove(chart_path)
            
            # بناء المستند
            doc.build(story)
            
            # إرجاع الاستجابة
            buffer.seek(0)
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="student_report_{timezone.now().strftime("%Y%m%d")}.pdf"'
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating student PDF report: {str(e)}")
            raise
    
    def _generate_student_excel_report(self, students, stats):
        """إنشاء تقرير Excel للطلاب"""
        try:
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            
            # تنسيقات
            title_format = workbook.add_format({
                'bold': True,
                'font_size': 16,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#4472C4',
                'font_color': 'white'
            })
            
            header_format = workbook.add_format({
                'bold': True,
                'font_size': 12,
                'align': 'center',
                'bg_color': '#D9E1F2',
                'border': 1
            })
            
            cell_format = workbook.add_format({
                'align': 'center',
                'border': 1
            })
            
            # ورقة الإحصائيات
            stats_sheet = workbook.add_worksheet('الإحصائيات')
            stats_sheet.write('A1', 'تقرير الطلاب الشامل', title_format)
            stats_sheet.merge_range('A1:C1', 'تقرير الطلاب الشامل', title_format)
            
            row = 3
            stats_sheet.write(f'A{row}', 'إجمالي الطلاب', header_format)
            stats_sheet.write(f'B{row}', stats['total_students'], cell_format)
            
            row += 1
            stats_sheet.write(f'A{row}', 'الطلاب النشطون', header_format)
            stats_sheet.write(f'B{row}', stats['active_students'], cell_format)
            
            # ورقة التفاصيل
            details_sheet = workbook.add_worksheet('تفاصيل الطلاب')
            
            # رؤوس الأعمدة
            headers = ['الرقم الجامعي', 'الاسم', 'القسم', 'المستوى', 'الحالة', 'تاريخ التسجيل']
            for col, header in enumerate(headers):
                details_sheet.write(0, col, header, header_format)
            
            # بيانات الطلاب
            for row, student in enumerate(students, 1):
                details_sheet.write(row, 0, student.student_id or '', cell_format)
                details_sheet.write(row, 1, student.user.get_full_name() or student.user.username, cell_format)
                details_sheet.write(row, 2, student.department.name if student.department else 'غير محدد', cell_format)
                details_sheet.write(row, 3, student.get_academic_level_display() if hasattr(student, 'get_academic_level_display') else '', cell_format)
                details_sheet.write(row, 4, student.get_status_display() if hasattr(student, 'get_status_display') else student.status, cell_format)
                details_sheet.write(row, 5, student.created_at.strftime('%Y-%m-%d') if student.created_at else '', cell_format)
            
            # ضبط عرض الأعمدة
            for sheet in [stats_sheet, details_sheet]:
                sheet.set_column('A:F', 15)
            
            workbook.close()
            output.seek(0)
            
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="student_report_{timezone.now().strftime("%Y%m%d")}.xlsx"'
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating student Excel report: {str(e)}")
            raise
    
    def _generate_student_csv_report(self, students):
        """إنشاء تقرير CSV للطلاب"""
        try:
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="student_report_{timezone.now().strftime("%Y%m%d")}.csv"'
            
            # إضافة BOM للدعم الصحيح للعربية في Excel
            response.write('\ufeff')
            
            # إنشاء DataFrame
            data = []
            for student in students:
                data.append({
                    'الرقم الجامعي': student.student_id or '',
                    'الاسم': student.user.get_full_name() or student.user.username,
                    'القسم': student.department.name if student.department else 'غير محدد',
                    'المستوى': student.get_academic_level_display() if hasattr(student, 'get_academic_level_display') else '',
                    'الحالة': student.get_status_display() if hasattr(student, 'get_status_display') else student.status,
                    'تاريخ التسجيل': student.created_at.strftime('%Y-%m-%d') if student.created_at else ''
                })
            
            df = pd.DataFrame(data)
            df.to_csv(response, index=False, encoding='utf-8-sig')
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating student CSV report: {str(e)}")
            raise
    
    def _create_student_chart(self, stats):
        """إنشاء مخطط بياني للطلاب"""
        try:
            if not stats['by_department']:
                return None
            
            # تحضير البيانات
            departments = [item['department__name'] or 'غير محدد' for item in stats['by_department']]
            counts = [item['count'] for item in stats['by_department']]
            
            # إنشاء المخطط
            plt.figure(figsize=(10, 6))
            bars = plt.bar(departments, counts, color=['#4472C4', '#70AD47', '#FFC000', '#C5504B'])
            
            plt.title('توزيع الطلاب حسب القسم', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('الأقسام', fontsize=12)
            plt.ylabel('عدد الطلاب', fontsize=12)
            
            # إضافة قيم على الأعمدة
            for bar, count in zip(bars, counts):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                        str(count), ha='center', va='bottom', fontweight='bold')
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # حفظ المخطط
            chart_path = f'/tmp/student_chart_{timezone.now().timestamp()}.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            logger.error(f"Error creating student chart: {str(e)}")
            return None
    
    def _get_enrollment_trend(self, students):
        """الحصول على اتجاه التسجيل"""
        try:
            # مثال على البيانات - يجب استبدالها ببيانات حقيقية
            months = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو']
            enrollments = [45, 52, 38, 67, 73, 61]
            
            return list(zip(months, enrollments))
            
        except Exception as e:
            logger.error(f"Error getting enrollment trend: {str(e)}")
            return []
    
    def _calculate_success_rate(self, enrollments):
        """حساب معدل النجاح"""
        try:
            # مثال - يجب تنفيذه بناءً على نماذج الدرجات الفعلية
            return 85.7
        except Exception as e:
            logger.error(f"Error calculating success rate: {str(e)}")
            return 0
    
    def _get_grade_distribution(self, enrollments):
        """الحصول على توزيع الدرجات"""
        try:
            # مثال على البيانات
            return [
                {'grade': 'ممتاز', 'count': 45, 'percentage': 25.5},
                {'grade': 'جيد جداً', 'count': 67, 'percentage': 38.1},
                {'grade': 'جيد', 'count': 52, 'percentage': 29.5},
                {'grade': 'مقبول', 'count': 12, 'percentage': 6.8}
            ]
        except Exception as e:
            logger.error(f"Error getting grade distribution: {str(e)}")
            return []
    
    def _get_attendance_statistics(self, enrollments):
        """الحصول على إحصائيات الحضور"""
        try:
            return {
                'average_attendance': 85.3,
                'highest_attendance': 96.7,
                'lowest_attendance': 67.2
            }
        except Exception as e:
            logger.error(f"Error getting attendance statistics: {str(e)}")
            return {}
    
    def _get_financial_trend(self):
        """الحصول على الاتجاه المالي"""
        try:
            months = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو']
            revenue = [120000, 135000, 128000, 142000, 155000, 148000]
            expenses = [85000, 92000, 88000, 95000, 102000, 98000]
            
            return {
                'months': months,
                'revenue': revenue,
                'expenses': expenses
            }
        except Exception as e:
            logger.error(f"Error getting financial trend: {str(e)}")
            return {}
    
    def _get_attendance_trend(self):
        """الحصول على اتجاه الحضور"""
        try:
            weeks = ['الأسبوع 1', 'الأسبوع 2', 'الأسبوع 3', 'الأسبوع 4']
            attendance_rates = [88.5, 85.2, 87.8, 89.1]
            
            return list(zip(weeks, attendance_rates))
        except Exception as e:
            logger.error(f"Error getting attendance trend: {str(e)}")
            return []
    
    # طرق إضافية لإنشاء تقارير أخرى...
    def _generate_academic_pdf_report(self, enrollments, stats):
        """إنشاء تقرير PDF أكاديمي"""
        # تنفيذ مشابه لتقرير الطلاب
        pass
    
    def _generate_financial_pdf_report(self, stats):
        """إنشاء تقرير PDF مالي"""
        # تنفيذ التقرير المالي
        pass
    
    def _generate_attendance_pdf_report(self, stats):
        """إنشاء تقرير PDF للحضور"""
        # تنفيذ تقرير الحضور
        pass


# دوال مساعدة للاستخدام السهل
def generate_student_report(filters=None, format='pdf'):
    """دالة مساعدة لإنشاء تقرير الطلاب"""
    generator = ReportGenerator()
    return generator.generate_student_report(filters, format)

def generate_academic_report(filters=None, format='pdf'):
    """دالة مساعدة لإنشاء التقرير الأكاديمي"""
    generator = ReportGenerator()
    return generator.generate_academic_report(filters, format)

def generate_financial_report(filters=None, format='pdf'):
    """دالة مساعدة لإنشاء التقرير المالي"""
    generator = ReportGenerator()
    return generator.generate_financial_report(filters, format)

def generate_attendance_report(filters=None, format='pdf'):
    """دالة مساعدة لإنشاء تقرير الحضور"""
    generator = ReportGenerator()
    return generator.generate_attendance_report(filters, format)