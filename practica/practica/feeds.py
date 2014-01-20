from django.contrib.syndication.views import Feed
from django.contrib.syndication.views import FeedDoesNotExist
from django.core.urlresolvers import reverse

#from MiRevista.models import Users
#from MiRevista.models import Users_News
from MiRevista.models import Channel

class EntradaFeed(Feed):
    # atributos basicos del feed
    title='Mi Blog'
    link = "/blog/"
    description='Descripcion de la tematica del blog.'

    def items(self):
        # elementos del feed
        return Channel.objects.objects.all().order_by('-title_channel')
       

    def item_title(self, item): 
        return item.title_channel



    