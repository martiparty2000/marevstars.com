from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from .models import UserProfile

# --- Helper Functions ---
def is_admin_or_head_coach(user):
    # This allows 'head_coach' (what you have in DB) or 'Owner'
    return user.is_authenticated and (user.role == 'Owner' or user.role == 'head_coach')

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
        {'name': 'Благовест Марев', 'role': 'Главен Треньор', 'bio': 'Благовест Тодоров Марев е роден на 21 април 1983 година в град Варна, Народна Република България. Марев е юноша на ПФК Черно море (Варна). След като напуска отбора от родния си град, той преминава през клубовете Добруджа и Калиакра. От 2007 до 2009 г. Марев е част от един от най-добрите български отбори по футзал МФК Варна. През 2009 – 2010 г. се състезава за хърватцкия Битумина. След като се завръща в България играе последователно за Гранд Про, МФK Варна и Одесос Хидроремнт. През 2013 преминава в малтийския Хибърниънс с който става шампион на Малта. С него са свързани и най-големите успехи на Националния ни отбор по футзал. В момента той е треньор на ФК Марев Старс и ПФK Черно Море. ', 'image': 'marev.png'},
        {'name': 'Йордан Радев', 'role': 'Треньор', 'bio': 'Йордан Радев е роден e през 2001 година, висок е 178 сантиметра. Играе като централен защитник. Радев е капитан и шампион на България с юношите на Черно море до 19 години през 2018. През миналата кампания за кратко игра като преотстъпен на Спартак Плевен, преди да са завърне в Черно море заради финансови неуредици на плевенския клуб. ', 'image': 'radev.png'},
        {'name': 'Тодор Марев', 'role': 'Старши Треньор', 'bio': 'Тодor Бойчев Марев е легендарен български футболист и защитник, рекордьor по участия за ПФK Черно море (Варна) в А група с 422 мача. Роден е през 1953 г. и преминава през всички формации на „моряците“, като дебютира за мъжкия отбор през 1972 г. Изиграва общо 530 официални срещи за клуба, което е национален рекорд за мачове с един екип. В националния отбор на България записва 16 участия за „А“ тима и 36 за юношеските и младежки формации. Носител е на наградата „Футболист на Варна“ в три поредни сезона (1976, 1977, 1978). След края на състезателната си кариера се отдава на треньорска дейност в школата на „Черно море“ и успешно води дамския отбор „Грандхотел Варна“ до две шампионски титли.', 'image': 'todor.png'}
    ]
    return render(request, 'coaches.html', {'coaches': coaches})

# --- Auth Views ---
def register_view(request):
    if request.method == "POST":
        role = request.POST.get('role')
        egn = request.POST.get('egn')
        if UserProfile.objects.filter(egn=egn).exists():
            messages.error(request, "Error: That EGN is already registered.")
            return render(request, 'register.html')
        
        # Add your registration creation logic here...
        messages.info(request, "Registration successful!")
        return redirect('team:login')
    return render(request, 'register.html')

def login_view(request):
    if request.method == "POST":
        egn = request.POST.get('egn')
        password = request.POST.get('password')
        user = authenticate(request, username=egn, password=password)
        if user:
            login(request, user)
            return redirect('team:home')
        messages.error(request, "Invalid credentials.")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
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
        if action == 'approve':
            user.is_approved = True
            user.save()
        elif action == 'deny':
            user.delete()
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
        target_user.role = new_role
        target_user.save()
        messages.success(request, f"Updated {target_user.full_name} to {new_role}.")
        return redirect('team:manage_roles')
    return render(request, 'manage_roles.html', {'users': users})