from typing import cast

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError, OperationalError
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.http import HttpResponse, HttpResponseForbidden
from .models import UserProfile
from .gsheets import add_user_to_sheet

# --- Helper Functions ---
def is_admin_or_head_coach(user):
    # Allow owner and head coach accounts to access management pages
    return user.is_authenticated and (user.role == 'owner' or user.role == 'head_coach')

# --- Public Views ---
def home_view(request):
    return render(request, 'home.html')

def schedule_view(request):
    return render(request, 'schedule.html')

def contact_view(request):
    return render(request, 'contact.html')

def payment_view(request):
    if not request.user.is_authenticated:
        return redirect('team:login')
    return render(request, 'payment.html')

def coaches_view(request):
    coaches = [
        {'name': 'Тодор Марев', 'role': 'Старши Треньор', 'bio': 'Тодor Бойчев Марев е легендарен български футболист и защитник, рекордьor по участия за ПФK Черно море (Варна) в А група с 422 мача. Роден е през 1953 г. и преминава през всички формации на „моряците“, като дебютира за мъжкия отбор през 1972 г. Изиграва общо 530 официални срещи за клуба, което е национален рекорд за мачове с един екип. В националния отбор на България записва 16 участия за „А“ тима и 36 за юношеските и младежки формации. Носител е на наградата „Футболист на Варна“ в три поредни сезона (1976, 1977, 1978). След края на състезателната си кариера се отдава на треньорска дейност в школата на „Черно море“ и успешно води дамския отбор „Грандхотел Варна“ до две шампионски титли.', 'image': 'todor.png'},
        {'name': 'Благовест Марев', 'role': 'Главен Треньор', 'bio': 'Благовест Тодоров Марев е роден на 21 април 1983 година в град Варна, Народна Република България. Марев е юноша на ПФК Черно море (Варна). След като напуска отбора от родния си град, той преминава през клубовете Добруджа и Калиакра. От 2007 до 2009 г. Марев е част от един от най-добрите български отбори по футзал МФК Варна. През 2009 – 2010 г. се състезава за хърватцкия Битумина. След като се завръща в България играе последователно за Гранд Про, МФK Варна и Одесос Хидроремнт. През 2013 преминава в малтийския Хибърниънс с който става шампион на Малта. С него са свързани и най-големите успехи на Националния ни отбор по футзал.', 'image': 'marev.png'},
        {'name': 'Йордан Радев', 'role': 'Треньор', 'bio': 'Йордан Радев е роден e през 2001 година, висок е 178 сантиметра. Играе като централен защитник. Радев е капитан и шампион на България с юношите на Черно море до 19 години през 2018. През миналата кампания за кратко игра като преотстъпен на Спартак Плевен, преди да са завърне в Черно море заради финансови неуредици на плевенския клуб. ', 'image': 'radev.png'},
    ]
    return render(request, 'coaches.html', {'coaches': coaches})

# --- Auth Views ---
def register_view(request):
    if request.method == "POST":
        role = request.POST.get('role')
        egn = request.POST.get('egn') or ''
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        date_of_birth = request.POST.get('date_of_birth') or None

        # child verification fields (may be required when registering as parent)
        child_full_name = request.POST.get('child_full_name') or ''
        child_egn = request.POST.get('child_egn') or ''
        child_password = request.POST.get('child_password') or ''

        # If registering as parent, require child info and generate a synthetic EGN username if none provided
        if role == 'parent':
            if not all([child_full_name, child_egn, child_password]):
                messages.error(request, "Моля попълнете името на детето, ЕГН и парола за проверка.")
                return render(request, 'register.html')
            if not egn:
                import time, random
                candidate = f'parent{int(time.time())}{random.randint(1000,9999)}'
                while UserProfile.objects.filter(egn=candidate).exists():
                    candidate = f'parent{int(time.time())}{random.randint(1000,9999)}'
                egn = candidate

        if UserProfile.objects.filter(egn=egn).exists():
            messages.error(request, "Error: That EGN is already registered.")
            return render(request, 'register.html')

        # basic required fields check (egn may have been auto-generated for parents)
        if not all([full_name, email, password]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'register.html')

        role_mapping = {'child': 'player', 'parent': 'player', 'coach': 'coach'}
        role_value = role_mapping.get(role, 'player')

        user = UserProfile.objects.create_user(
            egn=egn,
            full_name=full_name,
            email=email,
            password=password,
            role=role_value,
            date_of_birth=date_of_birth,
            child_full_name=child_full_name,
            child_egn=child_egn,
            is_approved=False,
        )

        # 2. ИЗВИКВАМЕ ФУНКЦИЯТА ТУК (БЕЗ form.is_valid()):
        try:
            # Тъй като в gsheets.py функцията очаква (child_name, parent_email)
            # Ако се регистрира родител, взимаме child_full_name, иначе full_name
            name_to_save = child_full_name if child_full_name else full_name
            add_user_to_sheet(name_to_save, email)
        except Exception as e:
            print(f"Failed to sync user {egn} to Google Sheets: {e}")

        messages.info(request, "Registration successful! Your account is pending approval.")
        return redirect('team:login')
    return render(request, 'register.html')

