import json

from django.conf import settings
from django.core.mail import send_mail
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
        {'name': 'Тодor Марев', 'role': 'Старши Треньор', 'bio': 'Тodor Бойчев Марев е легендарен български футболист и защитник, рекордьor по участия за ПФK Черно море (Варна) в А група с 422 мача. Роден е през 1953 г. и преминава през всички формации на „моряците“, като дебютира за мъжкия отбор през 1972 г. Изиграва общо 530 официални срещи за клуба, което е национален рекорд за мачове с един екип. В националния отбор на България записва 16 участия за „А“ тима и 36 за юношеските и младежки формации. Носител е на наградата „Футболист на Варна“ в три поредни сезона (1976, 1977, 1978). След края на състезателната си кариера се отдава на треньорска дейност в школата на „Черно море“ и успешно води дамския отбор „Грандхотел Варна“ до две шампионски титли.', 'image': 'todor.png'},
        {'name': 'Благовест Марев', 'role': 'Главен Треньор', 'bio': 'Благовест Тодorов Марев е роден на 21 април 1983 година в град Варна, Народна Република България. Марев е юноша на ПФK Черно море (Варна). След като напуска отбора от родния си град, той преминава през клубовете Добруджа и Калиакра. От 2007 до 2009 г. Марев е част от един от най-добрите български отбори по футзал МFK Варна. През 2009 - 2010 г. се състезава за хърватцкия Битумина. След като се завръща в България играе последователно за Гранд Про, МFK Варна и Одесос Хидроремнт. През 2013 преминава в малтийския Хибърниънс с който става шампион на Малта. С него са свързани и най-големите успехи на Националния ни отбор по футзал.', 'image': 'marev.png'},
        {'name': 'Йордан Радев', 'role': 'Треньор', 'bio': 'Йorдан Рadev е роден e през 2001 година, висок е 178 сантиметра. Играе като централен защитник. Рadev е капитан и шампион на България с юношите на Черно море до 19 години през 2018. През миналата кампания за кратко игра като преотстъпен на Сpартак Плевен, преди да са завърне в Черно море заради финансови неуредици на плевенския клуб. ', 'image': 'radev.png'},
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
        'goalkeeper', 'goalie', 'individual', 'registration', 'contact', 'free', 'trial',
    ))


