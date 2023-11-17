from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import LoginForm, UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from actions.utils import create_action
from actions.models import Action

@login_required
def dashboard(request):
    # Display all actions by default
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id',
                                                       flat=True)
    if following_ids:
        # If user is following others, retrieve only their actions
        actions = actions.filter(user_id__in=following_ids)
    actions = actions.select_related('user', 'user__profile')[:10]
    return render(request,
                  'account/dashboard.html',
                  {'section': 'dashboard'})



def user_registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_user = form.save(commit=False)
            new_user.set_password(
                cd['password']
            )
            new_user.save()
            create_action(new_user, 'has created an account')
            return render(request, 'account/register_done.html', {'new_user' : new_user} )
    else:
        form = UserRegistrationForm()
    return render(request, 'account/register.html', {'form' : form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})

@login_required
def user_list(request):
    template_name = 'account/user/list.html'
    users = User.objects.filter(is_active=True)
    return render(request,
                  template_name,
                  {'section':'people',
                   'users':users})

@login_required
def user_detail(request, username):
    template_name = 'account/user/detail.html'
    user = get_object_or_404(User, username=username, is_active=True)
    return render(request,
                  template_name,
                  {'user': user,
                   'section': 'people'})
