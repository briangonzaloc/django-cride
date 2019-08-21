""" Circles views
"""

#Django REST Framework
from rest_framework import mixins, viewsets

# permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions.circles import IsCircleAdmin

#Models
from cride.circles.models import Circle, Membership

#Serializers
from cride.circles.serializers import CircleModelSerializer

class CircleViewSet(mixins.CreateModelMixin,
				   mixins.RetrieveModelMixin,
				   mixins.UpdateModelMixin,
				   mixins.ListModelMixin,
				   viewsets.GenericViewSet):
	"""Circle view set"""
	# queryset           = Circle.objects.all()
	serializer_class   = CircleModelSerializer
	# permission_classes = (IsAuthenticated,)
	lookup_field = 'slug_name'

	def get_queryset(self):
		# Restrict list to public-only
		queryset = Circle.objects.all()
		if self.action == 'list':
			return queryset.filter(is_public=True)
		return queryset

	def get_permissions(self):
		# assign permissions based on action
		permissions = [IsAuthenticated]
		if self.action in ['update', 'partial_update']:
			permissions.append(IsCircleAdmin)
		return [permission() for permission in permissions]

	def perform_create(self, serializer):
		#Assign circle admin
		circle = serializer.save()
		user = self.request.user
		profile = user.profile
		Membership.objects.create(
			user=user,
			profile=profile,
			circle=circle,
			is_admin=True,
			remaining_invitations=10,
		)