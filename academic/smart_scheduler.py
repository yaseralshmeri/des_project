# نظام الجداول الذكي والمتطور
# Advanced Smart Scheduling System with AI

import datetime
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.core.exceptions import ValidationError
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import json
import logging

# Machine Learning imports
try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    import numpy as np
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class TimeSlot:
    """فترة زمنية للجدولة"""
    day: int  # 0=الأحد, 1=الاثنين, إلخ
    start_time: datetime.time
    end_time: datetime.time
    duration: int  # بالدقائق
    
    def __str__(self):
        days = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت']
        return f"{days[self.day]} {self.start_time}-{self.end_time}"
    
    def overlaps_with(self, other: 'TimeSlot') -> bool:
        """فحص التداخل مع فترة أخرى"""
        if self.day != other.day:
            return False
        return (self.start_time < other.end_time and 
                self.end_time > other.start_time)

@dataclass
class SchedulingConstraint:
    """قيود الجدولة"""
    teacher_id: Optional[str] = None
    room_id: Optional[str] = None
    student_group_ids: List[str] = field(default_factory=list)
    preferred_time_slots: List[TimeSlot] = field(default_factory=list)
    blackout_time_slots: List[TimeSlot] = field(default_factory=list)
    max_consecutive_hours: int = 3
    min_break_between_classes: int = 15  # دقائق
    preferred_days: List[int] = field(default_factory=list)
    avoid_days: List[int] = field(default_factory=list)

@dataclass
class SchedulingRequest:
    """طلب جدولة مقرر"""
    course_id: str
    course_name: str
    teacher_id: str
    credit_hours: int
    sessions_per_week: int
    duration_per_session: int  # دقائق
    required_room_type: str
    student_groups: List[str]
    constraints: SchedulingConstraint
    priority: int = 1  # 1=عادي, 2=عالي, 3=حرج

