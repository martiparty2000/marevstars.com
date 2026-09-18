import json

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.views.decorators.http import require_GET, require_POST

from .models import SupportMessage, SupportTicket, UserProfile

# --- Helper Functions ---
def is_admin_or_head_coach(user):
    # Allow owner and head coach accounts to access management pages
    return user.is_authenticated and (user.role == 'owner' or user.role == 'head_coach')


def is_support_staff(user):
    return user.is_authenticated and user.is_staff


def is_support_owner(user):
    return user.is_authenticated and (user.is_superuser or user.role == 'owner')


def _support_title(text):
    message = text.lower()
    cleaned = ' '.join(text.split()).strip(' .!?')
    if any(word in message for word in ('здрасти', 'здравей', 'хей', 'hello', 'hi ')):
        return 'Нов разговор'
    return (cleaned[:54] + '…') if len(cleaned) > 55 else cleaned

# --- Public Views ---
def home_view(request):
    return render(request, 'home.html')

def schedule_view(request):
    return render(request, 'schedule.html')

def contact_view(request):
    return render(request, 'contact.html')

def coaches_view(request):
    coaches = [
        {'name': 'Тодор Марев', 'role': 'Старши Треньор', 'bio': 'Тодor Бойчев Марев е легендарен български футболист и защитник, рекордьor по участия за ПФK Черно море (Варна) в А група с 422 мача. Роден е през 1953 г. и преминава през всички формации на „моряците“, като дебютира за мъжкия отбор през 1972 г. Изиграва общо 530 официални срещи за клуба, което е национален рекорд за мачове с един екип. В националния отбор на България записва 16 участия за „А“ тима и 36 за юношеските и младежки формации. Носител е на наградата „Футболист на Варна“ в три поредни сезона (1976, 1977, 1978). След края на състезателната си кариера се отдава на треньорска дейност в школата на „Черно море“ и успешно води дамския отбор „Грандхотел Варна“ до две шампионски титли.', 'image': 'todor.png'},
        {'name': 'Благовест Марев', 'role': 'Главен Треньор', 'bio': 'Благовест Тодоров Марев е роден на 21 април 1983 година в град Варна, Народна Република България. Марев е юноша на ПФК Черно море (Варна). След като напуска отбора от родния си град, той преминава през клубовете Добруджа и Калиакра. От 2007 до 2009 г. Марев е част от един от най-добрите български отбори по футзал МФК Варна. През 2009 – 2010 г. се състезава за хърватцкия Битумина. След като се завръща в България играе последователно за Гранд Про, МФK Варна и Одесос Хидроремнт. През 2013 преминава в малтийския Хибърниънс с който става шампион на Малта. С него са свързани и най-големите успехи на Националния ни отбор по футзал.', 'image': 'marev.png'},
        {'name': 'Йордан Радев', 'role': 'Треньор', 'bio': 'Йордан Радев е роден e през 2001 година, висок е 178 сантиметра. Играе като централен защитник. Радев е капитан и шампион на България с юношите на Черно море до 19 години през 2018. През миналата кампания за кратко игра като преотстъпен на Спартак Плевен, преди да са завърне в Черно море заради финансови неуредици на плевенския клуб. ', 'image': 'radev.png'},
    ]
    return render(request, 'coaches.html', {'coaches': coaches})

def terms_view(request):
    return render(request, 'terms.html')

def privacy_view(request):
    return render(request, 'privacy.html')

def cookies_view(request):
    return render(request, 'cookies.html')


def _is_english(text):
    words = text.lower()
    return any(word in words for word in (
        'hello', 'hi', 'how', 'what', 'when', 'where', 'can i', 'join',
        'club', 'training', 'schedule', 'coach', 'price', 'fees', 'please',
    ))


