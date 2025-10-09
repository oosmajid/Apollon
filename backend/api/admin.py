# api/admin.py

from django.contrib import admin
from . import models

# ثبت تمام مدل‌ها برای نمایش در پنل ادمین
# با این کار، جنگو به صورت خودکار یک رابط کاربری کامل برای مدیریت این مدل‌ها می‌سازد

admin.site.register(models.User)
admin.site.register(models.Apollonyar)
admin.site.register(models.Course)
admin.site.register(models.Term)
admin.site.register(models.Group)
admin.site.register(models.AssignmentDef)
admin.site.register(models.AssignmentDefTemplate)
admin.site.register(models.CallDef)
admin.site.register(models.Profile)
admin.site.register(models.MedalDef)
admin.site.register(models.Medal)
admin.site.register(models.DiscountCode)
admin.site.register(models.Transaction)
admin.site.register(models.TransactionNote)
admin.site.register(models.Installment)
admin.site.register(models.Assignment)
admin.site.register(models.AssignmentSubmission)
admin.site.register(models.AssignmentSubmissionFile)
admin.site.register(models.Call)
admin.site.register(models.Note)
admin.site.register(models.Log)
admin.site.register(models.OTPCode)