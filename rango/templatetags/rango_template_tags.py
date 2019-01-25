from django import template
from rango.models import Category

register = template.Library()

@register.inclusion_tag('rango/cats.html')
def get_category_list(request,cat=None):
    return {'cats': Category.objects.all(),'act_cat': cat, }