def _support_reply(text):
    message = text.lower()
    if _is_english(text):
        if any(word in message for word in ('join', 'register', 'sign up', 'become a member', 'club')):
            return 'To join Marev Stars, please look at the Training page first and choose the suitable age group and time. Then call us on 089 917 3417, or choose “Connect me with a consultant” and the team will reply here.'
        if any(word in message for word in ('schedule', 'time', 'when', 'training')):
            return 'You can find the full schedule in the Training page. The 8–12 group trains Monday, Wednesday and Thursday, 18:00–19:00; the 13–16 group trains Monday, Wednesday and Friday, 20:00–21:00.'
        if any(word in message for word in ('where', 'location', 'address')):
            return 'Group training takes place at Sportna ploshtadka “Studentska”, football pitch “Zhechka Karamfilova”. You can also find the location in the Training section.'
        if any(word in message for word in ('coach', 'marev', 'radev')):
            return 'Our coaches are Todor Marev, Blagovest Marev and Yordan Radev. Please see the Coaches section to learn more about them.'
        if any(word in message for word in ('hello', 'hi')):
            return 'Hi! 🙂 How can I help? You can ask about training, the schedule, age groups, coaches, location, or joining the club.'
        return 'I can help with training, the schedule, groups, coaches, location, or joining the club. What would you like to know?'
    if any(word in message for word in ('здрасти', 'здравей', 'хей')):
        return 'Здрасти! 🙂 Кажи ми какво те интересува и ще помогна — например график, група за детето, място на тренировките или записване.'
    if any(word in message for word in ('график', 'час', 'кога', 'ден')):
        return 'Групата за 8–12 г. тренира понеделник, сряда и четвъртък от 18:00 до 19:00. За 13–16 г. тренировките са понеделник, сряда и петък от 20:00 до 21:00.'
    if any(word in message for word in ('адрес', 'къде', 'терен', 'локация')):
        return 'Груповите тренировки са на Спортна площадка „Студентска“ — футболно игрище „Жечка Карамфилова“.'
    if any(word in message for word in ('възраст', 'години', 'група', 'дете')):
        return 'Работим с групи за деца и младежи от 8 до 16 години. Можете да видите графика в секция „Тренировки“. '
    if any(word in message for word in ('треньор', 'марев', 'радев')):
        return 'Екипът ни включва Тодор Марев, Благовест Марев и Йордан Радев. Повече за тях има в секция „Треньори“. '
    if any(word in message for word in ('запис', 'такса', 'цена', 'индивидуал')):
        return 'За записване, такси или индивидуална тренировка първо вижте секция „Тренировки“. Ако имате въпрос, изберете „Свържи ме с консултант“ и екипът ще ви отговори тук.'
    return 'Мога да помогна с тренировки, график, възрастови групи, треньори, мястото и записването. За кое от тези неща питаш?'
def _messages_data(ticket):
    return [
        {
            'author': item.author_type,
            'text': item.text,
            'created_at': item.created_at.strftime('%d.%m · %H:%M'),
        }
        for item in ticket.messages.all()
    ]


def _read_json(request):
    try:
        return json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


@require_POST
def support_start(request):
    data = _read_json(request)
    text = str(data.get('text', '')).strip()
    if not text or len(text) > 2000:
        return JsonResponse({'error': 'Напишете съобщение до 2000 символа.'}, status=400)
    ticket = SupportTicket.objects.create(title=_support_title(text))
    SupportMessage.objects.create(ticket=ticket, author_type='visitor', text=text)
    SupportMessage.objects.create(ticket=ticket, author_type='bot', text=_support_reply(text))
    return JsonResponse({'ticket': str(ticket.public_id), 'number': ticket.pk, 'title': ticket.title, 'status': ticket.status, 'escalated': ticket.escalated, 'messages': _messages_data(ticket)})