def _support_reply(text):
    """Answer common questions using verified information published on this site."""
    message = text.lower()
    english = _is_english(text)

    goalkeeper_words = ('вратар', 'вратарск', 'goalkeeper', 'goalie', 'keeper')
    individual_words = ('индивидуал', 'лична тренировка', 'private training', 'individual')
    schedule_words = ('график', 'час', 'кога', 'ден', 'schedule', 'time', 'when')
    location_words = ('адрес', 'къде', 'терен', 'локация', 'where', 'location', 'address')
    age_words = ('възраст', 'години', 'група', 'дете', 'age', 'years old', 'group')
    coach_words = ('треньор', 'марев', 'радев', 'coach', 'todor', 'blagovest', 'yordan')
    joining_words = ('запис', 'запиша', 'такса', 'цена', 'плащ', 'join', 'register', 'sign up', 'membership', 'fees', 'price')
    fee_words = ('такса', 'цена', 'колко струва', 'fees', 'price', 'cost')
    payment_words = ('как се плаща', 'плащане', 'в брой', 'cash', 'how to pay', 'payment method')
    free_first_words = ('безплат', 'първата тренировка', 'пробна тренировка', 'free', 'first training', 'trial')
    equipment_words = ('какво да нося', 'какво носи', 'екипировка', 'калци', 'ръкавици', 'облекло', 'what to bring', 'equipment', 'gear')
    experience_words = ('предишен опит', 'футболен опит', 'начинаещ', 'няма опит', 'experience', 'beginner')
    holiday_words = ('ваканци', 'празниц', 'holiday', 'vacation', 'school break')
    joining_late_words = ('по средата', 'средата на сезона', 'средата на месеца', 'късно', 'mid-season', 'mid season', 'join later')
    capacity_words = ('места', 'лимит', 'свободни места', 'capacity', 'spots', 'places available')
    championship_words = ('първенств', 'мач', 'програма', 'съперник', 'championship', 'match', 'fixture', 'game')

    if any(word in message for word in goalkeeper_words):
        return (
            'Yes — goalkeeper work is included in both age groups, 8-12 and 13-16. At the moment, we do not offer separate individual goalkeeper sessions.'
            if english else
            'Да — вратарската работа е част от двете възрастови групи: 8-12 и 13-16 години. Към момента не предлагаме отделни индивидуални тренировки само за вратари.'
        )

    if any(word in message for word in payment_words):
        return (
            'The monthly fee is paid in cash.'
            if english else
            'Месечната такса се заплаща в брой.'
        )

    if any(word in message for word in equipment_words):
        return (
            'For the first session, please bring sportswear, football socks and water. Goalkeepers should also bring goalkeeper gloves.'
            if english else
            'За първата тренировка носете спортно облекло, калци и вода. Ако детето е вратар, носете и вратарски ръкавици.'
        )

    if any(word in message for word in experience_words):
        return (
            'No previous football experience is required. The important thing is that the child wants to train and develop.'
            if english else
            'Не е нужен предишен футболен опит. Важно е детето да има желание да тренира и да се развива.'
        )

    if any(word in message for word in holiday_words):
        return (
            'The schedule can change during holidays and school breaks. Some sessions take place, while parents are informed in advance about others.'
            if english else
            'Графикът може да се променя през ваканциите и празниците. Някои тренировки се провеждат, а за други родителите се информират предварително.'
        )

    if any(word in message for word in joining_late_words):
        return (
            'Yes, children can join during the month or season. Contact us so we can arrange a suitable group and first session.'
            if english else
            'Да, детето може да се присъедини по средата на месеца или сезона. Свържете се с нас, за да уточним подходяща група и първа тренировка.'
        )

    if any(word in message for word in capacity_words):
        return (
            'There is currently no fixed limit on places in the groups.'
            if english else
            'Към момента няма фиксиран лимит на местата в групите.'
        )

    if any(word in message for word in fee_words):
        return (
            'The monthly fee is 65 euros.'
            if english else
            'Месечната такса е 65 евро.'
        )

    if any(word in message for word in free_first_words):
        return (
            'Yes — the first training session is free.'
            if english else
            'Да — първата тренировка е безплатна.'
        )

    if any(word in message for word in individual_words):
        return (
            'Individual training is available on ul. “Fernando Magellan”. The day and time are arranged individually. '
            'Please call 089 917 3417 or connect with a consultant here to arrange it.'
            if english else
            'Индивидуалните тренировки са на ул. „Фернандо Магелан“, като денят и часът се уговарят индивидуално. '
            'Можете да се обадите на 089 917 3417 или да се свържете с консултант тук, за да уточните удобен час.'
        )

    if any(word in message for word in schedule_words):
        return (
            'The 8-12 group trains Monday, Wednesday and Thursday, 18:00-19:00. '
            'The 13-16 group trains Monday, Wednesday and Friday, 20:00-21:00.'
            if english else
            'Групата за 8-12 г. тренира в понеделник, сряда и четвъртък от 18:00 до 19:00. '
            'За 13-16 г. тренировките са в понеделник, сряда и петък от 20:00 до 21:00.'
        )

    if any(word in message for word in location_words):
        return (
            'Group training takes place at Sportna ploshtadka “Studentska”, football pitch “Zhechka Karamfilova”. '
            'Individual training is held on ul. “Fernando Magellan”.'
            if english else
            'Груповите тренировки са на Спортна площадка „Студентска“ — футболно игрище „Жечка Карамфилова“. '
            'Индивидуалните тренировки са на ул. „Фернандо Магелан“.'
        )

    if any(word in message for word in age_words):
        return (
            'We work with children and teenagers from 8 to 16 years old: 8-12 and 13-16. '
            'Tell me the child’s age and I can point you to the right group.'
            if english else
            'Работим с деца и младежи от 8 до 16 години — група 8-12 и група 13-16 години. '
            'Кажете ми на колко е детето и ще ви насоча към правилната група.'
        )

    if any(word in message for word in coach_words):
        return (
            'The coaching team includes Todor Marev (Senior Coach), Blagovest Marev (Head Coach) and Yordan Radev (Coach). '
            'You can read their football biographies in the Coaches section.'
            if english else
            'Треньорският екип е Тодор Марев — старши треньор, Благовест Марев — главен треньор, и Йордан Радев — треньор. '
            'Повече за футболната им биография има в секция „Треньори“.'
        )

    if any(word in message for word in championship_words):
        return (
            'The U15 upcoming-match programme is available in the “Championship” section of the site. '
            'It includes the date, time, opponent and whether the match is home or away.'
            if english else
            'Програмата на предстоящите мачове на U15 е в секция „Първенство“. '
            'Там са посочени дата, час, съперник и дали мачът е домакински или гостуване.'
        )

    if any(word in message for word in joining_words):
        return (
            'For joining, fees or another specific question, call the Head Coach on 089 917 3417. '
            'You can also choose “Connect me with a consultant” and send the child’s age here.'
            if english else
            'За записване, такси или друг конкретен въпрос се обадете на главния треньор на 089 917 3417. '
            'Можете и да натиснете „Свържи ме с консултант“ и да изпратите възрастта на детето тук.'
        )

    if any(word in message for word in ('здрасти', 'здравей', 'хей', 'hello', 'hi')):
        return (
            'Hi! 🙂 I can help with age groups, the schedule, goalkeeper and individual training, locations, coaches, matches, or joining the club. What would you like to know?'
            if english else
            'Здравейте! 🙂 Мога да помогна с възрастови групи, график, вратарски и индивидуални тренировки, място, треньори, мачове или записване. Какво ви интересува?'
        )

    return (
        'I can help with age groups, training times, goalkeeper or individual training, locations, coaches, upcoming matches and joining Marev Stars. What would you like to know?'
        if english else
        'Мога да помогна с възрастови групи, часове, вратарски или индивидуални тренировки, място, треньори, предстоящи мачове и записване в Марев Старс. Какво ви интересува?'
    )


