""" Circles permission classes. """

# Django REST Framework
from rest_framework.permissions import BasePermission

# Models
from cride.circles.models import Membership

class IsCircleAdmin(BasePermission):
	# allow access only to circle admins
	def has_object_permission(self, request, view, obj):
		# in this case OBJ is the Circle
		#Verify user have a a membership in the obj
		try:
			Membership.objects.get(
				user=request.user,
				circle=obj,
				is_admin=True,
				is_active=True
			)
		except Membership.DoesNotExist:
			return False

		return True