@require_GET
def support_thread(request, public_id):
    ticket = get_object_or_404(SupportTicket.objects.prefetch_related('messages'), public_id=public_id)
    if ticket.title in ('Ново запитване', 'Общо запитване'):
        first = ticket.messages.filter(author_type='visitor').first()
        if first:
            ticket.title = _support_title(first.text)
            ticket.save(update_fields=['title', 'updated_at'])
    return JsonResponse({'ticket': str(ticket.public_id), 'number': ticket.pk, 'title': ticket.title, 'status': ticket.status, 'escalated': ticket.escalated, 'messages': _messages_data(ticket)})


@require_POST
def support_message(request, public_id):
    ticket = get_object_or_404(SupportTicket.objects.prefetch_related('messages'), public_id=public_id)
    if ticket.status == 'archived':
        return JsonResponse({'error': 'Този разговор е затворен. Отворете нов чат, ако имате друг въпрос.'}, status=403)
    data = _read_json(request)
    text = str(data.get('text', '')).strip()
    if not text or len(text) > 2000:
        return JsonResponse({'error': 'Напишете съобщение до 2000 символа.'}, status=400)
    SupportMessage.objects.create(ticket=ticket, author_type='visitor', text=text)
    if not ticket.escalated:
        SupportMessage.objects.create(ticket=ticket, author_type='bot', text=_support_reply(text))
        ticket.save()
    ticket.refresh_from_db()
    return JsonResponse({'ticket': str(ticket.public_id), 'number': ticket.pk, 'status': ticket.status, 'escalated': ticket.escalated, 'messages': _messages_data(ticket)})


@require_POST
def support_escalate(request, public_id):
    ticket = get_object_or_404(SupportTicket, public_id=public_id)
    if ticket.status == 'archived':
        return JsonResponse({'error': 'Този разговор е затворен. Отворете нов чат, ако имате нужда от помощ.'}, status=403)
    ticket.escalated = True
    ticket.save()
    last_message = ticket.messages.filter(author_type='visitor').last()
    notice = 'Your request has been sent to a consultant. The reply will appear in this conversation.' if last_message and _is_english(last_message.text) else 'Запитването е изпратено към консултант. Отговорът ще се появи в този разговор.'
    SupportMessage.objects.create(ticket=ticket, author_type='bot', text=notice)
    return JsonResponse({'ticket': str(ticket.public_id), 'number': ticket.pk, 'status': ticket.status, 'messages': _messages_data(ticket), 'escalated': True})

@require_POST
def support_close(request, public_id):
    ticket = get_object_or_404(SupportTicket, public_id=public_id)
    if ticket.status == 'archived':
        return JsonResponse({'ticket': str(ticket.public_id), 'number': ticket.pk, 'status': ticket.status, 'escalated': ticket.escalated, 'messages': _messages_data(ticket)})
    if ticket.escalated:
        return JsonResponse({'error': 'Заявката вече е при консултант и се затваря от екипа.'}, status=403)
    last_message = ticket.messages.filter(author_type='visitor').last()
    notice = 'This ticket is now closed and has been moved to Archived. Thank you!' if last_message and _is_english(last_message.text) else 'Този билет е затворен и е преместен в Архивирано. Благодарим ви!'
    SupportMessage.objects.create(ticket=ticket, author_type='bot', text=notice)
    ticket.status = 'archived'
    ticket.save()
    return JsonResponse({'ticket': str(ticket.public_id), 'number': ticket.pk, 'status': ticket.status, 'escalated': ticket.escalated, 'messages': _messages_data(ticket)})

# --- Staff & Admin Portal ---
@staff_member_required
def staff_dashboard(request):
    pending_users = UserProfile.objects.filter(is_approved=False).count()
    # Make sure this points to your template file
    return render(request, 'dashboard.html', {'pending_count': pending_users})


@user_passes_test(is_support_staff, login_url='team:support_login')
def support_dashboard(request):
    tickets = SupportTicket.objects.prefetch_related('messages').all()
    return render(request, 'support_dashboard.html', {
        'tickets': tickets,
        'ai_count': tickets.filter(status='active', escalated=False).count(),
        'new_count': tickets.filter(status='active', escalated=True).count(),
        'handled_count': tickets.filter(status='handled').count(),
        'archived_count': tickets.filter(status='archived').count(),
        'ticket_statuses': SupportTicket.STATUS_CHOICES,
    })


