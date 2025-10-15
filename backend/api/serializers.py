# api/serializers.py

from rest_framework import serializers
from .models import (
    User, Course, Term, Apollonyar, Group, MedalDef, DiscountCode,
    AssignmentDef, CallDef, Profile, AssignmentSubmissionFile, AssignmentSubmission, Assignment,
    Call, Note, Transaction, TransactionNote, Installment
    )
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای ثبت‌نام کاربر جدید (هنرجو).
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = [
            'phone_number', 
            'password', 
            'first_name', 
            'last_name', 
            'email'
        ] # فیلدهایی که از فرم ثبت‌نام دریافت می‌شوند

    def create(self, validated_data):
        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', '')
        )
        return user

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer سفارشی برای لاگین با phone_number به جای username
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # اضافه کردن اطلاعات کاربر به توکن
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['phone_number'] = user.phone_number
        
        return token

    def validate(self, attrs):
        # اعتبارسنجی اصلی
        data = super().validate(attrs)
        
        # اضافه کردن اطلاعات کاربر به پاسخ
        data['user'] = {
            'id': self.user.id,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'phone_number': self.user.phone_number,
            'email': self.user.email
        }
        
        return data

    # این متد دیگر username را در فیلدهای سریالایزر نشان نمی‌دهد
    def get_fields(self):
        fields = super().get_fields()
        # حذف فیلد username و جایگزینی آن با phone_number
        fields.pop('username', None)
        fields['phone_number'] = serializers.CharField()
        return fields

class OTPRequestSerializer(serializers.Serializer):
    """
    سریالایزر برای اعتبارسنجی شماره تلفن در هنگام درخواست OTP.
    """
    phone_number = serializers.CharField(max_length=15)

class OTPVerifySerializer(serializers.Serializer):
    """
    سریالایزر برای اعتبارسنجی شماره تلفن و کد OTP.
    """
    phone_number = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)


class UserSerializerForProfile(serializers.ModelSerializer):
    """سریالایزر خلاصه‌ای از کاربر برای نمایش در پروفایل."""
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'email', 'photo']

class CourseSerializerForProfile(serializers.ModelSerializer):
    """سریالایزر خلاصه‌ای از دوره."""
    class Meta:
        model = Course
        fields = ['id', 'name']

class TermSerializerForProfile(serializers.ModelSerializer):
    """سریالایزر خلاصه‌ای از ترم همراه با دوره آن."""
    course = CourseSerializerForProfile(read_only=True)
    class Meta:
        model = Term
        fields = ['id', 'name', 'start_date', 'end_date', 'course']

class GroupSerializerForProfile(serializers.ModelSerializer):
    """سریالایزر خلاصه‌ای از گروه."""
    class Meta:
        model = Group
        fields = ['id', 'title']

class ApollonyarSerializerForProfile(serializers.ModelSerializer):
    """سریالایزر خلاصه‌ای از آپولون‌یار."""
    class Meta:
        model = Apollonyar
        fields = ['id', 'first_name', 'last_name', 'telegram_id']

# --- سریالایزر اصلی پروفایل ---

