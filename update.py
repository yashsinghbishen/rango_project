import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','rango_project.settings')
import django
django.setup()
from rango.models import Category,Page
import random
def add_cat(lst):
    c = Category.objects.get_or_create(name=lst[0])[0]
    c.view = lst[1]
    c.likes = lst[2]
    c.save()
    return c
lst = [["Python",5,7],["Django",2,1],["Other Frameworks",7,8]]
for l in lst:
    add_cat(l)
for i in range(1,9):
    p = Page.objects.get_or_create(id=i)[0]
    r = random.randint(50,100)
    p.views = r
    p.save()