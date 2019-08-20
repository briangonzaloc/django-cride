"""Circle URLS
"""

# Django 
from django.urls import path, include

# DJango REST framework
from rest_framework.routers import DefaultRouter

# Views
from .views import circles as circle_views

router = DefaultRouter()
router.register(r'circles', circle_views.CircleViewSet, basename='circle')

urlpatterns = [
	path('', include(router.urls))
]

# #Views
# from cride.circles.views import list_circles, create_circle

# urlpatterns = [
# 	path('circles/', list_circles),
# 	path('circles/create/', create_circle),

# ]