@user_passes_test(is_support_owner, login_url='team:support_login')
def support_access_manage(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            egn = request.POST.get('egn', '').strip()
            full_name = request.POST.get('full_name', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            if not all((egn, full_name, email, password)):
                messages.error(request, 'Попълнете име, потребител, имейл и парола.')
            elif UserProfile.objects.filter(egn=egn).exists():
                messages.error(request, 'Този потребител вече съществува.')
            elif len(password) < 8:
                messages.error(request, 'Паролата трябва да е поне 8 символа.')
            else:
                person = UserProfile.objects.create_user(
                    egn=egn, full_name=full_name, email=email, password=password,
                )
                person.is_staff = True
                person.is_approved = True
                person.role = 'coach'
                person.save(update_fields=['is_staff', 'is_approved', 'role'])
                messages.success(request, f'Добавен е Support достъп за {full_name}.')
        elif action in ('toggle', 'password'):
            person = get_object_or_404(UserProfile, id=request.POST.get('user_id'))
            if person.pk == request.user.pk and action == 'toggle':
                messages.error(request, 'Не можете да махнете собствения си достъп.')
            elif action == 'toggle':
                person.is_staff = not person.is_staff
                person.save(update_fields=['is_staff'])
                messages.success(request, 'Достъпът е обновен.')
            else:
                password = request.POST.get('password', '')
                if len(password) < 8:
                    messages.error(request, 'Новата парола трябва да е поне 8 символа.')
                else:
                    person.set_password(password)
                    person.save(update_fields=['password'])
                    messages.success(request, 'Паролата е сменена.')
        return redirect('team:support_access_manage')

    staff_accounts = UserProfile.objects.filter(is_staff=True).order_by('full_name')
    return render(request, 'support_access_manage.html', {'staff_accounts': staff_accounts})


@user_passes_test(is_support_staff, login_url='team:support_login')
def support_ticket_detail(request, public_id):
    ticket = get_object_or_404(SupportTicket.objects.prefetch_related('messages'), public_id=public_id)
    if request.method == 'POST':
        if ticket.status == 'archived':
            messages.info(request, 'Този билет е архивиран и не може да се редактира или да получава нови отговори.')
            return redirect('team:support_ticket_detail', public_id=ticket.public_id)
        if not ticket.escalated:
            messages.info(request, 'Този разговор все още се обработва от автоматичния помощник. Консултант може да отговори само след заявка от посетителя.')
            return redirect('team:support_ticket_detail', public_id=ticket.public_id)
        text = request.POST.get('text', '').strip()
        status = request.POST.get('status', ticket.status)
        if text:
            SupportMessage.objects.create(ticket=ticket, author_type='staff', author=request.user, text=text[:2000])
            if status == 'active':
                status = 'handled'
        if status in dict(SupportTicket.STATUS_CHOICES):
            ticket.status = status
        if ticket.status == 'archived' and status == 'archived':
            SupportMessage.objects.create(ticket=ticket, author_type='bot', text='Този разговор е затворен и е преместен в архива. Благодарим ви!')
        ticket.save()
        return redirect('team:support_ticket_detail', public_id=ticket.public_id)
    return render(request, 'support_ticket_detail.html', {'ticket': ticket})


def support_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('team:support_dashboard')
    error = ''
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username', ''), password=request.POST.get('password', ''))
        if user and user.is_staff:
            login(request, user)
            return redirect(request.POST.get('next') or 'team:support_dashboard')
        error = 'Невалидни данни за вход или нямате достъп до Support.'
    return render(request, 'support_login.html', {'error': error, 'next': request.GET.get('next', '')})


def support_logout(request):
    logout(request)
    return redirect('team:support_login')

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
