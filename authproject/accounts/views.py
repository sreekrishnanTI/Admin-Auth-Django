from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache

from .forms import AdminUserCreateForm, AdminUserUpdateForm, RegisterForm

User = get_user_model()


@never_cache
def home(request):
    return redirect('dashboard' if request.user.is_authenticated else 'login')


@never_cache
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.role = 'user'
        user.save()
        messages.success(request, 'Account created. Please login.')
        return redirect('login')

    return render(request, 'register.html', {'form': form})


@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    context = {}

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        try:
            user_obj = User.objects.get(username=username)

            if not user_obj.is_active:
                context['error'] = 'Your account is blocked by admin.'

            else:
                user = authenticate(request, username=username, password=password)

                if user is None:
                    context['error'] = 'Invalid username or password.'
                else:
                    login(request, user)
                    return redirect('dashboard')

        except User.DoesNotExist:
            context['error'] = 'Invalid username or password.'

    return render(request, 'login.html', context)


@login_required
@never_cache
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
@never_cache
def logout_view(request):
    logout(request)
    return redirect('login')


def _require_admin(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden('Only admin users can access this page.')
    return None


@login_required
@never_cache
def user_list(request):
    forbidden = _require_admin(request)
    if forbidden:
        return forbidden

    users = User.objects.order_by('id')
    return render(request, 'user_list.html', {'users': users})


@login_required
@never_cache
def user_create(request):
    forbidden = _require_admin(request)
    if forbidden:
        return forbidden

    form = AdminUserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.role = "user"
        user.save()

        messages.success(request, 'User created successfully.')
        return redirect('user_list')

    return render(request, 'user_form.html', {'form': form, 'title': 'Create User'})


@login_required
@never_cache
def user_update(request, user_id):
    forbidden = _require_admin(request)
    if forbidden:
        return forbidden

    target_user = get_object_or_404(User, id=user_id)
    form = AdminUserUpdateForm(request.POST or None, instance=target_user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'User updated successfully.')
        return redirect('user_list')

    return render(request, 'user_form.html', {'form': form, 'title': f'Edit {target_user.username}'})



@login_required
@never_cache
def user_toggle_active(request, user_id):
    forbidden = _require_admin(request)
    if forbidden:
        return forbidden

    target_user = get_object_or_404(User, id=user_id)

    if target_user == request.user:
        messages.error(request, "You cannot block your own account.")
        return redirect("user_list")

    target_user.is_active = not target_user.is_active
    target_user.save()

    if target_user.is_active:
        messages.success(request, f"{target_user.username} has been unblocked.")
    else:
        messages.warning(request, f"{target_user.username} has been blocked.")

    return redirect("user_list")