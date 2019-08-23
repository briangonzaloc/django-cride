"""Rides view """

#Django
from django.utils import timezone

#Utilities
from datetime import timedelta


#Django REST Framework
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

#Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions.memberships import IsActiveCircleMember
from cride.rides.permissions.rides import IsRideOwner, IsNotRideOwner

#Filters
from rest_framework.filters import SearchFilter, OrderingFilter
# from django_filters.rest_framework import DjangoFilterBackend

# serializers
from cride.rides.serializers import (CreateRideSerializer, RideModelSerializer, JoinRideSerializer, EndRideSerializer, CreateRideRatingSerializer)

#Models
from cride.circles.models import Circle


class RideViewSet(mixins.CreateModelMixin,
				mixins.ListModelMixin,
				mixins.RetrieveModelMixin,
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
		if self.action in ['update', 'partial_update', 'finish']:
			permissions.append(IsRideOwner)
		if action == 'join':
			permissions.append(IsNotRideOwner)
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
		if self.action == 'join': 
			return JoinRideSerializer
		if self.action == 'finish':
			return EndRideSerializer
		if self.action == 'rate':
			return CreateRideRatingSerializer
		return RideModelSerializer

	def get_queryset(self):
		#return actuve circle's rides
		print(self.action)
		if self.action not in ['finish', 'retrieve', 'rate']:
			offset = timezone.now() + timedelta(minutes=10)
			return self.circle.ride_set.filter(
				departure_date__gte=offset,
				is_active=True,
				available_seats__gte=1
			)

		return self.circle.ride_set.all()


	@action(detail=True, methods=['post'])
	def join(self, request, *args, **kwargs):
		# add requesting user to ride
		ride = self.get_object()
		serializer_class = self.get_serializer_class()
		serializer = serializer_class(
			ride,
			data={'passenger' : request.user.pk},
			context={'ride': ride, 'circle': self.circle},
			partial=True
		)
		serializer.is_valid(raise_exception=True)
		ride = serializer.save()
		data = RideModelSerializer(ride).data
		return Response(data, status=status.HTTP_200_OK)


	@action(detail=True, methods=['post'])
	def finish(self, request, *args, **kwargs):
		# call by owner to finish a ride
		ride = self.get_object()
		serializer_class = self.get_serializer_class()
		serializer = serializer_class(
			ride,
			data={'is_active':False, 'current_time':timezone.now()},
			context=self.get_serializer_context(),
			partial=True
		)
		serializer.is_valid(raise_exception=True)
		ride = serializer.save()
		data = RideModelSerializer(ride).data
		return Response(data, status=status.HTTP_200_OK)


	@action(detail=True, methods=['post'])
	def rate(self, request, *args, **kwargs):
		# rate ride
		ride = self.get_object()
		serializer_class = self.get_serializer_class()
		context = self.get_serializer_context()
		context['ride'] = ride
		serializer = serializer_class(data=request.data, context=context)
		serializer.is_valid(raise_exception=True)
		ride = serializer.save()
		data = RideModelSerializer(ride).data
		return Response(data, status=status.HTTP_201_CREATED)