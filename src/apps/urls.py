from django.conf import settings
from django.conf.urls import patterns, include, url

import django.contrib.admin

django.contrib.admin.autodiscover()


urlpatterns = patterns('',
    url(r'^', include('apps.website.urls', namespace='website')),
    url(r'^admin/', include('apps.admin.urls', namespace='admin')),
    url(r'^django_admin/', include(django.contrib.admin.site.urls)),
    url(r'^wechat/', include('apps.wechat.urls', namespace='wechat')),
)

urlpatterns += patterns('',
    url(r'^captcha/', include('captcha.urls')),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', dict(document_root=settings.MEDIA_ROOT)),
    )
