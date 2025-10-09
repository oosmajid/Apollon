from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# === 0. UserManager برای مدل User ===
class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)

# === 1. کاربران و آپولون‌یارها ===

class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True, verbose_name="شماره تلفن")
    first_name = models.CharField(max_length=150, blank=True, verbose_name="نام")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="نام خانوادگی")
    email = models.EmailField(blank=True, verbose_name="ایمیل")
    
    is_staff = models.BooleanField(default=False, verbose_name="کارمند")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    phone_2_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="شماره تلفن دوم")
    SEX_CHOICES = [('male', 'مرد'), ('female', 'زن')]
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, blank=True, null=True, verbose_name="جنسیت")
    birthday = models.DateField(blank=True, null=True, verbose_name="تاریخ تولد")
    country = models.CharField(max_length=50, blank=True, null=True, verbose_name="کشور")
    state_province = models.CharField(max_length=50, blank=True, null=True, verbose_name="استان")
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name="شهر")
    full_address = models.TextField(blank=True, null=True, verbose_name="آدرس کامل")
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="کد پستی")
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True, verbose_name="عکس")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}" or self.phone_number

class Apollonyar(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="نام")
    last_name = models.CharField(max_length=100, verbose_name="نام خانوادگی")
    phone_number = models.CharField(max_length=15, unique=True, verbose_name="شماره تلفن")
    password = models.CharField(max_length=128, verbose_name="رمز عبور")
    telegram_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="آیدی تلگرام")
    is_admin = models.BooleanField(default=False, verbose_name="آیا ادمین است؟")
    is_blocked = models.BooleanField(default=False, verbose_name="مسدود شده؟")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# === 2. ساختار آموزشی ===

class Course(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دوره")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")

    def __str__(self):
        return self.name

class Term(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='terms', verbose_name="دوره")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت")
    name = models.CharField(max_length=100, verbose_name="نام ترم")
    start_date = models.DateField(verbose_name="تاریخ شروع")
    end_date = models.DateField(verbose_name="تاریخ پایان")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")

    def __str__(self):
        return f"{self.course.name} - {self.name}"

class Group(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='groups', verbose_name="ترم")
    title = models.CharField(max_length=100, verbose_name="عنوان گروه")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")

    def __str__(self):
        return self.title

class AssignmentDef(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='assignment_defs', verbose_name="ترم")
    title = models.CharField(max_length=200, verbose_name="عنوان تکلیف")
    deadline = models.DateTimeField(verbose_name="مهلت ارسال")
    is_required = models.BooleanField(default=True, verbose_name="آیا الزامی است؟")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")

    def __str__(self):
        return self.title

class AssignmentDefTemplate(models.Model):
    assignment_def = models.ForeignKey(AssignmentDef, on_delete=models.CASCADE, related_name='templates', verbose_name="تعریف تکلیف")
    title = models.CharField(max_length=100, verbose_name="عنوان فایل الگو")
    file = models.FileField(upload_to='assignment_templates/', verbose_name="فایل")
    is_help_file = models.BooleanField(default=False, verbose_name="آیا فایل راهنما است؟")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")
    
    def __str__(self):
        return f"{self.assignment_def.title} - {self.title}"

class CallDef(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='call_defs', verbose_name="ترم")
    title = models.CharField(max_length=200, verbose_name="موضوع تماس")
    start_due_date = models.DateTimeField(verbose_name="تاریخ شروع موعد")
    end_due_date = models.DateTimeField(verbose_name="تاریخ پایان موعد")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")
    
    def __str__(self):
        return self.title

# === 3. پروفایل هنرجو و وضعیت‌ها ===

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles', verbose_name="کاربر هنرجو")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='profiles', verbose_name="دوره")
    term = models.ForeignKey(Term, on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles', verbose_name="ترم")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles', verbose_name="گروه")
    apollonyar = models.ForeignKey(Apollonyar, on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles', verbose_name="آپولون‌یار")
    sales_representative = models.ForeignKey(Apollonyar, on_delete=models.SET_NULL, null=True, blank=True, related_name='sold_profiles', verbose_name="نماینده فروش")

    TYPE_CHOICES = [('term-based', 'ترمی'), ('self-study', 'خودخوان')]
    STATUS_CHOICES = [('active', 'فعال'), ('suspended', 'معلق'), ('optout', 'انصراف')]
    
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='term-based', verbose_name="نوع")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="وضعیت")
    hearts = models.PositiveSmallIntegerField(default=3, verbose_name="جان")
    stars = models.FloatField(default=0.0, verbose_name="ستاره")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")

    def __str__(self):
        return f"پروفایل {self.user.get_full_name()} برای دوره {self.course.name}"

# === 4. مدال‌ها و تخفیف‌ها ===

