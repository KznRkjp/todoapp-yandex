#import debug_toolbar #comment out before upload to heroku
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', include('tasks.urls', namespace="tasks")),
    path('tasks/', include('tasks.urls', namespace="tasks")),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#comment out before upload to heroku
#if settings.DEBUG:
#    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
