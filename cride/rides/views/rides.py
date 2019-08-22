"""Rides view """

#Django
from django.utils import timezone

#Utilities
from datetime import timedelta


#Django REST Framework
from rest_framework import mixins, viewsets
from rest_framework.generics import get_object_or_404

#Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions.memberships import IsActiveCircleMember
from cride.rides.permissions.rides import IsRideOwner

#Filters
from rest_framework.filters import SearchFilter, OrderingFilter
# from django_filters.rest_framework import DjangoFilterBackend

# serializers
from cride.rides.serializers import (CreateRideSerializer, RideModelSerializer)

#Models
from cride.circles.models import Circle


class RideViewSet(mixins.CreateModelMixin,
				mixins.ListModelMixin,
				mixins.UpdateModelMixin,
				viewsets.GenericViewSet):
		#Ride view set

	# serializer_class = CreateRideSerializer
	filter_backends = (SearchFilter, OrderingFilter)
	ordering = ('departure_date', 'arrival_date', 'available_seats')
	ordering_fields = ('departure_date', 'arrival_date', 'available_seats')
	search_fields = ('departure_location', 'arrival_location')

	def dispatch(self, request, *args, **kwargs):
		# Verify that the circle exists
		slug_name = kwargs['slug_name'] #from url
		self.circle = get_object_or_404(Circle, slug_name=slug_name)
		return super(RideViewSet, self).dispatch(request, *args, **kwargs)

	def get_permissions(self):
		#assign permission based on action
		permissions = [ IsAuthenticated, IsActiveCircleMember]
		if self.action in ['update', 'partial_update']:
			permissions.append(IsRideOwner)
		return [p() for p in permissions]


	def get_serializer_context(self):
		"""Add circle to serializer context """
		context = super(RideViewSet, self).get_serializer_context()
		context['circle'] = self.circle
		return context

	def get_serializer_class(self):
		# return serializer based on action
		if self.action == 'create':
			return CreateRideSerializer

		return RideModelSerializer

	def get_queryset(self):
		#return actuve circle's rides
		offset = timezone.now() + timedelta(minutes=10)
		return self.circle.ride_set.filter(
			departure_date__gte=offset,
			is_active=True,
			available_seats__gte=1
		)