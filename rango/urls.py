from django.conf.urls import url
from rango import views

urlpatterns = [
url(r'^$', views.index, name='index'),
url(r'^about/', views.about, name='about'),
url(r'^add_category/$', views.add_category, name='add_category'),
url(r'^(?P<category_id>[\w\-]+)/edit_category/$', views.edit_category, name='edit_category'),
url(r'^category/(?P<category_name_url>[\w\-]+)/$',views.show_category, name='show_category'),
url(r'^(?P<category_name_slug>[\w\-]+)/add_page/$',views.add_page, name='add_page'),
url(r'^category/(?P<category_name_url>[\w\-]+)/(?P<page_id>[\w\-]+)/edit_page/$',views.edit_page, name='edit_page'),
url(r'^register/$', views.register, name='register'),
url(r'^profile_registration', views.profile, name='profile_register'),
url(r'^profile/(?P<username>[\w\-]+)/$', views.profile, name='profile'),
url(r'^profiles/$', views.list_profiles, name='list_profiles'),
url(r'^login/$', views.user_login, name='login'),
url(r'^logout/$', views.user_logout, name='logout'),
url(r'^restricted/$', views.restricted, name='restricted'),
url(r'^search/$', views.search,name='search'),
url(r'^like/$', views.like_category, name='like_category'),
url(r'^goto',views.track_url,name='goto'),
url(r'^suggest/$', views.suggest_category, name='suggest_category'),
url(r'^add/$', views.auto_add_page,name='auto_add_page'),
]