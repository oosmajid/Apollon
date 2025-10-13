# api/views.py

import random
from rest_framework import generics, status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    MyTokenObtainPairSerializer, OTPRequestSerializer, OTPVerifySerializer,
    UserRegistrationSerializer, CourseSerializer, TermSerializer,
    ApollonyarSerializer, GroupSerializer, MedalDefSerializer, DiscountCodeSerializer,
    AssignmentDefSerializer, CallDefSerializer, ProfileSerializer,
    AssignmentSerializer, CallSerializer, NoteSerializer,
    CallCreateSerializer, NoteCreateSerializer,
    AssignmentSubmissionCreateSerializer, AssignmentGradeSerializer
    )
from .models import (
    User, OTPCode, Course, Term, Apollonyar, Group,
    MedalDef, DiscountCode, AssignmentDef, CallDef, Profile,
    Assignment, AssignmentSubmission
    )

class UserRegistrationView(generics.CreateAPIView):
    """
    یک API endpoint برای ثبت‌نام کاربران جدید.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,) # به همه اجازه دسترسی به این endpoint را می‌دهیم
    serializer_class = UserRegistrationSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    """
    View سفارشی برای لاگین که از Serializer جدید ما استفاده می‌کند.
    """
    serializer_class = MyTokenObtainPairSerializer

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class OTPRequestView(generics.GenericAPIView):
    """
    یک کد OTP برای شماره تلفن داده شده ایجاد و (فعلا) در کنسول چاپ می‌کند.
    """
    permission_classes = [AllowAny]
    serializer_class = OTPRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']

        # تولید کد ۶ رقمی تصادفی
        otp_code = str(random.randint(100000, 999999))
        
        # حذف کدهای قبلی برای این شماره
        OTPCode.objects.filter(phone_number=phone_number).delete()
        # ذخیره کد جدید
        OTPCode.objects.create(phone_number=phone_number, code=otp_code)
        
        # در دنیای واقعی، اینجا کد را با SMS ارسال می‌کنیم
        # اما برای تست، آن را در کنسول پرینت می‌کنیم
        print(f"OTP Code for {phone_number} is: {otp_code}")

        return Response({"message": "کد تایید با موفقیت ارسال شد."}, status=status.HTTP_200_OK)


class OTPVerifyView(generics.GenericAPIView):
    """
    کد OTP را تایید کرده و در صورت صحت، توکن‌های JWT را برمی‌گرداند.
    """
    permission_classes = [AllowAny]
    serializer_class = OTPVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']

        try:
            otp_obj = OTPCode.objects.get(phone_number=phone_number, code=code)
        except OTPCode.DoesNotExist:
            return Response({"error": "کد وارد شده صحیح نیست."}, status=status.HTTP_400_BAD_REQUEST)

        if otp_obj.is_expired():
            return Response({"error": "کد منقضی شده است، لطفا مجددا درخواست دهید."}, status=status.HTTP_400_BAD_REQUEST)
        
        # پیدا کردن کاربر یا ساخت کاربر جدید
        user, created = User.objects.get_or_create(phone_number=phone_number)
        
        # حذف کد استفاده شده
        otp_obj.delete()

        tokens = get_tokens_for_user(user)
        return Response(tokens, status=status.HTTP_200_OK)

class CourseViewSet(viewsets.ModelViewSet):
    """
    یک ViewSet کامل برای مشاهده و ویرایش دوره‌ها.
    این ViewSet به صورت خودکار عملیات list, create, retrieve, update, destroy را فراهم می‌کند.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    # فقط کاربران ادمین (is_staff) به این API دسترسی دارند
    permission_classes = [permissions.IsAdminUser] 

class TermViewSet(viewsets.ModelViewSet):
    """API برای مدیریت ترم‌ها"""
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    permission_classes = [permissions.IsAdminUser]

class ApollonyarViewSet(viewsets.ModelViewSet):
    """API برای مدیریت آپولون‌یارها"""
    queryset = Apollonyar.objects.all()
    serializer_class = ApollonyarSerializer
    permission_classes = [permissions.IsAdminUser]

