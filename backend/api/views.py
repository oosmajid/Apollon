# api/views.py

import random
from django.utils import timezone
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
    AssignmentSubmissionCreateSerializer, AssignmentGradeSerializer,
    TransactionSerializer, InstallmentSerializer
    )
from .models import (
    User, OTPCode, Course, Term, Apollonyar, Group,
    MedalDef, DiscountCode, AssignmentDef, CallDef, Profile,
    Assignment, AssignmentSubmission, Transaction, Installment, Call, Log
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

def get_apollonyar_for_user(user):
    """
    پیدا کردن آپولون‌یار مربوط به کاربر لاگین کرده
    """
    if hasattr(user, 'phone_number') and user.phone_number:
        try:
            from .models import Apollonyar
            return Apollonyar.objects.get(phone_number=user.phone_number)
        except Apollonyar.DoesNotExist:
            # اگر آپولون‌یار پیدا نشد، آن را ایجاد کن
            from .models import Apollonyar
            apollonyar = Apollonyar.objects.create(
                first_name=user.first_name or 'کاربر',
                last_name=user.last_name or 'سیستم',
                phone_number=user.phone_number,
                password='default_password',
                telegram_id='',
                is_admin=True
            )
            return apollonyar
    
    # اگر شماره تلفن موجود نیست، اولین آپولون‌یار را به عنوان پیش‌فرض استفاده کن
    from .models import Apollonyar
    return Apollonyar.objects.first()

def log_action(apollonyar, action, description=""):
    """
    ثبت یک اقدام در جدول لاگ
    """
    from .models import Log
    Log.objects.create(
        action=action,
        issuer_apollonyar=apollonyar,
        description=description
    )

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

        # تولید کد ۴ رقمی تصادفی
        otp_code = str(random.randint(1000, 9999))
        
        # حذف کدهای قبلی برای این شماره
        OTPCode.objects.filter(phone_number=phone_number).delete()
        # ذخیره کد جدید
        OTPCode.objects.create(phone_number=phone_number, code=otp_code)
        
        # در دنیای واقعی، اینجا کد را با SMS ارسال می‌کنیم
        # اما برای تست، آن را در کنسول پرینت می‌کنیم
        print(f"OTP Code for {phone_number} is: {otp_code}")

        # برای تست، کد OTP را در پاسخ هم برمی‌گردانیم
        return Response({
            "message": "کد تایید با موفقیت ارسال شد.",
            "otp_code_for_test": otp_code  # فقط برای محیط تست
        }, status=status.HTTP_200_OK)


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
        
        # اضافه کردن اطلاعات کاربر به پاسخ
        response_data = {
            **tokens,
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
                'email': user.email
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

class UserMeView(generics.GenericAPIView):
    """
    دریافت اطلاعات کاربر فعلی
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number,
            'email': user.email
        })

class CourseViewSet(viewsets.ModelViewSet):
    """
    یک ViewSet کامل برای مشاهده و ویرایش دوره‌ها.
    این ViewSet به صورت خودکار عملیات list, create, retrieve, update, destroy را فراهم می‌کند.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    # تغییر: هر کاربر احراز هویت شده دسترسی دارد
    permission_classes = [permissions.IsAuthenticated] 

class TermViewSet(viewsets.ModelViewSet):
    """API برای مدیریت ترم‌ها"""
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    permission_classes = [permissions.IsAuthenticated]

class ApollonyarViewSet(viewsets.ModelViewSet):
    """API برای مدیریت آپولون‌یارها"""
    queryset = Apollonyar.objects.all()
    serializer_class = ApollonyarSerializer
    permission_classes = [permissions.IsAuthenticated]

class GroupViewSet(viewsets.ModelViewSet):
    """API برای مدیریت گروه‌ها"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class MedalDefViewSet(viewsets.ModelViewSet):
    """API برای مدیریت تعاریف مدال‌ها"""
    queryset = MedalDef.objects.all()
    serializer_class = MedalDefSerializer
    permission_classes = [permissions.IsAuthenticated]

class DiscountCodeViewSet(viewsets.ModelViewSet):
    """API برای مدیریت کدهای تخفیف"""
    queryset = DiscountCode.objects.all()
    serializer_class = DiscountCodeSerializer
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated] # تغییر: هر کاربر احراز هویت شده دسترسی دارد

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
            # پیدا کردن آپولون‌یار مربوط به کاربر لاگین کرده
            caller_apollonyar = get_apollonyar_for_user(request.user)
            call = serializer.save(profile=profile, caller=caller_apollonyar)
            
            # ثبت لاگ
            student_name = f"{profile.user.first_name} {profile.user.last_name}".strip() if profile.user else "نامشخص"
            call_type = call.get_type_display() if hasattr(call, 'get_type_display') else call.type
            log_action(
                caller_apollonyar,
                "ثبت تماس",
                f"تماس {call_type} برای هنرجو {student_name} ({profile.user.phone_number if profile.user else 'نامشخص'}) ثبت شد"
            )
            
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
            # پیدا کردن آپولون‌یار مربوط به کاربر لاگین کرده
            author_apollonyar = get_apollonyar_for_user(request.user)
            note = serializer.save(profile=profile, author_apollonyar=author_apollonyar)
            
            # ثبت لاگ
            student_name = f"{profile.user.first_name} {profile.user.last_name}".strip() if profile.user else "نامشخص"
            log_action(
                author_apollonyar,
                "افزودن یادداشت",
                f"یادداشت جدید برای هنرجو {student_name} ({profile.user.phone_number if profile.user else 'نامشخص'}) اضافه شد"
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # === اکشن جدید برای دریافت پرداخت‌ها ===
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """
        دریافت لیست اقساط و تراکنش‌های یک پروفایل خاص.
        آدرس: /api/profiles/{id}/payments/
        """
        profile = self.get_object()
        installments = profile.installments.all().order_by('due_date')
        transactions = Transaction.objects.filter(target_user=profile.user).order_by('-timestamp')
        
        # ترکیب اقساط و تراکنش‌ها برای نمایش در یک لیست
        payments_data = []
        
        # اضافه کردن اقساط
        for installment in installments:
            payment_data = {
                'id': f"installment_{installment.id}",
                'type': 'قسط',
                'amount': float(installment.due_amount),
                'date': installment.due_date.strftime('%Y/%m/%d'),
                'method': 'قسط',
                'status': installment.get_status_display(),
                'paymentStatus': installment.get_status_display(),
                'transactionId': installment.transaction.id if installment.transaction else None,
                'dueDate': installment.due_date.strftime('%Y/%m/%d')
            }
            payments_data.append(payment_data)
        
        # اضافه کردن تراکنش‌ها
        for transaction in transactions:
            payment_data = {
                'id': f"transaction_{transaction.id}",
                'type': transaction.get_type_display(),
                'amount': float(transaction.amount),
                'date': transaction.timestamp.strftime('%Y/%m/%d'),
                'method': transaction.get_payment_method_display(),
                'status': transaction.get_verification_status_display(),
                'paymentStatus': transaction.get_verification_status_display(),
                'transactionId': transaction.id,
                'dueDate': None
            }
            payments_data.append(payment_data)
        
        # مرتب‌سازی بر اساس تاریخ
        payments_data.sort(key=lambda x: x['date'], reverse=True)
        
        return Response(payments_data)

    # === اکشن جدید برای به‌روزرسانی اقساط ===
    @action(detail=True, methods=['patch'])
    def update_installments(self, request, pk=None):
        """
        به‌روزرسانی اقساط یک پروفایل خاص.
        آدرس: PATCH /api/profiles/{id}/update_installments/
        """
        profile = self.get_object()
        installments_data = request.data.get('installments', [])
        total_course_fee = request.data.get('totalCourseFee', 0)
        
        try:
            # حذف اقساط قبلی
            profile.installments.all().delete()
            
            # ایجاد اقساط جدید
            for installment_data in installments_data:
                Installment.objects.create(
                    profile=profile,
                    due_amount=installment_data.get('amount', 0),
                    due_date=installment_data.get('dueDate'),
                    status=installment_data.get('paymentStatus', 'pending').lower().replace(' ', '_'),
                    transaction_id=installment_data.get('transactionId') if installment_data.get('transactionId') else None
                )
            
            return Response({'message': 'اقساط با موفقیت به‌روزرسانی شد'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # === اکشن جدید برای اضافه کردن مدال ===
    @action(detail=True, methods=['post'])
    def add_medal(self, request, pk=None):
        """
        اضافه کردن مدال به یک پروفایل خاص.
        آدرس: POST /api/profiles/{id}/add_medal/
        """
        profile = self.get_object()
        medal_id = request.data.get('medalId')
        
        if not medal_id:
            return Response({'error': 'medalId الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from .models import Medal, MedalDef
            medal_def = MedalDef.objects.get(id=medal_id)
            
            # پیدا کردن آپولون‌یار مربوط به کاربر لاگین کرده
            giver_apollonyar = get_apollonyar_for_user(request.user)
            
            # بررسی اینکه آیا این مدال قبلاً اعطا شده یا نه
            if not Medal.objects.filter(profile=profile, medal_def=medal_def).exists():
                Medal.objects.create(
                    profile=profile,
                    medal_def=medal_def,
                    giver_apollonyar=giver_apollonyar
                )
                
                # ثبت لاگ
                student_name = f"{profile.user.first_name} {profile.user.last_name}".strip() if profile.user else "نامشخص"
                log_action(
                    giver_apollonyar,
                    "اعطای مدال",
                    f"مدال {medal_def.title} به هنرجو {student_name} ({profile.user.phone_number if profile.user else 'نامشخص'}) اعطا شد"
                )
                
                return Response({'message': 'مدال با موفقیت اضافه شد'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'این مدال قبلاً اعطا شده است'}, status=status.HTTP_400_BAD_REQUEST)
        except MedalDef.DoesNotExist:
            return Response({'error': 'مدال مورد نظر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # === اکشن جدید برای حذف مدال ===
    @action(detail=True, methods=['delete'])
    def remove_medal(self, request, pk=None):
        """
        حذف مدال از یک پروفایل خاص.
        آدرس: DELETE /api/profiles/{id}/remove_medal/{medal_id}/
        """
        profile = self.get_object()
        medal_id = request.data.get('medalId')
        
        if not medal_id:
            return Response({'error': 'medalId الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from .models import Medal
            medal = Medal.objects.get(profile=profile, medal_def_id=medal_id)
            
            # ثبت لاگ قبل از حذف
            apollonyar = get_apollonyar_for_user(request.user)
            student_name = f"{profile.user.first_name} {profile.user.last_name}".strip() if profile.user else "نامشخص"
            log_action(
                apollonyar,
                "حذف مدال",
                f"مدال {medal.medal_def.title} از هنرجو {student_name} ({profile.user.phone_number if profile.user else 'نامشخص'}) حذف شد"
            )
            
            medal.delete()
            return Response({'message': 'مدال با موفقیت حذف شد'}, status=status.HTTP_200_OK)
        except Medal.DoesNotExist:
            return Response({'error': 'مدال مورد نظر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # === اکشن جدید برای حذف یادداشت ===
    @action(detail=True, methods=['delete'])
    def remove_note(self, request, pk=None):
        """
        حذف یادداشت از یک پروفایل خاص.
        آدرس: DELETE /api/profiles/{id}/notes/{note_id}/
        """
        profile = self.get_object()
        note_id = request.data.get('noteId')
        
        if not note_id:
            return Response({'error': 'noteId الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            note = profile.general_notes.get(id=note_id)
            
            # ثبت لاگ قبل از حذف
            apollonyar = get_apollonyar_for_user(request.user)
            student_name = f"{profile.user.first_name} {profile.user.last_name}".strip() if profile.user else "نامشخص"
            log_action(
                apollonyar,
                "حذف یادداشت",
                f"یادداشت از هنرجو {student_name} ({profile.user.phone_number if profile.user else 'نامشخص'}) حذف شد"
            )
            
            note.delete()
            return Response({'message': 'یادداشت با موفقیت حذف شد'}, status=status.HTTP_200_OK)
        except Note.DoesNotExist:
            return Response({'error': 'یادداشت مورد نظر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # === اکشن جدید برای تغییر ترم ===
    @action(detail=True, methods=['patch'])
    def change_term(self, request, pk=None):
        """
        تغییر ترم یک پروفایل خاص.
        آدرس: PATCH /api/profiles/{id}/change_term/
        """
        profile = self.get_object()
        term_id = request.data.get('termId')
        reason = request.data.get('reason', '')
        
        if not term_id:
            return Response({'error': 'termId الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            term = Term.objects.get(id=term_id)
            old_term = profile.term
            
            # تغییر ترم
            profile.term = term
            profile.save()
            
            # ثبت لاگ
            apollonyar = get_apollonyar_for_user(request.user)
            student_name = f"{profile.user.first_name} {profile.user.last_name}".strip() if profile.user else "نامشخص"
            old_term_name = old_term.name if old_term else "نامشخص"
            new_term_name = term.name
            log_action(
                apollonyar,
                "تغییر ترم",
                f"ترم هنرجو {student_name} ({profile.user.phone_number if profile.user else 'نامشخص'}) از {old_term_name} به {new_term_name} تغییر یافت"
            )
            
            return Response({'message': 'ترم با موفقیت تغییر یافت'}, status=status.HTTP_200_OK)
        except Term.DoesNotExist:
            return Response({'error': 'ترم مورد نظر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # === اکشن جدید برای تغییر آپولون‌یار ===
    @action(detail=True, methods=['patch'])
    def change_apollonyar(self, request, pk=None):
        """
        تغییر آپولون‌یار یک پروفایل خاص.
        آدرس: PATCH /api/profiles/{id}/change_apollonyar/
        """
        profile = self.get_object()
        apollonyar_id = request.data.get('apollonyarId')
        reason = request.data.get('reason', '')
        
        if not apollonyar_id:
            return Response({'error': 'apollonyarId الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            apollonyar = Apollonyar.objects.get(id=apollonyar_id)
            old_apollonyar = profile.apollonyar
            
            # تغییر آپولون‌یار
            profile.apollonyar = apollonyar
            profile.save()
            
            # ثبت لاگ
            current_apollonyar = get_apollonyar_for_user(request.user)
            student_name = f"{profile.user.first_name} {profile.user.last_name}".strip() if profile.user else "نامشخص"
            old_apollonyar_name = f"{old_apollonyar.first_name} {old_apollonyar.last_name}".strip() if old_apollonyar else "نامشخص"
            new_apollonyar_name = f"{apollonyar.first_name} {apollonyar.last_name}".strip()
            log_action(
                current_apollonyar,
                "تغییر آپولون‌یار",
                f"آپولون‌یار هنرجو {student_name} ({profile.user.phone_number if profile.user else 'نامشخص'}) از {old_apollonyar_name} به {new_apollonyar_name} تغییر یافت"
            )
            
            return Response({'message': 'آپولون‌یار با موفقیت تغییر یافت'}, status=status.HTTP_200_OK)
        except Apollonyar.DoesNotExist:
            return Response({'error': 'آپولون‌یار مورد نظر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # === اکشن جدید برای تغییر نوع ===
    @action(detail=True, methods=['patch'])
    def change_type(self, request, pk=None):
        """
        تغییر نوع یک پروفایل خاص.
        آدرس: PATCH /api/profiles/{id}/change_type/
        """
        profile = self.get_object()
        student_type = request.data.get('studentType')
        reason = request.data.get('reason', '')
        
        if not student_type:
            return Response({'error': 'studentType الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        
        # تبدیل نوع از فارسی به انگلیسی
        type_map = {
            'ترمی': 'term-based',
            'خودخوان': 'self-study'
        }
        
        if student_type not in type_map:
            return Response({'error': 'نوع نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            old_type = profile.get_type_display()
            profile.type = type_map[student_type]
            profile.save()
            
            # ثبت لاگ
            apollonyar = get_apollonyar_for_user(request.user)
            student_name = f"{profile.user.first_name} {profile.user.last_name}".strip() if profile.user else "نامشخص"
            log_action(
                apollonyar,
                "تغییر نوع هنرجو",
                f"نوع هنرجو {student_name} ({profile.user.phone_number if profile.user else 'نامشخص'}) از {old_type} به {student_type} تغییر یافت"
            )
            
            return Response({'message': 'نوع با موفقیت تغییر یافت'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # === اکشن جدید برای تغییر وضعیت ===
    @action(detail=True, methods=['patch'])
    def change_status(self, request, pk=None):
        """
        تغییر وضعیت یک پروفایل خاص.
        آدرس: PATCH /api/profiles/{id}/change_status/
        """
        profile = self.get_object()
        new_status = request.data.get('status')
        reason = request.data.get('reason', '')
        
        if not new_status:
            return Response({'error': 'status الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        
        # تبدیل وضعیت از فارسی به انگلیسی
        status_map = {
            'آزاد': 'active',
            'مسدود': 'suspended',
            'انصراف': 'optout'
        }
        
        if new_status not in status_map:
            return Response({'error': 'وضعیت نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            old_status = profile.get_status_display()
            profile.status = status_map[new_status]
            profile.save()
            
            # ثبت لاگ
            apollonyar = get_apollonyar_for_user(request.user)
            student_name = f"{profile.user.first_name} {profile.user.last_name}".strip() if profile.user else "نامشخص"
            log_action(
                apollonyar,
                "تغییر وضعیت هنرجو",
                f"وضعیت هنرجو {student_name} ({profile.user.phone_number if profile.user else 'نامشخص'}) از {old_status} به {new_status} تغییر یافت"
            )
            
            return Response({'message': 'وضعیت با موفقیت تغییر یافت'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet برای مشاهده لاگ اقدامات
    """
    from .serializers import LogSerializer
    queryset = Log.objects.all().order_by('-timestamp')
    serializer_class = LogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Log.objects.all().order_by('-timestamp')

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

    # اکشن سفارشی برای ویرایش مهلت تکلیف
    @action(detail=True, methods=['patch'])
    def update_due_date(self, request, pk=None):
        """
        ویرایش مهلت ارسال یک تکلیف خاص.
        آدرس: PATCH /api/assignments/{id}/update_due_date/
        """
        assignment = self.get_object()
        new_due_date = request.data.get('dueDate')
        reason = request.data.get('reason', '')
        
        if not new_due_date:
            return Response({'error': 'dueDate الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from datetime import datetime
            # تبدیل تاریخ از فرمت YYYY-MM-DD به datetime
            if isinstance(new_due_date, str):
                due_date_obj = datetime.strptime(new_due_date, '%Y-%m-%d')
            else:
                due_date_obj = new_due_date
            
            old_deadline = assignment.deadline
            assignment.deadline = due_date_obj
            assignment.save()
            
            # ثبت لاگ
            apollonyar = get_apollonyar_for_user(request.user)
            student_name = f"{assignment.profile.user.first_name} {assignment.profile.user.last_name}".strip() if assignment.profile.user else "نامشخص"
            assignment_title = assignment.assignment_def.title if assignment.assignment_def else "نامشخص"
            old_date_str = old_deadline.strftime('%Y/%m/%d') if old_deadline else "نامشخص"
            new_date_str = due_date_obj.strftime('%Y/%m/%d')
            log_action(
                apollonyar,
                "تغییر مهلت تکلیف",
                f"مهلت تکلیف {assignment_title} هنرجو {student_name} ({assignment.profile.user.phone_number if assignment.profile.user else 'نامشخص'}) از {old_date_str} به {new_date_str} تغییر یافت"
            )
            
            return Response({'message': 'مهلت تکلیف با موفقیت به‌روزرسانی شد'}, status=status.HTTP_200_OK)
        except ValueError:
            return Response({'error': 'فرمت تاریخ نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


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

class TransactionViewSet(viewsets.ModelViewSet):
    """API برای مدیریت تراکنش‌ها."""
    queryset = Transaction.objects.select_related('target_user').prefetch_related('notes__author_apollonyar').all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated] # تغییر: هر کاربر احراز هویت شده دسترسی دارد

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """
        یک endpoint سفارشی برای تایید یا رد کردن یک تراکنش.
        آدرس: POST /api/transactions/{id}/verify/
        بدنه درخواست: {"status": "valid"} یا {"status": "invalid"}
        """
        transaction = self.get_object()
        new_status = request.data.get('status')

        if new_status not in ['valid', 'invalid', 'pending']:
            return Response({'error': 'وضعیت نامعتبر است.'}, status=status.HTTP_400_BAD_REQUEST)
        
        transaction.verification_status = new_status
        transaction.verification_timestamp = timezone.now()
        transaction.save()
        
        # یک لاگ یا یادداشت هم می‌توان اینجا اضافه کرد
        
        return Response(TransactionSerializer(transaction).data)

class InstallmentViewSet(viewsets.ModelViewSet):
    """API برای مدیریت اقساط."""
    queryset = Installment.objects.select_related(
        'profile__user', 'profile__course', 'transaction'
    ).all()
    serializer_class = InstallmentSerializer
    permission_classes = [permissions.IsAuthenticated]

class CallViewSet(viewsets.ReadOnlyModelViewSet):
    """API برای مشاهده تماس‌ها."""
    queryset = Call.objects.select_related(
        'profile__user', 'caller', 'call_def'
    ).all()
    serializer_class = CallSerializer
    permission_classes = [permissions.IsAuthenticated]