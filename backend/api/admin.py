# api/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from . import models

# === کاربران و آپولون‌یارها ===

@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    list_display = ('phone_number', 'first_name', 'last_name', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'sex', 'country')
    search_fields = ('phone_number', 'first_name', 'last_name', 'email')
    ordering = ('-created_at',)

    fieldsets = (
        ('اطلاعات احراز هویت', {'fields': ('phone_number', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'email', 'sex', 'birthday')}),
        ('اطلاعات تماس', {'fields': ('phone_2_number', 'country', 'state_province', 'city', 'full_address', 'postal_code')}),
        ('تصویر', {'fields': ('photo',)}),
        ('دسترسی‌ها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

@admin.register(models.Apollonyar)
class ApollonyarAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number', 'is_admin', 'is_blocked', 'created_at')
    list_filter = ('is_admin', 'is_blocked')
    search_fields = ('first_name', 'last_name', 'phone_number', 'telegram_id')
    ordering = ('-created_at',)

# === ساختار آموزشی ===

@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_price', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)
    fields = ('name', 'total_price')

@admin.register(models.Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'start_date', 'end_date')
    list_filter = ('course', 'start_date')
    search_fields = ('name', 'course__name')
    ordering = ('-start_date',)

@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'term', 'created_at')
    list_filter = ('course', 'term')
    search_fields = ('title', 'course__name', 'term__name')
    ordering = ('-created_at',)

@admin.register(models.AssignmentFile)
class AssignmentFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'file', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)

@admin.register(models.AssignmentDef)
class AssignmentDefAdmin(admin.ModelAdmin):
    list_display = ('title', 'term', 'deadline', 'is_required', 'created_at')
    list_filter = ('term', 'is_required', 'deadline')
    search_fields = ('title', 'term__name')
    ordering = ('-deadline',)
    filter_horizontal = ('assignment_files',)

@admin.register(models.AssignmentDefTemplate)
class AssignmentDefTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'assignment_def', 'is_help_file', 'created_at')
    list_filter = ('is_help_file', 'assignment_def')
    search_fields = ('title', 'assignment_def__title')
    ordering = ('-created_at',)

@admin.register(models.CallDef)
class CallDefAdmin(admin.ModelAdmin):
    list_display = ('title', 'term', 'start_due_date', 'end_due_date')
    list_filter = ('term', 'start_due_date')
    search_fields = ('title', 'term__name')
    ordering = ('-start_due_date',)

# === پروفایل هنرجو ===

@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'term', 'group', 'type', 'status', 'hearts', 'stars')
    list_filter = ('type', 'status', 'course', 'term')
    search_fields = ('user__phone_number', 'user__first_name', 'user__last_name')
    ordering = ('-created_at',)
    raw_id_fields = ('user', 'apollonyar', 'sales_representative')

# === مدال‌ها و تخفیف‌ها ===

@admin.register(models.MedalDef)
class MedalDefAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('title',)

@admin.register(models.Medal)
class MedalAdmin(admin.ModelAdmin):
    list_display = ('profile', 'medal_def', 'giver_apollonyar', 'timestamp')
    list_filter = ('medal_def', 'timestamp')
    search_fields = ('profile__user__phone_number', 'medal_def__title')
    ordering = ('-timestamp',)
    raw_id_fields = ('profile',)

@admin.register(models.DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'course', 'final_cash_price', 'final_installment_price', 'usage_count', 'max_usage', 'expiration_date')
    list_filter = ('course', 'expiration_date')
    search_fields = ('code', 'course__name')
    ordering = ('-created_at',)

# === مالی ===

@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('target_user', 'amount', 'type', 'payment_method', 'verification_status', 'timestamp')
    list_filter = ('type', 'payment_method', 'verification_status', 'timestamp')
    search_fields = ('target_user__phone_number', 'reference_number')
    ordering = ('-timestamp',)
    raw_id_fields = ('target_user',)

@admin.register(models.TransactionNote)
class TransactionNoteAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'author_apollonyar', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('note', 'transaction__reference_number')
    ordering = ('-timestamp',)
    raw_id_fields = ('transaction',)

@admin.register(models.Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = ('profile', 'due_amount', 'due_date', 'status', 'is_splited')
    list_filter = ('status', 'is_splited', 'due_date')
    search_fields = ('profile__user__phone_number',)
    ordering = ('-due_date',)
    raw_id_fields = ('profile', 'transaction')

# === فعالیت‌های هنرجو و آپولون‌یار ===

@admin.register(models.Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('profile', 'assignment_def', 'deadline', 'created_at')
    list_filter = ('deadline', 'assignment_def')
    search_fields = ('profile__user__phone_number', 'assignment_def__title')
    ordering = ('-deadline',)
    raw_id_fields = ('profile',)

@admin.register(models.AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'submission_timestamp', 'grade', 'assessor_apollonyar', 'assessment_timestamp')
    list_filter = ('submission_timestamp', 'assessment_timestamp', 'grade')
    search_fields = ('assignment__profile__user__phone_number', 'feedback')
    ordering = ('-submission_timestamp',)
    raw_id_fields = ('assignment',)

@admin.register(models.AssignmentSubmissionFile)
class AssignmentSubmissionFileAdmin(admin.ModelAdmin):
    list_display = ('submission', 'template', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('description', 'submission__assignment__assignment_def__title')
    ordering = ('-created_at',)
    raw_id_fields = ('submission',)

@admin.register(models.Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ('profile', 'type', 'status', 'caller', 'call_timestamp')
    list_filter = ('type', 'status', 'call_timestamp')
    search_fields = ('profile__user__phone_number', 'description')
    ordering = ('-call_timestamp',)
    raw_id_fields = ('profile',)

@admin.register(models.Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('profile', 'course', 'author_apollonyar', 'timestamp')
    list_filter = ('timestamp', 'course')
    search_fields = ('note', 'profile__user__phone_number')
    ordering = ('-timestamp',)
    raw_id_fields = ('profile',)

@admin.register(models.Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('action', 'course', 'issuer_apollonyar', 'timestamp')
    list_filter = ('timestamp', 'course')
    search_fields = ('action', 'description')
    ordering = ('-timestamp',)

@admin.register(models.OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'code', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('phone_number', 'code')
    ordering = ('-created_at',)