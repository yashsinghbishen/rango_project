from django import forms
from django.contrib.auth.models import User
from rango.models import Page, Category ,UserProfile 
from django.template.defaultfilters import slugify

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text = 'Enter the name of Category' )
    view = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required= False)
    class Meta:
        model = Category
        fields = ('name',)

class CategoryEditForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text = 'Update the name of Category', initial='name')
    view = forms.IntegerField(help_text = 'Update the views of Category', initial='view')
    likes = forms.IntegerField(help_text = 'Update the likes of Category', initial='likes')
    slug = forms.CharField(widget=forms.HiddenInput(), required= False)
    class Meta:
        model = Category
        fields = ('name','view','likes')
    
class PageEditForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text= 'Update the title of Page', initial='title')
    url = forms.URLField(max_length=128, help_text= 'Update the url for page', initial='url')
    views = forms.IntegerField(help_text = 'Update the views of Category', initial='views')
    likes = forms.IntegerField(help_text = 'Update the likes of Category', initial='likes')
    class Meta:
        model = Page
        # exclude = ('Category',)
        fields=('title','url','views','likes')
    
class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128,
                            help_text= 'Enter the title of Page')
    url = forms.URLField(max_length=128,
                            help_text= 'Enter the url for page')
    class Meta:
        model = Page
        # exclude = ('Category',)
        fields=('title','url',)
        
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    website = forms.URLField()
    picture = forms.ImageField()
    class Meta:
        model = UserProfile
        fields = ('website', 'picture',)