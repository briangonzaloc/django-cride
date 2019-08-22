""" Circle memebership views
"""

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

#Models
from cride.circles.models import Circle, Membership, Invitation

#Serializers
from cride.circles.serializers import MembershipModelSerializer, AddMemberSerializer

#Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions.memberships import IsActiveCircleMember, IsSelfMember

class MembershipViewSet(mixins.ListModelMixin, 
						mixins.CreateModelMixin,
						mixins.RetrieveModelMixin,
						mixins.DestroyModelMixin,
						viewsets.GenericViewSet):
	"""Circle membershio view set
	"""
	serializer_class = MembershipModelSerializer

	def dispatch(self, request, *args, **kwargs):
		# Verify that the circle exists
		slug_name = kwargs['slug_name'] #from url
		self.circle = get_object_or_404(Circle, slug_name=slug_name)
		return super(MembershipViewSet, self).dispatch(request, *args, **kwargs)

	def get_permissions(self):
		#Assign permission based on action
		permissions = [IsAuthenticated]
		if self.action != 'create':
			permissions.append(IsActiveCircleMember)
		if self.action == 'invitations':
			permissions.append(IsSelfMember)
		return [p() for p in permissions]

	def get_queryset(self):
		# Return circle memebers
		# self.circle.memebers return users members but we want memberships
		return Membership.objects.filter(
			circle=self.circle,
			is_active=True
		)		

	def get_object(self):
		#Return the circle member by using the user's username
		return get_object_or_404(
			Membership,
			user__username=self.kwargs['pk'], # pk is username parameter received by url
			circle=self.circle,
			is_active=True
		)

	def perform_destroy(self, instance):
		# disable membership
		instance.is_active = False
		instance.save()


	@action(detail=True, methods=['get'])
	def invitations(self, request, *args, **kwargs):
		"""Retrieve a member's invitations breakdown
		
		will return a list containin all the members that have
		used its invitations and another list containing the 
		invitations that haven't being used yet 
		"""
		member = self.get_object()

		invited_memebers = Membership.objects.filter(
			circle=self.circle,
			invited_by=request.user,
			is_active=True
		)

		unused_invitations = Invitation.objects.filter(
			circle=self.circle,
			issued_by=request.user,
			used=False  #unused
		).values_list('code')

		diff = member.remaining_invitations - len(unused_invitations)

		invitations = [ x[0] for x in unused_invitations ]

		for i in range(0,diff):
			#Create remaining invitation
			invitations.append(
				Invitation.objects.create(
					issued_by=request.user,
					circle=self.circle
				).code
			)

		data = {
			'used_invitations' : MembershipModelSerializer(invited_memebers, many=True).data,
			'invitations'      : invitations
		}

		return Response(data)

	def create(self, request, *args, **kwargs):
		# Handle member cration from invitation code
		serializer = AddMemberSerializer(
			data = request.data,
			context = {'circle': self.circle, 'request': request}
		)
		serializer.is_valid(raise_exception=True)
		member = serializer.save()

		data = self.get_serializer(member).data 	#serializer_class 
		return Response(data, status = status.HTTP_201_CREATED)