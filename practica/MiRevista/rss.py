from django.contrib.syndication.views import Feed
from django.contrib.syndication.views import FeedDoesNotExist
from django.utils import feedgenerator

from django.contrib import admin
from models import Users
from models import Channel
from models import News
from models import Users_News
from models import Users_Css
from models import Users_Count

class rss_user(Feed):
	"""docstring for rss_user"""
	
	
	def title (self, obj):
		return obj.usuario 

	def link(self, obj):
		return "/"+obj.usuario

	def description(self,obj):
		return obj.usuario+"'s feed"

	def pubDate(self,obj):
		return str(Users.objects.get(usuario=obj.usuario).fecha)

	def lastBuildDate(self,obj):
		return str(Users.objects.get(usuario=obj.usuario).fecha)

	def get_object(self, request, usuario):
		return Users(Users, usuario=usuario)


	def items(self,obj):	
		return Users_News.objects.filter(usuario=obj.usuario).order_by('-date_selection')[:10]

	def item_title(self, item):
		return News.objects.get(id=item.id_new).title_news
	
	def item_link(self, item):
		return News.objects.get(id=item.id_new).url_news

	def item_description(self,item):
		return News.objects.get(id=item.id_new).content

	def item_pubDate(self, item):
		return obj.date_selection

class rss_mag(Feed):
	"""docstring for rss_user"""
	
	
	title = "MiRevista"
	link="/"
	description="MiRevista's feed"
	

	def pubDate(self,obj):
		return str(Users.objects.get(usuario=obj.usuario).fecha)

	def lastBuildDate(self,obj):
		return str(Users.objects.get(usuario=obj.usuario).fecha)

	def get_object(self, request):
		return Users_News.objects.all()


	def items(self,obj):	
		return obj.order_by('-date_selection')

	def item_title(self, item):
		return News.objects.get(id=item.id_new).title_news
	
	def item_link(self, item):
		return News.objects.get(id=item.id_new).url_news

	def item_description(self,item):
		return News.objects.get(id=item.id_new).content

	def item_pubDate(self, item):
		return item.date_selection

	def  item_author_name(self, item):
		return item.usuario