class MedalDef(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان مدال")
    description = models.TextField(verbose_name="توضیحات")
    icon = models.FileField(upload_to='medal_icons/', verbose_name="آیکون SVG")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")

    def __str__(self):
        return self.title

class Medal(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='medals', verbose_name="پروفایل")
    medal_def = models.ForeignKey(MedalDef, on_delete=models.CASCADE, related_name='awards', verbose_name="مدال")
    giver_apollonyar = models.ForeignKey(Apollonyar, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="اعطا کننده")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="زمان اعطا")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")

class DiscountCode(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="کد تخفیف")
    cash_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="تخفیف نقدی")
    installment_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="تخفیف قسطی")
    max_usage = models.PositiveIntegerField(default=1, verbose_name="حداکثر استفاده")
    expiration_date = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ انقضا")
    usage_count = models.PositiveIntegerField(default=0, verbose_name="تعداد استفاده شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")

    def __str__(self):
        return self.code

# === 5. مالی ===

class Transaction(models.Model):
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions', verbose_name="کاربر هدف")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="مبلغ")
    TYPE_CHOICES = [('deposit', 'واریز'), ('withdrawal', 'برداشت')]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="نوع")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="زمان ثبت")
    reference_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="شماره پیگیری")
    METHOD_CHOICES = [('gateway', 'درگاه'), ('card', 'کارت به کارت'), ('paya', 'پایا')]
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name="روش پرداخت")
    VERIFICATION_CHOICES = [('pending', 'در انتظار'), ('valid', 'معتبر'), ('invalid', 'نامعتبر')]
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='pending', verbose_name="وضعیت تایید")
    verification_timestamp = models.DateTimeField(blank=True, null=True, verbose_name="زمان تایید")
    receipt_image = models.ImageField(upload_to='receipts/', blank=True, null=True, verbose_name="عکس رسید")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")

class TransactionNote(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='notes', verbose_name="تراکنش")
    author_apollonyar = models.ForeignKey(Apollonyar, on_delete=models.SET_NULL, null=True, verbose_name="نویسنده")
    note = models.TextField(verbose_name="یادداشت")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="زمان")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")

class Installment(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='installments', verbose_name="پروفایل")
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="تراکنش پرداخت")
    
    STATUS_CHOICES = [('pending', 'در انتظار'), ('paid', 'پرداخت شده'), ('refund', 'عودت شده')]
    
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="مبلغ قسط")
    due_date = models.DateField(verbose_name="تاریخ سررسید")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    is_splited = models.BooleanField(default=False, verbose_name="آیا شکسته شده؟")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")

# === 6. فعالیت‌های هنرجو و آپولون‌یار ===

class Assignment(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='assignments', verbose_name="پروفایل")
    assignment_def = models.ForeignKey(AssignmentDef, on_delete=models.CASCADE, verbose_name="تکلیف")
    deadline = models.DateTimeField(verbose_name="مهلت ارسال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions', verbose_name="تکلیف")
    assessor_apollonyar = models.ForeignKey(Apollonyar, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="ارزیاب")
    submission_timestamp = models.DateTimeField(auto_now_add=True, verbose_name="زمان ارسال")
    grade = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="نمره")
    feedback = models.TextField(blank=True, null=True, verbose_name="بازخورد")
    assessment_timestamp = models.DateTimeField(null=True, blank=True, verbose_name="زمان ارزیابی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")

class AssignmentSubmissionFile(models.Model):
    submission = models.ForeignKey(AssignmentSubmission, on_delete=models.CASCADE, related_name='files', verbose_name="ارسال")
    template = models.ForeignKey(AssignmentDefTemplate, on_delete=models.CASCADE, verbose_name="فایل الگو")
    file = models.FileField(upload_to='submission_files/', verbose_name="فایل ارسالی")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")

class Call(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='calls', verbose_name="پروفایل")
    call_def = models.ForeignKey(CallDef, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="تعریف تماس")
    caller = models.ForeignKey(Apollonyar, on_delete=models.SET_NULL, null=True, verbose_name="تماس گیرنده")

    TYPE_CHOICES = [('course', 'دوره'), ('installment', 'قسط'), ('cancellation', 'انصراف'), ('other', 'غیره')]
    STATUS_CHOICES = [('pending', 'در انتظار'), ('not_answered', 'بی‌پاسخ'), ('successful', 'موفق'), ('lost', 'سوخته')]
    
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="نوع تماس")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    call_timestamp = models.DateTimeField(verbose_name="زمان تماس")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")

class Note(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='general_notes', verbose_name="پروفایل")
    author_apollonyar = models.ForeignKey(Apollonyar, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="نویسنده")
    note = models.TextField(verbose_name="یادداشت")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="زمان")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")

class Log(models.Model):
    action = models.CharField(max_length=255, verbose_name="اقدام")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="زمان")
    issuer_apollonyar = models.ForeignKey(Apollonyar, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="انجام دهنده")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")