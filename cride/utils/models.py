#Django models utilities

# Django
from django.db import models

class CRideModel(models.Model):
	"""Comparte Rise Base model
	CRideModel acts as an abstract base class from which every
	other model in the project will inherit. This class provides
	every table with the following attributes:
		+ create (DateTime): Store the datetime the object was created
		+ modified (DateTime): Store the last datetime the object was modified
	"""
	created = models.DateTimeField(
		'created_at',
		auto_now_add=True,
		help_text='Date time on which the object was created.'
	)

	modified = models.DateTimeField(
		'modified_at',
		auto_now=True,
		help_text='Date time on which the object was last modified.'
	)

	class Meta:
		#Meta option
		abstract      =True
		get_latest_by ='created'
		ordering      = ['-created', '-modified']


# class Student(CRideModel)
# 	name = models.CharField()

# 	# Para heredar de Meta
# 	class Meta(CRideModel.META):
# 		db_table = 'student_role'
