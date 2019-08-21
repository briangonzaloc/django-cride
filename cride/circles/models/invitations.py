"""Circle invitations models
"""

# Django
from django.db import models

#Utilities
from cride.utils.models import CRideModel

#Managers
from cride.circles.managers import InvitationManager

class Invitation(CRideModel):
	"""Circle invitation

	A circle invitation is a random text that acts as 
	a unique code that grants access to a specif circle,
	This codes are generated by users that are already
	members of the circle and habe a 'remaining_invitations'
	values greater that 0
	"""

	code = models.CharField(max_length=50, unique=True)
	issued_by = models.ForeignKey(
		'users.User',
		on_delete=models.CASCADE,
		help_text='Circle member that is provinding the invitation',
		related_name='issued_by'
	)
	used_by = models.ForeignKey(
		'users.User',
		on_delete=models.CASCADE,
		null=True,
		help_text='User that used the code to enter the circle'
	)

	circle = models.ForeignKey('circles.Circle', on_delete=models.CASCADE)

	used    = models.BooleanField(default=True)
	used_at = models.DateTimeField(blank=True, null=True)

	objects = InvitationManager()

	def __str__(self):
		#Return code and circle
		return '#{}: {}'.format(self.code, self.circle.slug_name )
