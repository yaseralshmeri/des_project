class UserNotificationPreference(models.Model):
    """تفضيلات إشعارات المستخدم المحسنة"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_notification_preferences',
                               verbose_name="المستخدم")
    
    # تفضيلات القنوات
    email_enabled = models.BooleanField(default=True, verbose_name="البريد الإلكتروني")
    sms_enabled = models.BooleanField(default=False, verbose_name="الرسائل النصية")
    push_enabled = models.BooleanField(default=True, verbose_name="الإشعارات المدفوعة")
    in_app_enabled = models.BooleanField(default=True, verbose_name="الإشعارات داخل التطبيق")
    
    # تفضيلات الفئات
    academic_notifications = models.BooleanField(default=True, verbose_name="الإشعارات الأكاديمية")
    financial_notifications = models.BooleanField(default=True, verbose_name="الإشعارات المالية")
    administrative_notifications = models.BooleanField(default=True, verbose_name="الإشعارات الإدارية")
    
    # التواريخ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "تفضيلات إشعارات المستخدم"
        verbose_name_plural = "تفضيلات إشعارات المستخدمين"
    
    def __str__(self):
        return f"تفضيلات {self.user.username}"