def login_view(request):
    if request.method == "POST":
        egn = request.POST.get('egn')
        password = request.POST.get('password')
        try:
            user = authenticate(request, username=egn, password=password)
        except OperationalError:
            call_command('migrate', verbosity=0, interactive=False, run_syncdb=True, no_input=True)
            user = authenticate(request, username=egn, password=password)

        if user is None:
            messages.error(request, "Invalid credentials.")
            return render(request, 'login.html')

        user = cast(UserProfile, user)
        if not user.is_approved and not user.is_superuser:
            messages.error(request, "Your account is pending approval.")
            return render(request, 'login.html')

        login(request, user)
        return redirect('team:home')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('team:home')

def create_admin_view(request, secret):
    secret_key = 'marev-stars-admin-2026'
    if secret != secret_key:
        return HttpResponseForbidden('Forbidden')

    egn = request.GET.get('egn')
    email = request.GET.get('email')
    full_name = request.GET.get('full_name')
    password = request.GET.get('password')

    if not all([egn, email, full_name, password]):
        return HttpResponse('Missing required query parameters. Use ?egn=...&email=...&full_name=...&password=...')

    try:
        call_command('migrate', verbosity=0, interactive=False, run_syncdb=True, no_input=True)
    except Exception:
        pass

    UserProfile.objects.filter(egn=egn).delete()
    UserProfile.objects.create_superuser(
        egn=egn,
        full_name=full_name,
        email=email,
        password=password,
    )
    return HttpResponse(f'Superuser created: {egn}. Now log in with that EGN and password.')


@login_required
def delete_account_view(request):
    if request.method != 'POST':
        return HttpResponseForbidden('Forbidden')

    user = request.user
    if user.role != 'owner':
        messages.error(request, 'Only the website owner may delete accounts.')
        return redirect(request.META.get('HTTP_REFERER', 'team:home'))

    password = request.POST.get('password')
    if not password:
        messages.error(request, 'Password required to delete account.')
        return redirect(request.META.get('HTTP_REFERER', 'team:home'))

    if not user.check_password(password):
        messages.error(request, 'Incorrect password. Account not deleted.')
        return redirect(request.META.get('HTTP_REFERER', 'team:home'))

    # record deletion in audit log (include identifying info in note so it survives FK nulling)
    try:
        from .models import ApprovalLog
        note = f'Self-deleted account {user.full_name} ({user.egn})'
        ApprovalLog.objects.create(actor=user, target=user, action='delete', note=note)
    except Exception:
        pass

    logout(request)
    # delete the user object
    try:
        user.delete()
    except Exception:
        pass

    messages.success(request, 'Your account has been deleted.')
    return redirect('team:home')

# --- Staff & Admin Portal ---
@staff_member_required
def staff_dashboard(request):
    pending_users = UserProfile.objects.filter(is_approved=False).count()
    # Make sure this points to your template file
    return render(request, 'dashboard.html', {'pending_count': pending_users})

@user_passes_test(is_admin_or_head_coach)
def approval_dashboard(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = get_object_or_404(UserProfile, id=user_id)
        note = request.POST.get('note', '')
        if action == 'approve':
            user.is_approved = True
            user.save()
            messages.success(request, f"Approved {user.full_name}.")
            try:
                from .models import ApprovalLog
                ApprovalLog.objects.create(actor=request.user, target=user, action='approve', note=note or 'Approved via dashboard')
            except Exception:
                pass
        elif action == 'deny':
            try:
                from .models import ApprovalLog
                ApprovalLog.objects.create(actor=request.user, target=user, action='deny', note=note or 'Denied via dashboard')
            except Exception:
                pass
            user.delete()
            messages.success(request, f"Denied {user.full_name}.")
        return redirect('team:approval_dashboard')
    
    pending_users = UserProfile.objects.filter(is_approved=False)
    return render(request, 'approval_dashboard.html', {'pending_users': pending_users})

@user_passes_test(is_admin_or_head_coach)
def manage_roles_view(request):
    users = UserProfile.objects.exclude(id=request.user.id)
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')
        target_user = get_object_or_404(UserProfile, id=user_id)
        old_role = target_user.role

        # Prevent assigning owner through this UI
        if new_role == 'owner' and target_user.role != 'owner':
            messages.error(request, 'Owner role may not be assigned through this interface.')
            return redirect('team:manage_roles')

        target_user.role = new_role
        target_user.save()
        messages.success(request, f"Updated {target_user.full_name} to {new_role}.")
        try:
            from .models import ApprovalLog
            ApprovalLog.objects.create(actor=request.user, target=target_user, action='role_change', note=f"{old_role} -> {new_role}")
        except Exception:
            pass
        return redirect('team:manage_roles')
    return render(request, 'manage_roles.html', {'users': users})