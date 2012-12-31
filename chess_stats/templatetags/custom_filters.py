from django.template import Library

register = Library()

@register.filter
def is_false(arg):
	return arg is False

@register.filter
def is_none(arg):
	return arg is None
