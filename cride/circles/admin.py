# Circle admin

# DJango 
from django.contrib import admin

# Models
from cride.circles.models import Circle

@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
	#circle admin 
	list_display = (
		'slug_name',
		'name',
		'is_public',
		'verified',
		'is_limited',
		'members_limit'
	)

	search_fields = ('slug_name', 'name')

	list_filter = (
		'is_public',
		'verified',
		'is_limited'
	)

	actions = ['make_verified', 'make_unverified']

	def make_verified(self, request, queryset):
		#self is an istance CircelAdmin
		# make circles verified
		queryset.update(verified=True)
	make_verified.short_description = 'Make select circles verified'


	def make_unverified(self, request, queryset):
		#self is an istance CircelAdmin
		# make circles verified
		queryset.update(verified=False)
	make_unverified.short_description = 'Make select circles unverified'