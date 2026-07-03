from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import RegisterForm, LoginForm, ProfileForm, NoteForm, MessageForm
from .models import Profile, Note, Message



def get_or_create_profile(user):
    profile, created = Profile.objects.get_or_create(user=user)
    return profile

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            get_or_create_profile(user)
            login(request, user)
            messages.success(request, f'Реєстрація успішна {user.first_name}! Ви увійшли в систему.')
            return redirect('dashboard')
        messages.error(request, 'Будь ласка, виправте помилки у формі.')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Ви увійшли в систему як {user.first_name}.')
            return redirect('dashboard')
        messages.error(request, 'Будь ласка, перевірте ваші дані для входу.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Ви вийшли з системи.')
    return redirect('login')

@login_required
def dashboard(request):
    profile = get_or_create_profile(request.user)
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    notes = request.user.notes.all()
    total_notes = notes.count()
    done_notes = notes.filter(done=True).count()
    pedding_notes = notes.filter(done=False).count()
    high_priority_notes = notes.filter(priority='high', done=False).count()
    unread_messages = request.user.received_messages.filter(is_read=False).count()
    recent_notes = notes[:5]
    recent_massages = request.user.received_messages.select_related('sender')[:5]
    context = {
        'profile': profile,
        'total_notes': total_notes,
        'done_notes': done_notes,
        'pedding_notes': pedding_notes,
        'high_priority_notes': high_priority_notes,
        'unread_messages': unread_messages,
        'recent_notes': recent_notes,
        'recent_massages': recent_massages,
        'completion_pct': int(done_notes / total_notes * 100) if total_notes > 0 else 0,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile_view(request):
    profile = get_or_create_profile(request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        form.fields['first_name'].initial = request.user.first_name
        form.fields['last_name'].initial = request.user.last_name
        form.fields['email'].initial = request.user.email
        if form.is_valid():
            profile = form.save(commit=False)
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            profile.save()
            messages.success(request, 'Профіль оновлено успішно.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email
        }
        )
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})

@login_required
def notes_view(request):
    profile = get_or_create_profile(request.user)
    notes = request.user.notes.all().order_by('-created_at')
    filter_by = request.GET.get('filter', 'all')

    if filter_by == 'done':
        notes = notes.filter(done=True)
    elif filter_by == 'active':
        notes = notes.filter(done=False)
    elif filter_by == 'high':
        notes = notes.filter(priority='high')
    
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            messages.success(request, 'Нотатка створена успішно.')
            return redirect('notes')
    else:
        form = NoteForm()
    return render(request, 'accounts/notes.html', {'form': form, 'notes': notes, 'filter_by': filter_by, 'profile': profile,
    'total_notes': request.user.notes.count(),
    'done_count': request.user.notes.filter(done=True).count()
    })

@login_required
def note_toogle(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.done = not note.done
    note.save()
    return JsonResponse({'done': note.done})


@login_required
def note_delete(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Нотатка видалена успішно.')
    return redirect('notes')

@login_required
def masseges_inbox(request):
    profile = get_or_create_profile(request.user)
    inbox = request.user.received_messages.select_related('sender').all()
    sent = request.user.sent_messages.select_related('recipient').all()
    unread_count = inbox.filter(is_read=False).count()
    form = MessageForm(current_user=request.user)
    if request.method == 'POST':
        form = MessageForm(request.POST, current_user=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            messages.success(request, f'Повідомлення надіслано успішно до {message.recipient.first_name} {message.recipient.last_name}.')
            return redirect('masseges_inbox')
    return render(request, 'accounts/masseges_inbox.html', {'inbox': inbox, 'sent': sent, 'unread_count': unread_count, 'form': form, 'profile': profile})

@login_required
def messsage_read(request, message_id):
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    if not message.is_read:
        message.is_read = True
        message.save()
    return render(request, 'accounts/message_detail.html', {'message': message, 'profile': get_or_create_profile(request.user)})
