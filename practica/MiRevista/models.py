from django.db import models


# Create your models here.

#user: grex foreignkeys id(user)
#identificador
#propiedad

class Users_News(models.Model):
	id_new=models.IntegerField()
	usuario=models.CharField(max_length=50)
	date_selection=	models.DateTimeField(auto_now_add=True)

class News(models.Model):
	title_news=models.CharField(max_length=50)
	date_publication=models.DateTimeField()
	url_news=models.URLField()
	content=models.TextField()
	channel=models.IntegerField()

class Users (models.Model):
	usuario=models.CharField(max_length=50)
	name_mag=models.CharField(max_length=50)
	fecha=models.DateTimeField()


class Channel(models.Model):
	title_channel=models.CharField(max_length=50)
	rss=models.URLField()
	logo=models.URLField()
	url_channel=models.URLField()
	update=models.DateTimeField()
	total_noticias=models.IntegerField()

class Users_Count(models.Model):
	usuario=models.CharField(max_length=50)
	count=models.IntegerField()



class Users_Css(models.Model):
	usuario=models.CharField(max_length=50)
	body_background=models.CharField(max_length=50)
	left_background=models.CharField(max_length=50)
	left_color=models.CharField(max_length=50)
	rigth_background=models.CharField(max_length=50)
	rigth_color=models.CharField(max_length=50)
	
class User_Coment(models.Model):
	usuario=models.CharField(max_length=50)
	comentario=models.CharField(max_length=50)
	nombre=models.CharField(max_length=50)
	fecha=models.DateTimeField(auto_now_add=True)

#RELATIONS#

#class Channel_News(models.Model):
#	id_new=models.IntegerField()
#	id_channel=models.IntegerField()
	


