# api/serializers.py

from rest_framework import serializers
from .models import (
    User, Course, Term, Apollonyar, Group, MedalDef, DiscountCode,
    AssignmentDef, CallDef, Profile, AssignmentSubmissionFile, AssignmentSubmission, Assignment, Call, Note
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

        # می‌توانید اطلاعات اضافی را در اینجا به توکن اضافه کنید
        # مثلا: token['first_name'] = user.first_name
        
        return token

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

    class Meta:
        model = Profile
        # تمام فیلدهای مدل Profile به همراه فیلدهای تودرتو
        fields = [
            'id', 'user', 'term', 'group', 'apollonyar', 'sales_representative',
            'type', 'status', 'hearts', 'stars', 'created_at', 'updated_at',
            'user_id', 'term_id', 'group_id', 'apollonyar_id' # فیلدهای write-only
        ]

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
    class Meta:
        model = MedalDef
        fields = '__all__'

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
    سریالایزر اصلی برای نمایش لیست تکالیف یک هنرجو در پروفایل.
    """
    assignment_def = serializers.StringRelatedField() # فقط عنوان تکلیف را نمایش می‌دهد
    submissions = AssignmentSubmissionSerializer(many=True, read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id', 'assignment_def', 'deadline', 'submissions'
        ]

class CallSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش لیست تماس‌های یک پروفایل."""
    # از سریالایزر خلاصه‌ای که قبلا ساختیم استفاده می‌کنیم
    caller = ApollonyarSerializerForProfile(read_only=True) 
    # فقط عنوان تعریف تماس را نمایش می‌دهیم
    call_def = serializers.StringRelatedField() 

    class Meta:
        model = Call
        fields = [
            'id', 'type', 'status', 'call_timestamp', 
            'description', 'caller', 'call_def'
        ]

class NoteSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش لیست یادداشت‌های یک پروفایل."""
    author_apollonyar = ApollonyarSerializerForProfile(read_only=True)

    class Meta:
        model = Note
        fields = [
            'id', 'note', 'timestamp', 'author_apollonyar'
        ]