from django.urls import path

from api.views import WebHookGrabber

urlpatterns = [
    path('', WebHookGrabber.as_view()),
]
