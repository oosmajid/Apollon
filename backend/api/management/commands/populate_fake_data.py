import random
import string
from datetime import datetime, timedelta, date
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from api.models import (
    User, Apollonyar, Course, Term, Group, AssignmentDef, AssignmentDefTemplate,
    CallDef, Profile, MedalDef, Medal, DiscountCode, Transaction, TransactionNote,
    Installment, Assignment, AssignmentSubmission, AssignmentSubmissionFile,
    Call, Note, Log, OTPCode
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with fake data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Starting to populate fake data...')
        
        # Generate data in dependency order
        self.create_apollonyars()
        self.create_users()
        self.create_courses_and_terms()
        self.create_groups()
        self.create_assignment_definitions()
        self.create_call_definitions()
        self.create_medal_definitions()
        self.create_profiles()
        self.create_assignments()
        self.create_transactions_and_installments()
        self.create_medals()
        self.create_discount_codes()
        self.create_calls_and_notes()
        self.create_logs()

        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with fake data!')
        )

    def clear_data(self):
        """Clear all existing data"""
        models_to_clear = [
            OTPCode, Log, Note, Call, AssignmentSubmissionFile, AssignmentSubmission,
            Assignment, Installment, TransactionNote, Transaction, Medal, DiscountCode,
            Profile, AssignmentDefTemplate, AssignmentDef, CallDef, Group, Term, Course,
            Apollonyar, User
        ]
        
        for model in models_to_clear:
            model.objects.all().delete()
            self.stdout.write(f'Cleared {model.__name__}')

    def get_random_phone(self):
        """Generate random Iranian phone number"""
        prefixes = ['0912', '0913', '0914', '0915', '0916', '0917', '0918', '0919']
        prefix = random.choice(prefixes)
        number = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        return prefix + number

    def get_random_email(self, first_name, last_name):
        """Generate random email"""
        domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'iran.ir']
        return f"{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}"

    def create_apollonyars(self):
        """Create fake Apollonyar users"""
        first_names = ['احمد', 'محمد', 'علی', 'حسن', 'حسین', 'رضا', 'امیر', 'سعید', 'مهدی', 'پیمان']
        last_names = ['احمدی', 'محمدی', 'علی‌زاده', 'حسینی', 'رضایی', 'کریمی', 'نوری', 'صادقی', 'موسوی', 'حیدری']
        
        apollonyars = []
        for i in range(15):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            phone = self.get_random_phone()
            
            apollonyar = Apollonyar.objects.create(
                first_name=first_name,
                last_name=last_name,
                phone_number=phone,
                password='password123',
                telegram_id=f"@{first_name.lower()}{last_name.lower()}",
                is_admin=random.choice([True, False]),
                is_blocked=False
            )
            apollonyars.append(apollonyar)
        
        self.stdout.write(f'Created {len(apollonyars)} Apollonyars')

    def create_users(self):
        """Create fake User students"""
        first_names = ['فاطمه', 'زهرا', 'مریم', 'علی', 'محمد', 'حسن', 'حسین', 'رضا', 'امیر', 'سارا', 'نازنین', 'کامران', 'داریوش', 'آرش', 'پویا']
        last_names = ['احمدی', 'محمدی', 'حسینی', 'رضایی', 'کریمی', 'نوری', 'صادقی', 'موسوی', 'حیدری', 'شریفی', 'جعفری', 'طاهری', 'مهدوی', 'رحمانی', 'فرهادی']
        cities = ['تهران', 'اصفهان', 'شیراز', 'مشهد', 'تبریز', 'کرج', 'اهواز', 'قم', 'کرمانشاه', 'ارومیه']
        states = ['تهران', 'اصفهان', 'فارس', 'خراسان رضوی', 'آذربایجان شرقی', 'البرز', 'خوزستان', 'قم', 'کرمانشاه', 'آذربایجان غربی']
        
        users = []
        for i in range(20):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            phone = self.get_random_phone()
            city = random.choice(cities)
            state = random.choice(states)
            
            # Generate random birth date (18-50 years old)
            today = date.today()
            birth_year = today.year - random.randint(18, 50)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            birthday = date(birth_year, birth_month, birth_day)
            
            user = User.objects.create(
                phone_number=phone,
                first_name=first_name,
                last_name=last_name,
                email=self.get_random_email(first_name, last_name),
                phone_2_number=self.get_random_phone() if random.choice([True, False]) else '',
                sex=random.choice(['male', 'female']),
                birthday=birthday,
                country='ایران',
                state_province=state,
                city=city,
                full_address=f"{city}، {state}، خیابان {random.choice(['ولیعصر', 'انقلاب', 'کریمخان', 'آزادی'])}، پلاک {random.randint(1, 100)}",
                postal_code=str(random.randint(1000000000, 9999999999))
            )
            users.append(user)
        
        self.stdout.write(f'Created {len(users)} Users')

    def create_courses_and_terms(self):
        """Create fake courses and terms"""
        course_names = [
            'آموزش گیتار کلاسیک',
            'آموزش پیانو',
            'آموزش ویولن',
            'آموزش سنتور',
            'آموزش تار',
            'آموزش دف',
            'آموزش آواز',
            'آموزش موسیقی کودک',
            'آموزش موسیقی ایرانی',
            'آموزش تنظیم و آهنگسازی'
        ]
        
        courses = []
        terms = []
        
        for course_name in course_names:
            course = Course.objects.create(name=course_name)
            courses.append(course)
            
            # Create 2-4 terms for each course
            num_terms = random.randint(2, 4)
            for i in range(num_terms):
                start_date = date.today() + timedelta(days=random.randint(-30, 90))
                end_date = start_date + timedelta(days=random.randint(60, 120))
                price = Decimal(str(random.randint(500000, 2000000)))
                
                term = Term.objects.create(
                    course=course,
                    price=price,
                    name=f'ترم {i+1}',
                    start_date=start_date,
                    end_date=end_date
                )
                terms.append(term)
        
        self.stdout.write(f'Created {len(courses)} Courses and {len(terms)} Terms')

    def create_groups(self):
        """Create fake groups for terms"""
        terms = Term.objects.all()
        groups = []
        
        for term in terms:
            # Create 1-3 groups per term
            num_groups = random.randint(1, 3)
            for i in range(num_groups):
                group = Group.objects.create(
                    term=term,
                    title=f'گروه {chr(65 + i)}'  # A, B, C
                )
                groups.append(group)
        
        self.stdout.write(f'Created {len(groups)} Groups')

    def create_assignment_definitions(self):
        """Create fake assignment definitions"""
        terms = Term.objects.all()
        assignments = []
        
        assignment_titles = [
            'تمرین آکوردهای مقدماتی',
            'اجرای قطعه کلاسیک',
            'تمرین تکنیک انگشت‌گذاری',
            'آهنگ‌سازی خلاقانه',
            'تمرین ریتم و تمپو',
            'اجرای قطعه محلی',
            'تمرین گام‌ها',
            'نواختن قطعه مدرن'
        ]
        
        for term in terms:
            # Create 3-6 assignments per term
            num_assignments = random.randint(3, 6)
            for i in range(num_assignments):
                title = random.choice(assignment_titles)
                deadline = timezone.now() + timedelta(days=random.randint(7, 30))
                
                assignment = AssignmentDef.objects.create(
                    term=term,
                    title=f'{title} - {term.name}',
                    deadline=deadline,
                    is_required=random.choice([True, False])
                )
                assignments.append(assignment)
        
        self.stdout.write(f'Created {len(assignments)} Assignment Definitions')

    def create_call_definitions(self):
        """Create fake call definitions"""
        terms = Term.objects.all()
        call_defs = []
        
        call_titles = [
            'پیگیری وضعیت تحصیلی',
            'یادآوری قسط ماهانه',
            'هماهنگی جلسه حضوری',
            'پیگیری تکالیف',
            'اطلاع‌رسانی رویداد جدید',
            'مشاوره تحصیلی',
            'پیگیری انصراف'
        ]
        
        for term in terms:
            # Create 2-4 call definitions per term
            num_calls = random.randint(2, 4)
            for i in range(num_calls):
                title = random.choice(call_titles)
                start_date = timezone.now() + timedelta(days=random.randint(1, 15))
                end_date = start_date + timedelta(days=random.randint(7, 30))
                
                call_def = CallDef.objects.create(
                    term=term,
                    title=f'{title} - {term.name}',
                    start_due_date=start_date,
                    end_due_date=end_date
                )
                call_defs.append(call_def)
        
        self.stdout.write(f'Created {len(call_defs)} Call Definitions')

    def create_medal_definitions(self):
        """Create fake medal definitions"""
        medal_defs = []
        
        medal_data = [
            {'title': 'دانش‌آموز برتر', 'description': 'برای عملکرد عالی در تکالیف'},
            {'title': 'نوازنده ماه', 'description': 'برای پیشرفت قابل توجه در نوازندگی'},
            {'title': 'خلاقیت', 'description': 'برای آهنگ‌سازی و خلاقیت موسیقایی'},
            {'title': 'پشتکار', 'description': 'برای تلاش مداوم و پیگیری'},
            {'title': 'همکاری', 'description': 'برای همکاری با سایر هنرجویان'},
            {'title': 'نوآوری', 'description': 'برای ارائه ایده‌های نو'},
            {'title': 'استاد کوچک', 'description': 'برای کمک به سایر هنرجویان'},
            {'title': 'تلاشگر', 'description': 'برای تلاش فوق‌العاده'}
        ]
        
        for medal_info in medal_data:
            medal_def = MedalDef.objects.create(
                title=medal_info['title'],
                description=medal_info['description'],
                icon=''  # Empty for now, can be filled with actual SVG files later
            )
            medal_defs.append(medal_def)
        
        self.stdout.write(f'Created {len(medal_defs)} Medal Definitions')

    def create_profiles(self):
        """Create fake student profiles"""
        users = User.objects.all()
        courses = Course.objects.all()
        apollonyars = Apollonyar.objects.all()
        groups = Group.objects.all()
        profiles = []
        
        for user in users:
            # Each user can have 1-2 profiles (different courses)
            num_profiles = random.randint(1, 2)
            selected_courses = random.sample(list(courses), min(num_profiles, len(courses)))
            
            for course in selected_courses:
                # Get a random term from this course
                terms = course.terms.all()
                if terms.exists():
                    term = random.choice(terms)
                    # Get a random group from this term
                    term_groups = term.groups.all()
                    group = random.choice(term_groups) if term_groups.exists() else None
                else:
                    term = None
                    group = None
                
                apollonyar = random.choice(apollonyars)
                sales_rep = random.choice(apollonyars)
                
                profile = Profile.objects.create(
                    user=user,
                    course=course,
                    term=term,
                    group=group,
                    apollonyar=apollonyar,
                    sales_representative=sales_rep,
                    type=random.choice(['term-based', 'self-study']),
                    status=random.choice(['active', 'suspended', 'optout']),
                    hearts=random.randint(1, 5),
                    stars=round(random.uniform(0.0, 5.0), 1)
                )
                profiles.append(profile)
        
        self.stdout.write(f'Created {len(profiles)} Profiles')

    def create_assignments(self):
        """Create fake assignments for profiles"""
        profiles = Profile.objects.filter(term__isnull=False)
        assignment_defs = AssignmentDef.objects.all()
        assignments = []
        
        for profile in profiles:
            # Get assignments for this profile's term
            term_assignments = assignment_defs.filter(term=profile.term)
            
            for assignment_def in term_assignments:
                assignment = Assignment.objects.create(
                    profile=profile,
                    assignment_def=assignment_def,
                    deadline=assignment_def.deadline
                )
                assignments.append(assignment)
        
        self.stdout.write(f'Created {len(assignments)} Assignments')

    def create_transactions_and_installments(self):
        """Create fake transactions and installments"""
        profiles = Profile.objects.all()
        apollonyars = Apollonyar.objects.all()
        transactions = []
        installments = []
        
        for profile in profiles:
            if profile.term:
                # Create installments for term-based profiles
                term_price = profile.term.price
                num_installments = random.randint(3, 12)
                installment_amount = term_price / num_installments
                
                for i in range(num_installments):
                    due_date = date.today() + timedelta(days=i * 30)
                    status = random.choice(['pending', 'paid', 'pending'])
                    
                    installment = Installment.objects.create(
                        profile=profile,
                        due_amount=installment_amount,
                        due_date=due_date,
                        status=status,
                        is_splited=random.choice([True, False])
                    )
                    
                    # If paid, create transaction
                    if status == 'paid':
                        transaction = Transaction.objects.create(
                            target_user=profile.user,
                            amount=installment_amount,
                            type='deposit',
                            payment_method=random.choice(['gateway', 'card', 'paya']),
                            verification_status=random.choice(['valid', 'pending']),
                            reference_number=str(random.randint(100000000, 999999999))
                        )
                        installment.transaction = transaction
                        installment.save()
                        transactions.append(transaction)
                    
                    installments.append(installment)
                
                # Create some random transactions
                for _ in range(random.randint(1, 3)):
                    amount = Decimal(str(random.randint(50000, 500000)))
                    transaction = Transaction.objects.create(
                        target_user=profile.user,
                        amount=amount,
                        type=random.choice(['deposit', 'withdrawal']),
                        payment_method=random.choice(['gateway', 'card', 'paya']),
                        verification_status=random.choice(['valid', 'pending', 'invalid']),
                        reference_number=str(random.randint(100000000, 999999999))
                    )
                    transactions.append(transaction)
        
        self.stdout.write(f'Created {len(transactions)} Transactions and {len(installments)} Installments')

    def create_medals(self):
        """Create fake medals for profiles"""
        profiles = Profile.objects.all()
        medal_defs = MedalDef.objects.all()
        apollonyars = Apollonyar.objects.all()
        medals = []
        
        for profile in profiles:
            # Each profile gets 0-3 medals
            num_medals = random.randint(0, 3)
            selected_medals = random.sample(list(medal_defs), min(num_medals, len(medal_defs)))
            
            for medal_def in selected_medals:
                medal = Medal.objects.create(
                    profile=profile,
                    medal_def=medal_def,
                    giver_apollonyar=random.choice(apollonyars),
                    description=f'مدال {medal_def.title} به {profile.user.first_name} {profile.user.last_name} اعطا شد.'
                )
                medals.append(medal)
        
        self.stdout.write(f'Created {len(medals)} Medals')

    def create_discount_codes(self):
        """Create fake discount codes"""
        discount_codes = []
        
        for i in range(10):
            code = f'DISCOUNT{random.randint(1000, 9999)}'
            cash_price = Decimal(str(random.randint(50000, 200000))) if random.choice([True, False]) else None
            installment_price = Decimal(str(random.randint(100000, 500000))) if random.choice([True, False]) else None
            
            discount_code = DiscountCode.objects.create(
                code=code,
                cash_price=cash_price,
                installment_price=installment_price,
                max_usage=random.randint(1, 50),
                expiration_date=timezone.now() + timedelta(days=random.randint(30, 365)),
                usage_count=random.randint(0, 20)
            )
            discount_codes.append(discount_code)
        
        self.stdout.write(f'Created {len(discount_codes)} Discount Codes')

    def create_calls_and_notes(self):
        """Create fake calls and notes"""
        profiles = Profile.objects.all()
        apollonyars = Apollonyar.objects.all()
        call_defs = CallDef.objects.all()
        calls = []
        notes = []
        
        for profile in profiles:
            # Create 1-5 calls per profile
            num_calls = random.randint(1, 5)
            for _ in range(num_calls):
                call = Call.objects.create(
                    profile=profile,
                    call_def=random.choice(call_defs) if call_defs.exists() else None,
                    caller=random.choice(apollonyars),
                    type=random.choice(['course', 'installment', 'cancellation', 'other']),
                    status=random.choice(['pending', 'not_answered', 'successful', 'lost']),
                    call_timestamp=timezone.now() - timedelta(days=random.randint(1, 30)),
                    description=f'تماس با {profile.user.first_name} {profile.user.last_name} در مورد {random.choice(["وضعیت تحصیلی", "قسط ماهانه", "تکالیف", "مشاوره"])}'
                )
                calls.append(call)
            
            # Create 1-3 notes per profile
            num_notes = random.randint(1, 3)
            for _ in range(num_notes):
                note = Note.objects.create(
                    profile=profile,
                    author_apollonyar=random.choice(apollonyars),
                    note=f'یادداشت برای {profile.user.first_name} {profile.user.last_name}: {random.choice(["هنرجوی فعال", "نیاز به پیگیری", "پیشرفت خوب", "مشکل در پرداخت"])}'
                )
                notes.append(note)
        
        self.stdout.write(f'Created {len(calls)} Calls and {len(notes)} Notes')

    def create_logs(self):
        """Create fake system logs"""
        apollonyars = Apollonyar.objects.all()
        logs = []
        
        actions = [
            'ایجاد پروفایل جدید',
            'تغییر وضعیت پروفایل',
            'اعطای مدال',
            'ایجاد تراکنش',
            'تایید پرداخت',
            'ایجاد گروه جدید',
            'تخصیص آپولون‌یار',
            'تغییر اطلاعات کاربر'
        ]
        
        for _ in range(50):
            log = Log.objects.create(
                action=random.choice(actions),
                issuer_apollonyar=random.choice(apollonyars),
                description=f'سیستم: {random.choice(actions)} انجام شد.'
            )
            logs.append(log)
        
        self.stdout.write(f'Created {len(logs)} Logs')