def _support_requires_consultant(text):
    """Return True only when the site does not contain a reliable answer."""
    message = text.lower()
    goalkeeper_words = ('вратар', 'вратарск', 'goalkeeper', 'goalie', 'keeper')
    asks_for_person = ('кой', 'коя', 'кои', 'who', 'name', 'име')

    # The site confirms goalkeeper training, but does not name a goalkeeper coach.
    if any(word in message for word in goalkeeper_words) and any(word in message for word in asks_for_person):
        return True

    known_topics = (
        'вратар', 'вратарск', 'goalkeeper', 'goalie', 'keeper',
        'индивидуал', 'лична тренировка', 'private training', 'individual',
        'график', 'час', 'кога', 'ден', 'schedule', 'time', 'when',
        'адрес', 'къде', 'терен', 'локация', 'where', 'location', 'address',
        'възраст', 'години', 'група', 'дете', 'age', 'years old', 'group',
        'треньор', 'марев', 'радев', 'coach', 'todor', 'blagovest', 'yordan',
        'запис', 'запиша', 'такса', 'цена', 'плащ', 'join', 'register', 'sign up', 'membership', 'fees', 'price',
        'безплат', 'първата тренировка', 'пробна тренировка', 'free', 'first training', 'trial',
        'как се плаща', 'плащане', 'в брой', 'cash', 'how to pay', 'payment method',
        'какво да нося', 'какво носи', 'екипировка', 'калци', 'ръкавици', 'облекло', 'what to bring', 'equipment', 'gear',
        'предишен опит', 'футболен опит', 'начинаещ', 'няма опит', 'experience', 'beginner',
        'ваканци', 'празниц', 'holiday', 'vacation', 'school break',
        'по средата', 'средата на сезона', 'средата на месеца', 'късно', 'mid-season', 'mid season', 'join later',
        'места', 'лимит', 'свободни места', 'capacity', 'spots', 'places available',
        'първенств', 'мач', 'съперник', 'championship', 'match', 'fixture', 'game',
        'здрасти', 'здравей', 'хей', 'hello', 'hi',
    )
    return not any(word in message for word in known_topics)


