from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *
import django.contrib.auth.views
from django.views.generic.simple import direct_to_template
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from django.conf.urls.defaults import *
from MiRevista.rss import rss_user
from MiRevista.rss import rss_mag

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'practica.views.home', name='home'),
    # url(r'^practica/', include('practica.foo.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    #url(r'^channel/(?P<num>[\d])/login$', 'MiRevista.views.num_login'),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^(images/xfuera.jpg)$', 'django.views.static.serve',{'document_root':'Templates'}),
    url(r'^(images/not-found-404-try-again.png)$','django.views.static.serve',{'document_root':'Templates'}),
    url(r'^(images/icon.ico)$', 'django.views.static.serve',{'document_root':'Templates'}),
    url(r'^(images/rss.jpg)$', 'django.views.static.serve',{'document_root':'Templates'}),

    url(r'^$', 'MiRevista.views.home'),
    url(r'^css/(?P<path>.*)$', 'django.views.static.serve',{'document_root': 'Templates/css'}), 
    url(r'^ayuda$','MiRevista.views.ayuda'),
    url(r'^rss$',rss_mag()),
    url(r'^login', 'django.contrib.auth.views.login'),
    #url(r'^logout', 'django.contrib.auth.views.logout'),
    url(r'^logout', 'MiRevista.views.logout'),

    url(r'^channel/logout', 'MiRevista.views.channel_logout'),
    #url(r'^login', 'MiRevista.views.login'),
    url(r'^canales$', 'MiRevista.views.channel'),
    url(r'^comentar/(.*)$', 'MiRevista.views.comment'),
    url(r'^borrar/(?P<num>[\d]+)$', 'MiRevista.views.borrar_canal'),
    url(r'^actualizar/(?P<num>[\d]+)$','MiRevista.views.actualizar'),
    url(r'^elegir/(?P<num>[\d]+)$', 'MiRevista.views.elegir'),
    url(r'^canales/(?P<num>[\d]+)$', 'MiRevista.views.num_channel'),
    url(r'^canales/(?P<num>[\d]+)/logout$', 'MiRevista.views.num_logout'),
    url(r'^new_user', 'MiRevista.views.crear_user'),
    url(r'^css$','MiRevista.views.usuario_css'),
    url(r'^nombre_revista','MiRevista.views.nombre_revista'),
    url(r'^(.*)/borrar/(\d+)$', 'MiRevista.views.borrar_noticia'),
    url(r'^(.*)/logout$', 'MiRevista.views.usuario_logout'),
    url(r'^(.*)/rss$',rss_user()),
    url(r'(.*)$', 'MiRevista.views.usuario'),
)
