# api/serializers.py

from rest_framework import serializers
from .models import User, Course, Term, Apollonyar, Group, MedalDef
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