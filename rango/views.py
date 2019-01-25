from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page, UserProfile, User
from rango.forms import CategoryForm, PageForm, CategoryEditForm, PageEditForm, UserProfileForm
from django.db import IntegrityError
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from datetime import datetime
from registration.backends.simple.views import RegistrationView
from rango.bing_search import run_query
# Create your views here.


def index(request):
    visitor_cookie_handler(request)
    request.session.set_test_cookie()
    context_dict = {'Category': Category.objects.order_by(
        'likes')[:5], 'Pages': Page.objects.order_by('views')[:5]}
    response = render(request, 'rango/index.html', context_dict)
    site_visitor_cookie_handler(request, response)
    return response


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def site_visitor_cookie_handler(request, response):
    if request.COOKIES.get('visited') == None:
        visits = int(request.session.get('visit', 0))
        visits = visits+1
        response.set_cookie('visited', 'yes')
        request.session['visit'] = visits


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request,
                                               'last_visit',
                                               str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')
    if (datetime.now() - last_visit_time).seconds > 0:
        visits = visits + 1
    request.session['last_visit'] = last_visit_cookie
    request.session['visits'] = visits


def about(request):
    if request.session.test_cookie_worked():
        print("Cookie worked.")
        request.session.delete_test_cookie()
    return render(request, 'rango/about.html')


def show_category(request, category_name_url):
    query = ""
    result_list = []
    context_dict = {}
    if request.method == 'POST' and 'query' in request.POST:
        query = request.POST['query'].strip()
        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)
            context_dict['result_list'] = result_list
            context_dict['query'] = query
    try:
        category = Category.objects.get(slug=category_name_url)
        if request.method == 'GET':
            category.view = category.view+1
            category.save()
        page = Page.objects.filter(category=category).order_by('-views')
        context_dict['views'] = category.view
        context_dict['pages'] = page
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['pages'] = None
        context_dict['category'] = None

    return render(request, 'rango/category.html', context_dict)


def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)
    else:
        cat_list = Category.objects.all()
    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]
    return cat_list

def suggest_category(request):
    cat_list = []
    starts_with = ''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']
        cat_list = get_category_list(8, starts_with)
    return render(request, 'rango/cats.html', {'cats': cat_list })


def add_category(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            try:
                form.save(commit=True)
                return index(request)
            except IntegrityError as e:
                form.add_error('name', e)
        else:
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})


def edit_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        category = None
    form = CategoryEditForm(
        {'name': category.name, 'view': category.view, 'likes': category.likes})
    if request.method == 'POST':
        form = CategoryEditForm(request.POST)
        try:
            category.name = request.POST.get('name')
            category.likes = request.POST.get('likes')
            category.view = request.POST.get('view')
            category.save()
            return index(request)
        except IntegrityError as e:
            form.add_error('name', e)

    return render(request, 'rango/edit_category.html', {'form': form})


def edit_page(request, category_name_url, page_id):
    try:
        page = Page.objects.get(id=page_id)
    except Page.DoesNotExist:
        page = None
    form = PageEditForm({'title': page.title, 'url': page.url,
                         'views': page.views, 'likes': page.likes})
    if request.method == 'POST':
        form = PageEditForm(request.POST)
        try:
            page.title = request.POST.get('title')
            page.url = request.POST.get('url')
            page.likes = request.POST.get('likes')
            page.views = request.POST.get('views')
            page.save()
            # print(str(reverse(show_category,{'category_name_url':category_name_url})))
            return HttpResponseRedirect('/rango/category/'+category_name_url+'/')
            # return HttpResponseRedirect(reverse(show_category,category_name_url))
        except IntegrityError as e:
            form.add_error('name', e)

    return render(request, 'rango/edit_Page.html', {'form': form})


def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)

        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)

@login_required
def auto_add_page(request):
    cat_id = None
    url = None
    title = None
    context_dict = {}
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category,
                                            title=title, url=url)
            pages = Page.objects.filter(category=category).order_by('-views')
            # Adds our results list to the template context under name pages.
            context_dict['pages'] = pages
            context_dict['category'] = category
            # return HttpResponseRedirect('/rango/category/'+category.slug+'/')
    return render(request, 'rango/page_list.html', context_dict)

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request, 'rango/register.html', {'user_form': user_form,
                                                   'profile_form': profile_form,
                                                   'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse('Your Account have been disabled.')
        else:
            return render(request, 'rango/login.html', {'err': 'bad credentials received '})
    else:
        return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
    return render(request, 'rango/ristricted.html')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


class MyRegistrationView(RegistrationView):
    def get_success_url(self, user):
        return '/rango/profile_registration'


def search(request):
    query = ""
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)
    return render(request, 'rango/search.html', {'result_list': result_list, 'query': query})


def track_url(request):
    page_id = None
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
            except Page.DoesNotExist:
                page = None

            if page:
                page.views = page.views+1
                page.save()
                print(page.views)
    return HttpResponseRedirect(str(page.url))


def profile(request):
    # if request.method=='GET':
    form = UserProfileForm()
    # return render(request,'rango/profile_registration.html',{'form' : form})

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            print('valid')
            try:
                pfr = form.save(commit=False)
                pfr.user = request.user
                pfr.save()
                return index(request)
            except IntegrityError as e:
                form.add_error('name', e)
        else:
            print('invalid')
            print('error', form.errors)
    return render(request, 'rango/profile_registration.html', {'form': form, })


@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('index')
    userprofile = UserProfile.objects.get_or_create(user=user)[0]
    form = UserProfileForm({'website': userprofile.website,
                            'picture': userprofile.picture})
    if request.method == 'POST':
        form = UserProfileForm(
            request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect('/rango/profile/'+user.username)
    else:
        print(form.errors)
    return render(request, 'rango/profile.html',
                  {'userprofile': userprofile, 'selecteduser': user, 'form': form})


@login_required
def list_profiles(request):
    userprofile_list = UserProfile.objects.all()
    pictures = {}
    for user in userprofile_list:
        # user_profile = UserProfile.objects.get(user=User.objects.get(user=user))
        # pictures[user.username]=user_profile.picture
        print(type(user))
    print(pictures)
    return render(request, 'rango/list_profiles.html',
                  {'userprofile_list': userprofile_list})


@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        likes = 0
        if cat_id:
            cat = Category.objects.get(id=int(cat_id))
            if cat:
                likes = cat.likes + 1
                cat.likes = likes
                cat.save()
    return HttpResponse(likes)
