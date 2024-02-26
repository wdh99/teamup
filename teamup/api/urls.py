from django.urls import include, path
from rest_framework import routers
from api import views


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet)
router.register(r'space', views.SpaceViewSet)
router.register(r'post', views.PostViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('login',views.login)
    # path('space/', views.space),
    # path('space/<int:pk>/', views.space_detail),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

