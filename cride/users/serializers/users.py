"""Users serializers
"""

#Django
from django.contrib.auth import authenticate, password_validation
from django.core.validators import RegexValidator

# Django Rest framework
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


# Models
from cride.users.models import User, Profile

class UserModelSerializer(serializers.ModelSerializer):
	# User model serializer
	class Meta:
		model  = User
		fields = (
			'username',
			'first_name',
			'last_name',
			'email',
			'phone_number'
		)

class UserSignUpSerializer(serializers.Serializer):
	# User signup serializer
	# Handle sign up data validation and user/profile creation

	email = serializers.EmailField(
		validators=[UniqueValidator(queryset=User.objects.all())]
	)
	username = serializers.CharField(
		min_length=4,
		max_length=20,
		validators=[UniqueValidator(queryset=User.objects.all())],
	)
	phone_regex = RegexValidator(
		regex=r'\+?1?\d{9,15}$',
		message='Phone number must be entered in the format +999999999. Up to 15 digits allowed.'
	)
	phone_number          = serializers.CharField(validators=[phone_regex])
	password              = serializers.CharField(min_length=8, max_length=64)
	password_confirmation = serializers.CharField(min_length=8, max_length=64)

	# Name
	first_name = serializers.CharField(min_length=2, max_length=30)
	last_name = serializers.CharField(min_length=2, max_length=30)

	def validate(self,data):
		#Verify password match
		passwd = data['password']
		passwd_conf = data['password_confirmation']
		if passwd != passwd_conf:
			raise serializers.ValidationError("Passwords don't match.")
		password_validation.validate_password(passwd)
		return data

	def create(self,data):
		#Handle user and profile creation
		data.pop('password_confirmation')
		user = User.objects.create_user(**data, is_verified=False)
		Profile.objects.create(user=user)
		return user



class UserLoginSerializer(serializers.Serializer):
	""" User login serializer
	Handle the login request data
	"""

	email    = serializers.EmailField()
	password = serializers.CharField(min_length=8, max_length=64)

	def validate(self, data):
		#check credentials. 
		user = authenticate(username=data['email'], password=data['password'])
		if not user:
			raise serializers.ValidationError('Invalid credentials.')

		if not user.is_verified:
			raise serializers.ValidationError('Account is not active yet.')

		self.context['user'] = user
		return data

	def create(self, data):
		#Generate or retrieve new token
		# crete is executed after validate
		token, created = Token.objects.get_or_create(user=self.context['user'])
		return self.context['user'], token.key