class ProfileSerializer(serializers.ModelSerializer):
    """
    سریالایزر کامل برای نمایش لیست یا جزئیات پروفایل هنرجویان.
    این سریالایزر اطلاعات را از مدل‌های مختلف جمع‌آوری می‌کند.
    """
    user = UserSerializerForProfile(read_only=True)
    term = TermSerializerForProfile(read_only=True)
    group = GroupSerializerForProfile(read_only=True)
    apollonyar = ApollonyarSerializerForProfile(read_only=True)
    sales_representative = ApollonyarSerializerForProfile(read_only=True)
    
    # برای اینکه بتوانیم هنگام ساخت یا ویرایش، فقط ID را ارسال کنیم
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    term_id = serializers.PrimaryKeyRelatedField(
        queryset=Term.objects.all(), source='term', write_only=True, allow_null=True
    )
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), source='group', write_only=True, allow_null=True
    )
    apollonyar_id = serializers.PrimaryKeyRelatedField(
        queryset=Apollonyar.objects.all(), source='apollonyar', write_only=True, allow_null=True
    )
    
    # فیلدهای اضافی برای سازگاری با فرانت‌اند
    name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    birthYear = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    studentType = serializers.SerializerMethodField()
    enrollmentStatus = serializers.SerializerMethodField()
    accessStatus = serializers.SerializerMethodField()
    term = serializers.SerializerMethodField()
    termStartDate = serializers.SerializerMethodField()
    termEndDate = serializers.SerializerMethodField()
    apollonyar = serializers.SerializerMethodField()
    apollonyarTelegramId = serializers.SerializerMethodField()
    apollonyarId = serializers.SerializerMethodField()
    courseId = serializers.SerializerMethodField()
    totalCourseFee = serializers.SerializerMethodField()
    earnedMedalIds = serializers.SerializerMethodField()
    actionLogs = serializers.SerializerMethodField()
    enrolledCourses = serializers.SerializerMethodField()
    watchTime = serializers.SerializerMethodField()
    totalWatchTime = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'term', 'group', 'apollonyar', 'sales_representative',
            'type', 'status', 'hearts', 'stars', 'created_at', 'updated_at',
            'user_id', 'term_id', 'group_id', 'apollonyar_id', # فیلدهای write-only
            'name', 'phone', 'birthYear', 'city', 'studentType', 'enrollmentStatus',
            'accessStatus', 'term', 'termStartDate', 'termEndDate', 'apollonyar',
            'apollonyarTelegramId', 'apollonyarId', 'courseId', 'totalCourseFee',
            'earnedMedalIds', 'actionLogs', 'enrolledCourses', 'watchTime',
            'totalWatchTime', 'score'
        ]
    
    def get_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return "نامشخص"
    
    def get_phone(self, obj):
        return obj.user.phone_number if obj.user else "نامشخص"
    
    def get_birthYear(self, obj):
        # دریافت سال تولد از اطلاعات کاربر
        if obj.user and obj.user.birthday:
            return obj.user.birthday.year
        return None
    
    def get_city(self, obj):
        # دریافت شهر از اطلاعات کاربر
        if obj.user and obj.user.city:
            return obj.user.city
        return None
    
    def get_studentType(self, obj):
        type_map = {
            'term-based': 'ترمی',
            'self-study': 'خودخوان'
        }
        return type_map.get(obj.type, obj.type)
    
    def get_enrollmentStatus(self, obj):
        # این فیلد نیاز به پیاده‌سازی دارد - فعلاً بر اساس وضعیت
        status_map = {
            'active': 'آزاد',
            'suspended': 'مسدود',
            'optout': 'انصراف'
        }
        return status_map.get(obj.status, obj.status)
    
    def get_accessStatus(self, obj):
        # این فیلد نیاز به پیاده‌سازی دارد - فعلاً بر اساس وضعیت
        status_map = {
            'active': 'فعال',
            'suspended': 'غیرفعال',
            'optout': 'غیرفعال'
        }
        return status_map.get(obj.status, 'غیرفعال')
    
    def get_term(self, obj):
        return obj.term.name if obj.term else "نامشخص"
    
    def get_termStartDate(self, obj):
        # دریافت تاریخ شروع ترم
        if obj.term and obj.term.start_date:
            return obj.term.start_date.strftime('%Y/%m/%d')
        return None
    
    def get_termEndDate(self, obj):
        # دریافت تاریخ پایان ترم
        if obj.term and obj.term.end_date:
            return obj.term.end_date.strftime('%Y/%m/%d')
        return None
    
    def get_apollonyar(self, obj):
        if obj.apollonyar:
            return f"{obj.apollonyar.first_name} {obj.apollonyar.last_name}".strip()
        return "نامشخص"
    
    def get_apollonyarTelegramId(self, obj):
        return obj.apollonyar.telegram_id if obj.apollonyar else None
    
    def get_apollonyarId(self, obj):
        return obj.apollonyar.id if obj.apollonyar else None
    
    def get_courseId(self, obj):
        return obj.term.course.id if obj.term and obj.term.course else None
    
    def get_totalCourseFee(self, obj):
        # محاسبه کل مبلغ دوره بر اساس اقساط
        if obj.term:
            return float(obj.term.price) if obj.term.price else 0
        return 0
    
    def get_earnedMedalIds(self, obj):
        # دریافت مدال‌های کسب شده توسط پروفایل
        from .models import Medal
        medals = Medal.objects.filter(profile=obj)
        return [medal.medal_def.id for medal in medals]
    
    def get_actionLogs(self, obj):
        # دریافت لاگ‌های مربوط به این پروفایل
        from .models import Log
        logs = Log.objects.all().order_by('-timestamp')[:20]  # آخرین 20 لاگ
        return LogSerializer(logs, many=True).data
    
    def get_enrolledCourses(self, obj):
        # دریافت دوره‌های ثبت‌نام شده پروفایل
        enrolled_courses = []
        
        # در حال حاضر هر پروفایل فقط یک دوره دارد
        if obj.term and obj.term.course:
            enrolled_courses.append({
                'courseId': obj.term.course.id,
                'courseName': obj.term.course.name,
                'termId': obj.term.id,
                'termName': obj.term.name,
                'enrollmentId': obj.id  # استفاده از ID پروفایل به عنوان enrollment ID
            })
        
        return enrolled_courses
    
    def get_watchTime(self, obj):
        # این فیلد نیاز به پیاده‌سازی دارد - فعلاً 0 برمی‌گردانیم
        return 0
    
    def get_totalWatchTime(self, obj):
        # این فیلد نیاز به پیاده‌سازی دارد - فعلاً 0 برمی‌گردانیم
        return 0
    
    def get_score(self, obj):
        return obj.stars if obj.stars else 0

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = '__all__'

