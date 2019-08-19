# circles views

# Django
# from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

#Serializers
from cride.circles.serializers import CircleSerializer, CreateCircleSerializer

# Models
from cride.circles.models import Circle

@api_view(['GET'])
def list_circles(request):
	circles = Circle.objects.filter(is_public=True)
	serializer = CircleSerializer(circles, many=True)
	# data = []
	# for circle in circles:
	# 	# data.append({
	# 	# 	'name'          : circle.name,
	# 	# 	'slug_name'     : circle.slug_name,
	# 	# 	'rides_taken'   : circle.rides_taken,
	# 	# 	'rides_offered' : circle.rides_offered,
	# 	# 	'members_limit' : circle.members_limit,
	# 	# })
	# 	serializer = CircleSerializer(circle)
	# 	data.append(serializer.data)
	# return Response(data)
	return Response(serializer.data)


@api_view(['POST'])
def create_circle(request):
	#Create circle

	serializer = CreateCircleSerializer(data=request.data)
	serializer.is_valid(raise_exception=True)
	circle = serializer.save()
	# data = serializer.data
	# circle = Circle.objects.create(**data)


	# name = request.data['name']
	# slug_name = request.data['slug_name']
	# name = request.data['name']
	# about = request.data.get('about','')

	# circle = Circle.objects.create(name=name, slug_name=slug_name, about=about)

	# data = {
	# 	'name'          : circle.name,
	# 	'slug_name'     : circle.slug_name,
	# 	'rides_taken'   : circle.rides_taken,
	# 	'rides_offered' : circle.rides_offered,
	# 	'members_limit' : circle.members_limit,
	# }

	return Response(CircleSerializer(circle).data)