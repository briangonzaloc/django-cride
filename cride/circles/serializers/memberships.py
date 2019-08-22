#Memship serializers

#Django 
from django.utils import timezone

#Django REST framework
from rest_framework import serializers

# Models
from cride.circles.models import Membership, Invitation

# Serializer
from cride.users.serializers import UserModelSerializer

class MembershipModelSerializer(serializers.ModelSerializer):
	# Member model serializer
	user       = UserModelSerializer(read_only=True)
	invited_by = serializers.StringRelatedField()
	joined_at  = serializers.DateTimeField(source='created', read_only=True)

	class Meta:
		model = Membership
		fields = (
			'user',
			'is_admin', 'is_active',
			'used_invitations', 'remaining_invitations',
			'invited_by',
			'rides_taken', 'rides_offered',
			'joined_at'
		)

		read_only_fields = (
			'user',
			'used_invitations',
			'invited_by',
			'rides_taken', 'rides_offered'
		)

class AddMemberSerializer(serializers.ModelSerializer):
	"""Add member serializer
	Handle the addition of a new member to a circle
	Circle object must be provided in the context
	"""

	invitation_code = serializers.CharField(min_length=8)
	user = serializers.HiddenField(default=serializers.CurrentUserDefault())

	#3. validate that we donot exceed the limit of de members

	def validate_user(self, data):
		# verify uer is not already a member
		circle = self.context['circle']
		user = data
		q = Membership.objects.filter(circle=circle, user=user)
		if q.exists():
			raise serializers.ValidationError('User is already member of the circle')
		# return data

	def validate_invitation_code(self, data):
		#verify code exists and that it is related to the circle.
		try:
			invitation = Invitation.objects.get(
				code=data,
				circle=self.context['circle'],
				used=False
			)
		except Invitation.DoesNotExist:
			raise serializers.ValidationError('Invalid invation code')

		self.context['invitation'] = invitation
		return data

	def validate(self, data):
		#verify circle is capable of accepting a new member
		circle = self.context['circle']
		if circle.is_limited and circle.members.count() >= circle.members_limit:
			raise serializers.ValidationError('Circle has reached its member limit.')
		return data

	def create(self, data):
		#Create a new member 
		circle = self.context['circle']
		invitation = self.context['invitation']
		user = data['user'] #from HIdden field

		now = timezone.now()

		#Mmeber creation
		member = Membership.objects.create(
			user=user,
			profile=user.profile,
			circle=circle,
			invited_by=invitation.issued_by
		)

		#Update invitation
		invitation.used_by = user
		invitation.used= True
		invitation.used_at = now
		invitation.save()

		# Update issuer data
		issuer = Membership.objects.get(user=invitation.issued_by, circle=circle)
		issuer.used_invitations += 1
		issuer.remaining_invitations -= 1
		issuer.save()

		return member