class ApollonyarSerializer(serializers.ModelSerializer):
    # برای اینکه پسورد هنگام خواندن اطلاعات نمایش داده نشود
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Apollonyar
        fields = '__all__'
    
    # متد create را بازنویسی می‌کنیم تا پسورد هش شود
    def create(self, validated_data):
        # در جنگو، پسوردها باید هش شوند. فعلا برای سادگی آن را مستقیم ذخیره می‌کنیم
        # در فازهای بعدی این بخش را امن خواهیم کرد
        apollonyar = Apollonyar.objects.create(**validated_data)
        return apollonyar

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class MedalDefSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()
    name = serializers.CharField(source='title')
    
    class Meta:
        model = MedalDef
        fields = ['id', 'name', 'title', 'description', 'icon']
    
    def get_icon(self, obj):
        # اگر آیکون آپلود شده باشد، URL آن را برگردان
        if obj.icon and hasattr(obj.icon, 'url'):
            return obj.icon.url
        
        # اگر آیکون آپلود نشده باشد، آیکون پیش‌فرض بر اساس نام مدال برگردان
        return 'fa-solid fa-award'

class DiscountCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCode
        fields = '__all__'

class AssignmentDefSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentDef
        fields = '__all__'

class CallDefSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallDef
        fields = '__all__'

class AssignmentSubmissionFileSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش فایل‌های ارسالی یک تکلیف."""
    class Meta:
        model = AssignmentSubmissionFile
        fields = ['id', 'file', 'description']

class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش تاریخچه ارسال‌های یک تکلیف."""
    files = AssignmentSubmissionFileSerializer(many=True, read_only=True)
    assessor_apollonyar = ApollonyarSerializerForProfile(read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = [
            'id', 'submission_timestamp', 'grade', 'feedback', 
            'assessment_timestamp', 'assessor_apollonyar', 'files'
        ]

class AssignmentSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای نمایش لیست تکالیف با اطلاعات کامل پروفایل.
    """
    assignment_def = serializers.StringRelatedField() # فقط عنوان تکلیف را نمایش می‌دهد
    submissions = AssignmentSubmissionSerializer(many=True, read_only=True)
    
    # اطلاعات پروفایل
    profile = ProfileSerializer(read_only=True)
    
    # فیلدهای اضافی برای سازگاری با فرانت‌اند
    studentName = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    assignmentTitle = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    term = serializers.SerializerMethodField()
    studentId = serializers.SerializerMethodField()
    apollonyar = serializers.SerializerMethodField()
    submissionDate = serializers.SerializerMethodField()
    reviewDate = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'id', 'assignment_def', 'deadline', 'submissions', 'profile',
            'studentName', 'phone', 'assignmentTitle', 'course', 'term', 
            'studentId', 'apollonyar', 'submissionDate', 'reviewDate', 
            'status', 'grade'
        ]
    
    def get_studentName(self, obj):
        if obj.profile and obj.profile.user:
            return f"{obj.profile.user.first_name} {obj.profile.user.last_name}".strip()
        return "نامشخص"
    
    def get_phone(self, obj):
        return obj.profile.user.phone_number if obj.profile and obj.profile.user else "نامشخص"
    
    def get_assignmentTitle(self, obj):
        return obj.assignment_def.title if obj.assignment_def else "نامشخص"
    
    def get_course(self, obj):
        return obj.profile.term.course.name if obj.profile and obj.profile.term and obj.profile.term.course else "نامشخص"
    
    def get_term(self, obj):
        return obj.profile.term.name if obj.profile and obj.profile.term else "نامشخص"
    
    def get_studentId(self, obj):
        return obj.profile.id if obj.profile else None
    
    def get_apollonyar(self, obj):
        if obj.profile and obj.profile.apollonyar:
            return f"{obj.profile.apollonyar.first_name} {obj.profile.apollonyar.last_name}".strip()
        return "نامشخص"
    
    def get_submissionDate(self, obj):
        submissions = obj.submissions.all()
        if submissions.exists():
            # آخرین submission را برمی‌گردانیم
            latest_submission = submissions.first()
            return latest_submission.submission_timestamp.strftime('%Y-%m-%d %H:%M')
        return None
    
    def get_reviewDate(self, obj):
        submissions = obj.submissions.all()
        if submissions.exists():
            latest_submission = submissions.first()
            if latest_submission.assessment_timestamp:
                return latest_submission.assessment_timestamp.strftime('%Y-%m-%d %H:%M')
        return None
    
    def get_status(self, obj):
        submissions = obj.submissions.all()
        if submissions.exists():
            latest_submission = submissions.first()
            if latest_submission.grade is not None:
                return "بررسی شده"
            else:
                return "در انتظار بررسی"
        return "ارسال نشده"
    
    def get_grade(self, obj):
        submissions = obj.submissions.all()
        if submissions.exists():
            latest_submission = submissions.first()
            if latest_submission.grade is not None:
                return latest_submission.grade
        return None

class CallSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش لیست تماس‌ها با اطلاعات کامل پروفایل."""
    # اطلاعات پروفایل
    profile = ProfileSerializer(read_only=True)
    # اطلاعات تماس‌گیرنده
    caller = ApollonyarSerializerForProfile(read_only=True) 
    # فقط عنوان تعریف تماس را نمایش می‌دهیم
    call_def = serializers.StringRelatedField() 
    
    # فیلدهای اضافی برای سازگاری با فرانت‌اند
    studentName = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()
    callStatus = serializers.SerializerMethodField()
    hearts = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    term = serializers.SerializerMethodField()
    studentId = serializers.SerializerMethodField()
    apollonyar = serializers.SerializerMethodField()

    class Meta:
        model = Call
        fields = [
            'id', 'type', 'status', 'call_timestamp', 'description',
            'profile', 'caller', 'call_def',
            'studentName', 'phone', 'topic', 'callStatus', 'hearts', 
            'course', 'term', 'studentId', 'apollonyar'
        ]
    
    def get_studentName(self, obj):
        if obj.profile and obj.profile.user:
            return f"{obj.profile.user.first_name} {obj.profile.user.last_name}".strip()
        return "نامشخص"
    
    def get_phone(self, obj):
        return obj.profile.user.phone_number if obj.profile and obj.profile.user else "نامشخص"
    
    def get_topic(self, obj):
        return obj.call_def.title if obj.call_def else obj.type
    
    def get_callStatus(self, obj):
        status_map = {
            'pending': 'در انتظار',
            'not_answered': 'بی‌پاسخ', 
            'successful': 'موفق',
            'lost': 'سوخته'
        }
        return status_map.get(obj.status, obj.status)
    
    def get_hearts(self, obj):
        return obj.profile.hearts if obj.profile else 0
    
    def get_course(self, obj):
        return obj.profile.term.course.name if obj.profile and obj.profile.term and obj.profile.term.course else "نامشخص"
    
    def get_term(self, obj):
        return obj.profile.term.name if obj.profile and obj.profile.term else "نامشخص"
    
    def get_studentId(self, obj):
        return obj.profile.id if obj.profile else None
    
    def get_apollonyar(self, obj):
        if obj.profile and obj.profile.apollonyar:
            return f"{obj.profile.apollonyar.first_name} {obj.profile.apollonyar.last_name}".strip()
        return "نامشخص"
    
class NoteSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش لیست یادداشت‌های یک پروفایل."""
    author_apollonyar = ApollonyarSerializerForProfile(read_only=True)
    date = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = [
            'id', 'note', 'timestamp', 'author_apollonyar', 'date', 'author'
        ]
    
    def get_date(self, obj):
        return obj.timestamp.strftime('%Y/%m/%d') if obj.timestamp else None
    
    def get_author(self, obj):
        if obj.author_apollonyar:
            return f"{obj.author_apollonyar.first_name} {obj.author_apollonyar.last_name}".strip()
        return "نامشخص"

class CallCreateSerializer(serializers.ModelSerializer):
    """سریالایزر برای ثبت یک تماس جدید برای یک پروفایل."""
    class Meta:
        model = Call
        # فیلدهایی که از فرانت‌اند دریافت می‌شوند
        fields = ['call_def', 'type', 'status', 'description', 'call_timestamp']

class NoteCreateSerializer(serializers.ModelSerializer):
    """سریالایزر برای ثبت یک یادداشت جدید برای یک پروفایل."""
    text = serializers.CharField(write_only=True, source='note', required=False)
    note = serializers.CharField(required=False)
    
    class Meta:
        model = Note
        fields = ['note', 'text'] # پشتیبانی از هر دو فرمت
    
    def validate(self, data):
        # اطمینان از اینکه حداقل یکی از فیلدها موجود باشد
        if not data.get('note') and not data.get('text'):
            raise serializers.ValidationError("Either 'note' or 'text' field is required")
        
        # اگر text موجود باشد، آن را به note تبدیل کن
        if 'text' in data and data['text']:
            data['note'] = data['text']
        
        return data

class LogSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش لاگ اقدامات."""
    issuer_name = serializers.SerializerMethodField()
    timestamp_formatted = serializers.SerializerMethodField()
    
    class Meta:
        from .models import Log
        model = Log
        fields = ['id', 'action', 'timestamp', 'description', 'issuer_name', 'timestamp_formatted']
    
    def get_issuer_name(self, obj):
        if obj.issuer_apollonyar:
            return f"{obj.issuer_apollonyar.first_name} {obj.issuer_apollonyar.last_name}".strip()
        return "سیستم"
    
    def get_timestamp_formatted(self, obj):
        return obj.timestamp.strftime('%Y/%m/%d %H:%M') if obj.timestamp else None

class AssignmentSubmissionFileCreateSerializer(serializers.ModelSerializer):
    """سریالایزر برای ایجاد فایل‌های یک Submission جدید."""
    class Meta:
        model = AssignmentSubmissionFile
        fields = ['template', 'file', 'description']

class AssignmentSubmissionCreateSerializer(serializers.ModelSerializer):
    """سریالایزر برای ایجاد یک Submission جدید به همراه فایل‌هایش."""
    files = AssignmentSubmissionFileCreateSerializer(many=True)

    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'assignment', 'files', 'submission_timestamp']
        read_only_fields = ['submission_timestamp']

    def create(self, validated_data):
        files_data = validated_data.pop('files')
        submission = AssignmentSubmission.objects.create(**validated_data)
        for file_data in files_data:
            AssignmentSubmissionFile.objects.create(submission=submission, **file_data)
        return submission

