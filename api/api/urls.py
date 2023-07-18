from django.urls import path

from api.views import WebHookGrabber, GrabView

urlpatterns = [
    path('', WebHookGrabber.as_view()),
    path('<slug:app>', WebHookGrabber.as_view()),
    path('<slug:app>/', WebHookGrabber.as_view()),
    path('<slug:app>/<slug:scope>', WebHookGrabber.as_view()),
    path('<slug:app>/<slug:scope>/', WebHookGrabber.as_view()),
    path('grab/<slug:app>/<slug:scope>/', GrabView.as_view()),
]