class GroupViewSet(viewsets.ModelViewSet):
    """API برای مدیریت گروه‌ها"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]

class MedalDefViewSet(viewsets.ModelViewSet):
    """API برای مدیریت تعاریف مدال‌ها"""
    queryset = MedalDef.objects.all()
    serializer_class = MedalDefSerializer
    permission_classes = [permissions.IsAdminUser]

class DiscountCodeViewSet(viewsets.ModelViewSet):
    """API برای مدیریت کدهای تخفیف"""
    queryset = DiscountCode.objects.all()
    serializer_class = DiscountCodeSerializer
    permission_classes = [permissions.IsAdminUser]

class AssignmentDefViewSet(viewsets.ModelViewSet):
    """API برای مدیریت تعاریف تکالیف"""
    queryset = AssignmentDef.objects.all()
    serializer_class = AssignmentDefSerializer
    permission_classes = [permissions.IsAdminUser]

class CallDefViewSet(viewsets.ModelViewSet):
    """API برای مدیریت تعاریف تماس‌ها"""
    queryset = CallDef.objects.all()
    serializer_class = CallDefSerializer
    permission_classes = [permissions.IsAdminUser]

class ProfileViewSet(viewsets.ModelViewSet):
    """API برای مشاهده و مدیریت پروفایل هنرجویان"""
    queryset = Profile.objects.select_related(
        'user', 'course', 'term', 'group', 'apollonyar', 'sales_representative'
    ).all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAdminUser] # فعلا فقط ادمین دسترسی دارد

    # === اکشن جدید برای دریافت تکالیف ===
    @action(detail=True, methods=['get'])
    def assignments(self, request, pk=None):
        """
        یک endpoint سفارشی برای دریافت لیست تکالیف یک پروفایل خاص.
        این اکشن در آدرس /api/profiles/{id}/assignments/ در دسترس خواهد بود.
        """
        profile = self.get_object() # پروفایل مورد نظر را بر اساس id پیدا می‌کند
        assignments = profile.assignments.all().order_by('deadline') # تمام تکالیف مرتبط با این پروفایل
        serializer = AssignmentSerializer(assignments, many=True)
        return Response(serializer.data)

    # === اکشن جدید برای دریافت تماس‌ها ===
    @action(detail=True, methods=['get'])
    def calls(self, request, pk=None):
        """
        دریافت لیست تماس‌های یک پروفایل خاص.
        آدرس: /api/profiles/{id}/calls/
        """
        profile = self.get_object()
        calls = profile.calls.all().order_by('-call_timestamp') # تماس‌های مرتبط، مرتب‌شده بر اساس جدیدترین
        serializer = CallSerializer(calls, many=True)
        return Response(serializer.data)

    # === اکشن جدید برای دریافت یادداشت‌ها ===
    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None):
        """
        دریافت لیست یادداشت‌های عمومی یک پروفایل خاص.
        آدرس: /api/profiles/{id}/notes/
        """
        profile = self.get_object()
        notes = profile.general_notes.all().order_by('-timestamp') # یادداشت‌های مرتبط، مرتب‌شده بر اساس جدیدترین
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)

    # === اکشن جدید برای ثبت تماس ===
    @action(detail=True, methods=['post'])
    def log_call(self, request, pk=None):
        """
        ثبت یک تماس جدید برای یک پروفایل خاص.
        آدرس: POST /api/profiles/{id}/log_call/
        """
        profile = self.get_object()
        serializer = CallCreateSerializer(data=request.data)
        if serializer.is_valid():
            # کاربر لاگین کرده (آپولون‌یار) را به عنوان تماس‌گیرنده ثبت می‌کنیم
            # **نکته:** فرض کردیم آپولون‌یارها با مدل User جنگو لاگین می‌کنند
            # اگر با مدل Apollonyar لاگین می‌کنند، این بخش نیاز به تغییر دارد
            
            # فعلا برای سادگی، caller را خالی می‌گذاریم
            # در فاز بعدی سیستم دسترسی‌ها را کامل می‌کنیم
            serializer.save(profile=profile) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # === اکشن جدید برای ثبت یادداشت ===
    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """
        ثبت یک یادداشت جدید برای یک پروفایل خاص.
        آدرس: POST /api/profiles/{id}/add_note/
        """
        profile = self.get_object()
        serializer = NoteCreateSerializer(data=request.data)
        if serializer.is_valid():
            # مانند بالا، نویسنده یادداشت را بعدا بر اساس کاربر لاگین کرده تنظیم می‌کنیم
            serializer.save(profile=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API برای مشاهده تکالیف.
    فقط خواندنی است چون تکالیف به صورت خودکار برای هنرجویان ساخته می‌شوند.
    """
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    # در فاز بعدی دسترسی‌ها را دقیق‌تر می‌کنیم (فقط هنرجوی مربوطه یا ادمین)
    permission_classes = [permissions.IsAuthenticated]

    # اکشن سفارشی برای ارسال یک تکلیف جدید
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        ایجاد یک Submission جدید برای یک تکلیف خاص.
        آدرس: POST /api/assignments/{id}/submit/
        """
        assignment = self.get_object()
        serializer = AssignmentSubmissionCreateSerializer(data=request.data)
        if serializer.is_valid():
            # assignment را به صورت خودکار به داده‌های سریالایزر اضافه می‌کنیم
            serializer.save(assignment=assignment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssignmentSubmissionViewSet(viewsets.GenericViewSet):
    """API برای مدیریت ارسال‌های تکالیف (مانند نمره‌دهی)."""
    queryset = AssignmentSubmission.objects.all()
    # دسترسی فقط برای آپولون‌یارها و ادمین‌ها
    permission_classes = [permissions.IsAdminUser] 

    @action(detail=True, methods=['post'])
    def grade(self, request, pk=None):
        """
        ثبت نمره و بازخورد برای یک Submission.
        آدرس: POST /api/submissions/{id}/grade/
        """
        submission = self.get_object()
        serializer = AssignmentGradeSerializer(instance=submission, data=request.data)
        if serializer.is_valid():
            serializer.save(
                assessor_apollonyar=request.user.apollonyar, # فرض می‌کنیم آپولون‌یار لاگین کرده
                assessment_timestamp=timezone.now()
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)