class AssignmentGradeSerializer(serializers.ModelSerializer):
    """سریالایزر برای ثبت نمره و بازخورد توسط آپولون‌یار."""
    class Meta:
        model = AssignmentSubmission
        fields = ['grade', 'feedback']

class TransactionNoteSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش یادداشت‌های یک تراکنش."""
    author_apollonyar = ApollonyarSerializerForProfile(read_only=True)

    class Meta:
        model = TransactionNote
        fields = ['id', 'note', 'timestamp', 'author_apollonyar']

class TransactionSerializer(serializers.ModelSerializer):
    """سریالایزر کامل برای نمایش لیست و جزئیات تراکنش‌ها."""
    target_user = UserSerializerForProfile(read_only=True)
    notes = TransactionNoteSerializer(many=True, read_only=True)
    
    # فیلدهای اضافی برای سازگاری با فرانت‌اند
    type = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    dateTime = serializers.SerializerMethodField()
    trackingNumber = serializers.SerializerMethodField()
    paymentMethod = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    receiptImageUrl = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'target_user', 'notes', 'reference_number', 'timestamp', 
            'payment_method', 'verification_status', 'verification_timestamp', 
            'receipt_image', 'created_at', 'updated_at',
            'type', 'amount', 'dateTime', 'trackingNumber', 'paymentMethod', 
            'status', 'receiptImageUrl'
        ]
    
    def get_type(self, obj):
        type_map = {
            'deposit': 'واریز',
            'withdrawal': 'برداشت'
        }
        return type_map.get(obj.type, obj.type)
    
    def get_amount(self, obj):
        return float(obj.amount) if obj.amount else 0
    
    def get_dateTime(self, obj):
        return obj.timestamp.strftime('%Y-%m-%d %H:%M') if obj.timestamp else None
    
    def get_trackingNumber(self, obj):
        return obj.reference_number or "نامشخص"
    
    def get_paymentMethod(self, obj):
        method_map = {
            'gateway': 'درگاه',
            'card': 'کارت به کارت',
            'paya': 'پایا'
        }
        return method_map.get(obj.payment_method, obj.payment_method)
    
    def get_status(self, obj):
        status_map = {
            'pending': 'در انتظار',
            'valid': 'تأیید',
            'invalid': 'رد'
        }
        return status_map.get(obj.verification_status, obj.verification_status)
    
    def get_receiptImageUrl(self, obj):
        if obj.receipt_image:
            return obj.receipt_image.url
        return None

class InstallmentSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش لیست اقساط با اطلاعات کامل پروفایل."""
    # اطلاعات پروفایل
    profile = ProfileSerializer(read_only=True)
    transaction = TransactionSerializer(read_only=True)
    
    # فیلدهای اضافی برای سازگاری با فرانت‌اند
    studentName = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    dueDate = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    daysRemaining = serializers.SerializerMethodField()
    paymentStatus = serializers.SerializerMethodField()
    term = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    apollonyar = serializers.SerializerMethodField()
    lastContactDate = serializers.SerializerMethodField()
    courseStatus = serializers.SerializerMethodField()
    studentId = serializers.SerializerMethodField()

    class Meta:
        model = Installment
        fields = [
            'id', 'profile', 'transaction', 'due_amount', 'due_date', 'status', 'is_splited',
            'studentName', 'phone', 'dueDate', 'amount', 'daysRemaining', 'paymentStatus',
            'term', 'course', 'apollonyar', 'lastContactDate', 'courseStatus', 'studentId'
        ]
    
    def get_studentName(self, obj):
        if obj.profile and obj.profile.user:
            return f"{obj.profile.user.first_name} {obj.profile.user.last_name}".strip()
        return "نامشخص"
    
    def get_phone(self, obj):
        return obj.profile.user.phone_number if obj.profile and obj.profile.user else "نامشخص"
    
    def get_dueDate(self, obj):
        return obj.due_date.strftime('%Y/%m/%d') if obj.due_date else None
    
    def get_amount(self, obj):
        return float(obj.due_amount) if obj.due_amount else 0
    
    def get_daysRemaining(self, obj):
        if obj.due_date:
            from datetime import date
            today = date.today()
            delta = (obj.due_date - today).days
            return delta
        return 0
    
    def get_paymentStatus(self, obj):
        status_map = {
            'pending': 'در انتظار',
            'paid': 'پرداخت شده',
            'refund': 'عودت شده'
        }
        return status_map.get(obj.status, obj.status)
    
    def get_term(self, obj):
        return obj.profile.term.name if obj.profile and obj.profile.term else "نامشخص"
    
    def get_course(self, obj):
        return obj.profile.term.course.name if obj.profile and obj.profile.term and obj.profile.term.course else "نامشخص"
    
    def get_apollonyar(self, obj):
        if obj.profile and obj.profile.apollonyar:
            return f"{obj.profile.apollonyar.first_name} {obj.profile.apollonyar.last_name}".strip()
        return "نامشخص"
    
    def get_lastContactDate(self, obj):
        # این فیلد نیاز به پیاده‌سازی دارد - فعلاً None برمی‌گردانیم
        return None
    
    def get_courseStatus(self, obj):
        # این فیلد نیاز به پیاده‌سازی دارد - فعلاً بر اساس وضعیت پروفایل
        if obj.profile:
            if obj.profile.status == 'active':
                return 'فعال'
            elif obj.profile.status == 'suspended':
                return 'مسدود'
            else:
                return 'نامشخص'
        return 'نامشخص'
    
    def get_studentId(self, obj):
        return obj.profile.id if obj.profile else None