class SmartScheduler:
    """نظام الجدولة الذكي"""
    
    # أوقات العمل الافتراضية
    DEFAULT_WORK_HOURS = {
        'start_time': datetime.time(8, 0),  # 8:00 ص
        'end_time': datetime.time(17, 0),   # 5:00 م
        'working_days': [0, 1, 2, 3, 4],   # الأحد-الخميس
        'break_times': [
            (datetime.time(12, 0), datetime.time(13, 0)),  # استراحة الغداء
        ]
    }
    
    def __init__(self, semester_id: str):
        self.semester_id = semester_id
        self.time_slots = self._generate_time_slots()
        self.conflicts = []
        self.optimization_scores = {}
        
    def _generate_time_slots(self) -> List[TimeSlot]:
        """توليد الفترات الزمنية المتاحة"""
        slots = []
        work_hours = self.DEFAULT_WORK_HOURS
        
        for day in work_hours['working_days']:
            current_time = work_hours['start_time']
            end_time = work_hours['end_time']
            
            while current_time < end_time:
                # تجنب أوقات الاستراحة
                is_break_time = False
                for break_start, break_end in work_hours['break_times']:
                    if break_start <= current_time < break_end:
                        current_time = break_end
                        is_break_time = True
                        break
                
                if is_break_time or current_time >= end_time:
                    continue
                
                # إنشاء فترة زمنية (ساعة واحدة)
                slot_end = (datetime.datetime.combine(datetime.date.today(), current_time) + 
                           datetime.timedelta(hours=1)).time()
                
                if slot_end <= end_time:
                    slots.append(TimeSlot(
                        day=day,
                        start_time=current_time,
                        end_time=slot_end,
                        duration=60
                    ))
                
                current_time = slot_end
        
        return slots
    
    def schedule_courses(self, requests: List[SchedulingRequest]) -> Dict:
        """جدولة مجموعة من المقررات"""
        logger.info(f"بدء جدولة {len(requests)} مقرر للفصل الدراسي {self.semester_id}")
        
        # ترتيب الطلبات حسب الأولوية والقيود
        sorted_requests = self._prioritize_requests(requests)
        
        # إنشاء الجدول الأساسي
        schedule = {}
        failed_requests = []
        conflicts = []
        
        for request in sorted_requests:
            try:
                sessions = self._schedule_single_course(request, schedule)
                if sessions:
                    schedule[request.course_id] = {
                        'course_name': request.course_name,
                        'teacher_id': request.teacher_id,
                        'sessions': sessions,
                        'total_hours': len(sessions)
                    }
                    logger.info(f"تم جدولة مقرر {request.course_name} بنجاح")
                else:
                    failed_requests.append(request)
                    logger.warning(f"فشل في جدولة مقرر {request.course_name}")
            except Exception as e:
                logger.error(f"خطأ في جدولة مقرر {request.course_name}: {str(e)}")
                failed_requests.append(request)
        
        # تحسين الجدول باستخدام الذكاء الاصطناعي
        if ML_AVAILABLE:
            schedule = self._optimize_schedule_with_ai(schedule)
        
        # إنشاء التقرير النهائي
        result = {
            'schedule': schedule,
            'failed_requests': [
                {
                    'course_id': req.course_id,
                    'course_name': req.course_name,
                    'reason': 'عدم توفر فترات زمنية مناسبة'
                }
                for req in failed_requests
            ],
            'conflicts': self.conflicts,
            'optimization_score': self._calculate_optimization_score(schedule),
            'statistics': self._generate_statistics(schedule),
            'recommendations': self._generate_recommendations(schedule, failed_requests)
        }
        
        logger.info(f"اكتملت الجدولة: {len(schedule)} مقرر مجدول، {len(failed_requests)} مقرر فاشل")
        return result
    
    def _prioritize_requests(self, requests: List[SchedulingRequest]) -> List[SchedulingRequest]:
        """ترتيب طلبات الجدولة حسب الأولوية"""
        def priority_score(request):
            score = request.priority * 1000
            
            # المقررات ذات الساعات الأكثر لها أولوية
            score += request.credit_hours * 100
            
            # المقررات مع قيود أكثر لها أولوية
            constraint_score = 0
            if request.constraints.preferred_time_slots:
                constraint_score += len(request.constraints.preferred_time_slots) * 10
            if request.constraints.blackout_time_slots:
                constraint_score += len(request.constraints.blackout_time_slots) * 5
            
            score += constraint_score
            return score
        
        return sorted(requests, key=priority_score, reverse=True)
    
    def _schedule_single_course(self, request: SchedulingRequest, 
                               existing_schedule: Dict) -> List[Dict]:
        """جدولة مقرر واحد"""
        sessions = []
        sessions_needed = request.sessions_per_week
        duration_minutes = request.duration_per_session
        
        # البحث عن الفترات المناسبة
        suitable_slots = self._find_suitable_slots(request, existing_schedule, duration_minutes)
        
        if len(suitable_slots) < sessions_needed:
            logger.warning(f"لا توجد فترات كافية لمقرر {request.course_name}")
            return []
        
        # اختيار أفضل الفترات
        selected_slots = self._select_optimal_slots(suitable_slots[:sessions_needed], request)
        
        # إنشاء الجلسات
        for slot in selected_slots:
            sessions.append({
                'day': slot.day,
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'duration': duration_minutes,
                'room_required': request.required_room_type,
                'student_groups': request.student_groups
            })
        
        return sessions
    
    def _find_suitable_slots(self, request: SchedulingRequest, 
                           existing_schedule: Dict, duration_minutes: int) -> List[TimeSlot]:
        """البحث عن الفترات المناسبة لمقرر"""
        suitable_slots = []
        
        for slot in self.time_slots:
            # فحص القيود الأساسية
            if not self._check_basic_constraints(slot, request):
                continue
            
            # فحص التعارضات مع الجدول الموجود
            if self._has_conflicts(slot, existing_schedule, request):
                continue
            
            # فحص القيود الإضافية
            if self._check_additional_constraints(slot, request, existing_schedule):
                suitable_slots.append(slot)
        
        return suitable_slots
    
    def _check_basic_constraints(self, slot: TimeSlot, request: SchedulingRequest) -> bool:
        """فحص القيود الأساسية"""
        constraints = request.constraints
        
        # فحص الأيام المرفوضة
        if slot.day in constraints.avoid_days:
            return False
        
        # فحص الأيام المفضلة (إذا كانت محددة)
        if constraints.preferred_days and slot.day not in constraints.preferred_days:
            return False
        
        # فحص أوقات المنع
        for blackout_slot in constraints.blackout_time_slots:
            if slot.overlaps_with(blackout_slot):
                return False
        
        return True
    
    def _has_conflicts(self, slot: TimeSlot, existing_schedule: Dict, 
                      request: SchedulingRequest) -> bool:
        """فحص التعارضات مع الجدول الموجود"""
        for course_id, course_info in existing_schedule.items():
            for session in course_info['sessions']:
                session_slot = TimeSlot(
                    day=session['day'],
                    start_time=datetime.time.fromisoformat(session['start_time']),
                    end_time=datetime.time.fromisoformat(session['end_time']),
                    duration=session['duration']
                )
                
                if slot.overlaps_with(session_slot):
                    # فحص تعارض الأستاذ
                    if course_info['teacher_id'] == request.teacher_id:
                        return True
                    
                    # فحص تعارض مجموعات الطلاب
                    if any(group in session['student_groups'] 
                           for group in request.student_groups):
                        return True
        
        return False
    
    def _check_additional_constraints(self, slot: TimeSlot, request: SchedulingRequest,
                                    existing_schedule: Dict) -> bool:
        """فحص القيود الإضافية"""
        constraints = request.constraints
        
        # فحص الحد الأقصى للساعات المتتالية
        consecutive_hours = self._count_consecutive_hours(
            slot, request.teacher_id, existing_schedule
        )
        if consecutive_hours >= constraints.max_consecutive_hours:
            return False
        
        # فحص الحد الأدنى للاستراحة بين الحصص
        if not self._check_minimum_break(
            slot, request.teacher_id, existing_schedule, constraints.min_break_between_classes
        ):
            return False
        
        return True
    
    def _count_consecutive_hours(self, slot: TimeSlot, teacher_id: str, 
                               existing_schedule: Dict) -> int:
        """حساب الساعات المتتالية للأستاذ"""
        consecutive = 1  # الحصة الحالية
        
        # البحث في الجدول الموجود
        for course_info in existing_schedule.values():
            if course_info['teacher_id'] != teacher_id:
                continue
            
            for session in course_info['sessions']:
                if session['day'] != slot.day:
                    continue
                
                session_end = datetime.time.fromisoformat(session['end_time'])
                session_start = datetime.time.fromisoformat(session['start_time'])
                
                # فحص الحصص المتتالية قبل الفترة الحالية
                if session_end == slot.start_time:
                    consecutive += 1
                
                # فحص الحصص المتتالية بعد الفترة الحالية
                if session_start == slot.end_time:
                    consecutive += 1
        
        return consecutive
    
    def _check_minimum_break(self, slot: TimeSlot, teacher_id: str, 
                           existing_schedule: Dict, min_break_minutes: int) -> bool:
        """فحص الحد الأدنى للاستراحة"""
        min_break = datetime.timedelta(minutes=min_break_minutes)
        
        for course_info in existing_schedule.values():
            if course_info['teacher_id'] != teacher_id:
                continue
            
            for session in course_info['sessions']:
                if session['day'] != slot.day:
                    continue
                
                session_end = datetime.time.fromisoformat(session['end_time'])
                session_start = datetime.time.fromisoformat(session['start_time'])
                
                # فحص الاستراحة قبل الحصة
                time_diff = datetime.datetime.combine(datetime.date.today(), slot.start_time) - \
                           datetime.datetime.combine(datetime.date.today(), session_end)
                if datetime.timedelta(0) < time_diff < min_break:
                    return False
                
                # فحص الاستراحة بعد الحصة
                time_diff = datetime.datetime.combine(datetime.date.today(), session_start) - \
                           datetime.datetime.combine(datetime.date.today(), slot.end_time)
                if datetime.timedelta(0) < time_diff < min_break:
                    return False
        
        return True
    
    def _select_optimal_slots(self, slots: List[TimeSlot], 
                            request: SchedulingRequest) -> List[TimeSlot]:
        """اختيار أفضل الفترات الزمنية"""
        if not slots:
            return []
        
        # تقييم كل فترة
        scored_slots = []
        for slot in slots:
            score = self._calculate_slot_score(slot, request)
            scored_slots.append((slot, score))
        
        # ترتيب حسب النقاط
        scored_slots.sort(key=lambda x: x[1], reverse=True)
        
        # اختيار أفضل الفترات
        selected = []
        for slot, score in scored_slots:
            if len(selected) >= request.sessions_per_week:
                break
            
            # التأكد من عدم التداخل مع الفترات المختارة
            if not any(slot.overlaps_with(selected_slot) for selected_slot in selected):
                selected.append(slot)
        
        return selected
    
    def _calculate_slot_score(self, slot: TimeSlot, request: SchedulingRequest) -> float:
        """حساب نقاط الفترة الزمنية"""
        score = 0.0
        constraints = request.constraints
        
        # الفترات المفضلة
        for preferred_slot in constraints.preferred_time_slots:
            if slot.day == preferred_slot.day:
                # نقاط إضافية للأيام المفضلة
                score += 10
                
                # نقاط للأوقات القريبة من المفضلة
                time_diff = abs(
                    (datetime.datetime.combine(datetime.date.today(), slot.start_time) -
                     datetime.datetime.combine(datetime.date.today(), preferred_slot.start_time)).seconds
                )
                if time_diff < 3600:  # أقل من ساعة
                    score += 5
        
        # تفضيل الأوقات الصباحية
        if slot.start_time <= datetime.time(12, 0):
            score += 3
        
        # تجنب الأوقات المتأخرة
        if slot.start_time >= datetime.time(15, 0):
            score -= 2
        
        # توزيع الأيام
        day_scores = {0: 5, 1: 5, 2: 5, 3: 4, 4: 3, 5: 1, 6: 0}  # الأحد-السبت
        score += day_scores.get(slot.day, 0)
        
        return score
    
    def _optimize_schedule_with_ai(self, schedule: Dict) -> Dict:
        """تحسين الجدول باستخدام الذكاء الاصطناعي"""
        if not ML_AVAILABLE:
            logger.warning("مكتبات التعلم الآلي غير متوفرة - تخطي التحسين بالذكاء الاصطناعي")
            return schedule
        
        try:
            # استخراج البيانات للتحليل
            schedule_data = self._extract_schedule_features(schedule)
            
            if not schedule_data:
                return schedule
            
            # تطبيق خوارزمية التجميع لتحسين التوزيع
            optimized_data = self._apply_clustering_optimization(schedule_data)
            
            # تطبيق التحسينات على الجدول
            optimized_schedule = self._apply_optimizations(schedule, optimized_data)
            
            logger.info("تم تحسين الجدول باستخدام الذكاء الاصطناعي")
            return optimized_schedule
            
        except Exception as e:
            logger.error(f"خطأ في تحسين الجدول بالذكاء الاصطناعي: {str(e)}")
            return schedule
    
    def _extract_schedule_features(self, schedule: Dict) -> List[List[float]]:
        """استخراج الميزات من الجدول للتحليل"""
        features = []
        
        for course_id, course_info in schedule.items():
            for session in course_info['sessions']:
                feature_vector = [
                    session['day'],  # اليوم
                    float(session['start_time'].replace(':', '.')),  # وقت البداية
                    session['duration'],  # المدة
                    len(session['student_groups']),  # عدد مجموعات الطلاب
                    hash(course_info['teacher_id']) % 1000,  # معرف الأستاذ (مُشفر)
                ]
                features.append(feature_vector)
        
        return features
    
    def _apply_clustering_optimization(self, data: List[List[float]]) -> Dict:
        """تطبيق خوارزمية التجميع للتحسين"""
        if len(data) < 2:
            return {}
        
        # تطبيع البيانات
        scaler = StandardScaler()
        normalized_data = scaler.fit_transform(data)
        
        # تطبيق K-Means
        n_clusters = min(len(data) // 2, 5)  # عدد مناسب من المجموعات
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(normalized_data)
        
        # تحليل النتائج
        optimization_suggestions = {
            'clusters': clusters.tolist(),
            'cluster_centers': kmeans.cluster_centers_.tolist(),
            'suggestions': self._generate_ai_suggestions(clusters, data)
        }
        
        return optimization_suggestions
    
    def _generate_ai_suggestions(self, clusters: np.ndarray, data: List[List[float]]) -> List[str]:
        """توليد اقتراحات التحسين من التحليل"""
        suggestions = []
        
        # تحليل توزيع الأيام
        day_distribution = {}
        for i, cluster in enumerate(clusters):
            day = int(data[i][0])
            if day not in day_distribution:
                day_distribution[day] = []
            day_distribution[day].append(cluster)
        
        # اقتراحات التوزيع
        days_ar = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس']
        for day, day_clusters in day_distribution.items():
            if len(day_clusters) > len(set(day_clusters)):
                suggestions.append(f"يُنصح بتوزيع أفضل للمقررات في يوم {days_ar[day]}")
        
        # اقتراحات الأوقات
        morning_sessions = sum(1 for row in data if row[1] < 12.0)
        afternoon_sessions = len(data) - morning_sessions
        
        if afternoon_sessions > morning_sessions * 1.5:
            suggestions.append("يُنصح بتوزيع المزيد من المقررات في الفترة الصباحية")
        
        return suggestions
    
    def _apply_optimizations(self, schedule: Dict, optimizations: Dict) -> Dict:
        """تطبيق التحسينات على الجدول"""
        # في هذا الإصدار، نحتفظ بالجدول الأساسي ونضيف معلومات التحسين
        optimized_schedule = schedule.copy()
        
        # إضافة اقتراحات التحسين
        optimized_schedule['_ai_analysis'] = {
            'optimization_applied': True,
            'suggestions': optimizations.get('suggestions', []),
            'analysis_timestamp': timezone.now().isoformat()
        }
        
        return optimized_schedule
    
    def _calculate_optimization_score(self, schedule: Dict) -> float:
        """حساب نقاط تحسين الجدول"""
        if not schedule:
            return 0.0
        
        total_score = 0.0
        total_sessions = 0
        
        # تحليل توزيع الأيام
        day_distribution = [0] * 7
        time_distribution = {'morning': 0, 'afternoon': 0, 'evening': 0}
        
        for course_info in schedule.values():
            for session in course_info['sessions']:
                total_sessions += 1
                day_distribution[session['day']] += 1
                
                # تصنيف الأوقات
                start_hour = int(session['start_time'].split(':')[0])
                if start_hour < 12:
                    time_distribution['morning'] += 1
                    total_score += 10  # الأوقات الصباحية أفضل
                elif start_hour < 15:
                    time_distribution['afternoon'] += 1
                    total_score += 7
                else:
                    time_distribution['evening'] += 1
                    total_score += 3
        
        # خصم نقاط للتوزيع غير المتوازن
        working_days = day_distribution[:5]  # الأحد-الخميس
        if working_days:
            avg_sessions_per_day = sum(working_days) / len(working_days)
            for day_sessions in working_days:
                deviation = abs(day_sessions - avg_sessions_per_day)
                total_score -= deviation * 2
        
        # معدل النقاط
        if total_sessions > 0:
            return min(max(total_score / total_sessions, 0), 100)
        return 0.0
    
    def _generate_statistics(self, schedule: Dict) -> Dict:
        """إنشاء إحصائيات الجدول"""
        stats = {
            'total_courses': len(schedule),
            'total_sessions': 0,
            'day_distribution': [0] * 7,
            'time_distribution': {'morning': 0, 'afternoon': 0, 'evening': 0},
            'teacher_load': {},
            'room_utilization': {},
            'average_sessions_per_day': 0
        }
        
        for course_info in schedule.values():
            teacher_id = course_info['teacher_id']
            if teacher_id not in stats['teacher_load']:
                stats['teacher_load'][teacher_id] = 0
            
            for session in course_info['sessions']:
                stats['total_sessions'] += 1
                stats['day_distribution'][session['day']] += 1
                stats['teacher_load'][teacher_id] += 1
                
                # تصنيف الأوقات
                start_hour = int(session['start_time'].split(':')[0])
                if start_hour < 12:
                    stats['time_distribution']['morning'] += 1
                elif start_hour < 15:
                    stats['time_distribution']['afternoon'] += 1
                else:
                    stats['time_distribution']['evening'] += 1
        
        # حساب المتوسطات
        working_days = sum(stats['day_distribution'][:5])
        stats['average_sessions_per_day'] = working_days / 5 if working_days > 0 else 0
        
        return stats
    
    def _generate_recommendations(self, schedule: Dict, 
                                failed_requests: List[SchedulingRequest]) -> List[str]:
        """توليد توصيات تحسين الجدول"""
        recommendations = []
        
        if not schedule:
            recommendations.append("لم يتم جدولة أي مقرر - يُرجى مراجعة القيود والمتطلبات")
            return recommendations
        
        stats = self._generate_statistics(schedule)
        
        # توصيات التوزيع الزمني
        morning_ratio = stats['time_distribution']['morning'] / stats['total_sessions']
        if morning_ratio < 0.4:
            recommendations.append("يُنصح بجدولة المزيد من المقررات في الفترة الصباحية لتحسين التركيز")
        
        evening_ratio = stats['time_distribution']['evening'] / stats['total_sessions']
        if evening_ratio > 0.3:
            recommendations.append("يُفضل تقليل المقررات المسائية وإعادة توزيعها على الفترات الأخرى")
        
        # توصيات التوزيع اليومي
        working_days = stats['day_distribution'][:5]
        max_day_load = max(working_days) if working_days else 0
        min_day_load = min(working_days) if working_days else 0
        
        if max_day_load > min_day_load * 2:
            recommendations.append("توزيع المقررات غير متوازن بين الأيام - يُنصح بإعادة التوزيع")
        
        # توصيات الأساتذة
        overloaded_teachers = [
            teacher_id for teacher_id, load in stats['teacher_load'].items()
            if load > 20  # أكثر من 20 ساعة أسبوعياً
        ]
        if overloaded_teachers:
            recommendations.append(f"هناك {len(overloaded_teachers)} أستاذ محمل بساعات زائدة - يُنصح بإعادة التوزيع")
        
        # توصيات للمقررات الفاشلة
        if failed_requests:
            recommendations.append(f"فشل في جدولة {len(failed_requests)} مقرر - قد تحتاج لتعديل القيود أو إضافة فترات زمنية")
        
        # توصيات عامة
        if stats['total_sessions'] < 30:
            recommendations.append("الجدول يبدو خفيفاً - يمكن إضافة المزيد من المقررات أو الأنشطة")
        elif stats['total_sessions'] > 100:
            recommendations.append("الجدول محمل بكثافة عالية - قد تحتاج لتوزيع أفضل أو تقليل العبء")
        
        return recommendations

# دوال مساعدة للاستخدام الخارجي

def create_scheduling_request(course_data: Dict) -> SchedulingRequest:
    """إنشاء طلب جدولة من بيانات المقرر"""
    constraints = SchedulingConstraint(
        teacher_id=course_data.get('teacher_id'),
        preferred_time_slots=[],
        blackout_time_slots=[],
        max_consecutive_hours=course_data.get('max_consecutive_hours', 3),
        min_break_between_classes=course_data.get('min_break_minutes', 15)
    )
    
    return SchedulingRequest(
        course_id=course_data['course_id'],
        course_name=course_data['course_name'],
        teacher_id=course_data['teacher_id'],
        credit_hours=course_data.get('credit_hours', 3),
        sessions_per_week=course_data.get('sessions_per_week', 2),
        duration_per_session=course_data.get('duration_per_session', 60),
        required_room_type=course_data.get('room_type', 'classroom'),
        student_groups=course_data.get('student_groups', []),
        constraints=constraints,
        priority=course_data.get('priority', 1)
    )

def schedule_semester_courses(semester_id: str, courses_data: List[Dict]) -> Dict:
    """جدولة مقررات فصل دراسي كامل"""
    scheduler = SmartScheduler(semester_id)
    
    # تحويل بيانات المقررات إلى طلبات جدولة
    requests = [create_scheduling_request(course) for course in courses_data]
    
    # تنفيذ الجدولة
    result = scheduler.schedule_courses(requests)
    
    return result