def _consultant_notice(text):
    return (
        'I do not have reliable information about this on the site. Would you like me to connect you with a consultant?'
        if _is_english(text) else
        'Нямам надеждна информация за това в сайта. Искате ли да ви насоча към консултант?'
    )


def _is_consultant_confirmation(text):
    message = ' '.join(text.lower().split()).strip(' .!?')
    confirmations = (
        'да', 'да моля', 'да, моля', 'искам консултант', 'искам да говоря с консултант',
        'свържи ме с консултант', 'насочи ме към консултант',
        'yes', 'yes please', 'i want a consultant', 'connect me with a consultant',
    )
    return message in confirmations


def _consultant_escalation_notice(text):
    return (
        'Your request is with a consultant now. They will reply here soon. You can still send more details in this chat if needed.'
        if _is_english(text) else
        'Запитването вече е при консултант. Той ще ви отговори тук скоро. Ако е нужно, можете да изпратите още информация в този разговор.'
    )


def _last_bot_offered_consultant(ticket):
    last_bot = ticket.messages.filter(author_type='bot').order_by('-created_at').first()
    return bool(last_bot and (
        'Искате ли да ви насоча към консултант?' in last_bot.text
        or 'Would you like me to connect you with a consultant?' in last_bot.text
    ))


def _notify_support_staff(ticket):
    """Email the notification inbox once a visitor requests a consultant."""
    recipient = settings.SUPPORT_NOTIFICATION_EMAIL
    if not recipient or not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        return

    send_mail(
        subject=f'Нов Support билет #{ticket.pk} чака консултант',
        message=(
            f'Посетител поиска консултант за билет #{ticket.pk}.\n\n'
            f'Отворете билета: https://marevstars-com.onrender.com/support/ticket/{ticket.public_id}/'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=True,
    )

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
    needs_consultant = _support_requires_consultant(text)
    SupportMessage.objects.create(
        ticket=ticket,
        author_type='bot',
        text=_consultant_notice(text) if needs_consultant else _support_reply(text),
    )
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
    had_consultant_offer = _last_bot_offered_consultant(ticket)
    SupportMessage.objects.create(ticket=ticket, author_type='visitor', text=text)
    if not ticket.escalated:
        if had_consultant_offer and _is_consultant_confirmation(text):
            ticket.escalated = True
            ticket.save(update_fields=['escalated', 'updated_at'])
            SupportMessage.objects.create(
                ticket=ticket,
                author_type='bot',
                text=_consultant_escalation_notice(text),
            )
            _notify_support_staff(ticket)
        else:
            needs_consultant = _support_requires_consultant(text)
            SupportMessage.objects.create(
                ticket=ticket,
                author_type='bot',
                text=_consultant_notice(text) if needs_consultant else _support_reply(text),
            )
    ticket.refresh_from_db()
    return JsonResponse({'ticket': str(ticket.public_id), 'number': ticket.pk, 'status': ticket.status, 'escalated': ticket.escalated, 'messages': _messages_data(ticket)})


@require_POST
def support_escalate(request, public_id):
    ticket = get_object_or_404(SupportTicket, public_id=public_id)
    if ticket.status == 'archived':
        return JsonResponse({'error': 'Този разговор е затворен. Отворете нов чат, ако имате нужда от помощ.'}, status=403)
    if ticket.escalated:
        return JsonResponse({'ticket': str(ticket.public_id), 'number': ticket.pk, 'status': ticket.status, 'messages': _messages_data(ticket), 'escalated': True})
    ticket.escalated = True
    ticket.save()
    last_message = ticket.messages.filter(author_type='visitor').last()
    SupportMessage.objects.create(
        ticket=ticket,
        author_type='bot',
        text=_consultant_escalation_notice(last_message.text if last_message else ''),
    )
    _notify_support_staff(ticket)
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
