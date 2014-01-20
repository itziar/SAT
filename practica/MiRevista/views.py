#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import os, sys

# Create your views here.

from django.contrib import auth
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect
from django.contrib import admin
from django.template.loader import get_template
from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response
import urllib2
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import sys
import string
import xml.sax
from django import *
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import datetime #para la hora
import feedparser
import urlparse
from django.contrib.syndication.views import Feed
import re
from django.contrib.syndication.views import FeedDoesNotExist
import BeautifulSoup                             # To get everything
from BeautifulSoup import BeautifulSoup          # For processing HTML
from django.contrib.contenttypes import generic

#crear usuario
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

#IMPORTAR MODELOS
from MiRevista.models import Users_News
from MiRevista.models import Users
from MiRevista.models import Channel
from MiRevista.models import News
from MiRevista.models import Users_Css
from MiRevista.models import Users_Count
from MiRevista.models import User_Coment
#feed

#en la pagina web resultante <style "text/css "link "css/hoja.css">
#style "text/css" link "dinamic.css" hacer el css dinamico para que sea para cada usuario


def logout(request):
	auth.logout(request)
	return HttpResponseRedirect("/")

def channel_logout(request):
	auth.logout(request)
	return HttpResponseRedirect("/canales")

def num_logout(request,num):
	auth.logout(request)
	num=str(num)
	url="/canales/"+num
	return HttpResponseRedirect(url)

def usuario_logout(request,usuario):
	auth.logout(request)
	url="/"+usuario
	return HttpResponseRedirect(url)

def usuario_rss_logout(request,usuario):
	auth.logout(request)
	url="/"+usuario+"/rss"
	return HttpResponseRedirect(url)

def pag_principal():
	user=Users.objects.order_by('-fecha')
	contents=''
	for i in user:
		contents+="<a href=/"+i.usuario+">"+i.name_mag+"</a href>"
		contents+="  usuario: "
		contents+=i.usuario
		contents+=" "
		contents+=str(i.fecha)		
		try:
			count=Users_Count.objects.get(usuario=i.usuario).count
		except:
			count=0
		contents+=" Visitas: " + str(count)
		url="/comentar/"+i.usuario
		contents+="<td><form action='"+url+"' Method='GET'{% @csrf_token %}> <input type='hidden' value='"+str(i.usuario)+"'> <input type='submit' value='ver comentarios'></form>"+"</td></tr>"	
		contents+="<br></br>"
	return contents

@csrf_exempt
def comment(request,usuario):
	comentarios=""
	if request.method=='POST':
		try:
			nombre=request.POST['nombre']
			comentario=request.POST['comentario']
			comments=User_Coment(usuario=usuario,nombre=nombre,comentario=comentario)
			comments.save()
		except:
			pass	
		return HttpResponseRedirect("/comentar/"+usuario)
	else:
		c=User_Coment.objects.filter(usuario=usuario)
		for comment in c:
			comentarios+="<table border='1'>"
			comentarios+="<tr><td>Comentario de: "
			comentarios+=comment.nombre
			comentarios+=" "+ str(comment.fecha)+"</td>"
			comentarios+='<td>'+comment.comentario+'</td></tr>'
		comentarios+="</table><br></br>"
		if request.user.is_authenticated():
			user='<br/>'+'Logged in as ' + request.user.username + '.  <a href="/logout">Logout</a>'
		else:
			user='<br/>'+'Not logged in '+'<a href="/login">Login</a>'	
	revista=Users.objects.get(usuario=usuario).name_mag
	dictionary={'revista':revista,'user':user,'content':comentarios}	
	t=loader.get_template('comentarios.html')
	template=t.render(Context(dictionary))
	return HttpResponse(template)
	

@csrf_exempt
def home(request):
	if request.method=='GET':
		content=pag_principal()
		if request.user.is_authenticated():
			usuario='<br/>'+'Logged in as ' + request.user.username + '.  <a href="/logout">Logout</a>'
			user=request.user
			try:
				css=Users_Css.objects.get(usuario=user)
				dictionary={'user':usuario,'content':content,'left_color':css.left_color,'left_background':css.left_background,'rigth_color':css.rigth_color,'rigth_background':css.rigth_background,'body_background':css.body_background}
			except:	
				dictionary={'user':usuario,'content':content}
			t=loader.get_template('main.html')

		else:
			usuario='<br/>'+'Not logged in '+'<a href="/login">Login</a>'
			dictionary={'user':usuario,'content':content}
			t=loader.get_template('main_login.html')

		#elif request.Method=='POST':
		#contenido de la pagina principal: nombre de la revista del usuario, usuario, fecha de actualizacion
		template=t.render(Context(dictionary))
		return HttpResponse(template)
	else:
		username = request.POST['username']
		password = request.POST['password']
		user = auth.authenticate(username=username, password=password)
		if user is not None and user.is_active:
			auth.login(request, user)
		return HttpResponseRedirect("/")		

def ayuda(request):
	t=loader.get_template('ayuda.html')
	template=t.render(Context())
	return HttpResponse(template)

def Entry (entry, num, update,contador):
	"""Process an entry in the RSS channel.Returns the correspondign HTML, showing text, images, etc."""
	html = ''
	urls = extractUrls(entry.title)
	html += '<h3>' +  entry.title + '</h3>'
	html+= entry.updated
	html+=entry.description
	html+=entry.link
	title=entry.title
	url=entry.link
	f=entry.published_parsed
	fecha = datetime(f[0], f[1], f[2], f[3], f[4], f[5])
	description=entry.description
	if update<fecha:
		contador=contador+1
		salvar_noticia(title,url,fecha,description,num)
	html += '<br/>'
	return html+str(contador)

def actualizo(update,num):
	canales=Channel.objects.get(id=num)
	contador=canales.total_noticias
	feed=feedparser.parse(canales.rss)
	page=""
	for entry in feed.entries[:]:
		page += Entry (entry, num, canales.update, contador)
		page+="numero de noticias "+str(contador)
		page += '</body></html>'
	canales.total_noticias=contador
	canales.update=update
	canales.save()

@csrf_exempt
def actualizar(request,num):
	if request.method=='POST':
		c=Channel.objects.get(id=num)
		fecha=c.update
		feed=feedparser.parse(c.rss)
		try:
			f=feed.feed.updated_parsed
			update=datetime(f[0],f[1],f[2],f[3],f[4],f[5])
		except:
			update=datetime.now()
		if update!=fecha:
			actualizo(update, num)
		return HttpResponseRedirect("/canales/"+num)
		#cojo la fecha de ultima actualizacion, la comparo con la mia y si no es igual
			#guardo la nueva fecha
			#saco las noticias nuevas y las guardo

def contenido():
	channel=Channel.objects.all()
	contents=""
	contents+="<table border='1'>"
	for i in channel:
		if i.logo.startswith('http://'):
			contents+='<tr><td><img src="http://immediatenet.com/t/l3?Size=1024x768&amp;URL=' + i.logo+ '"align="midle" /></td>'
		elif i.logo.startswith('https://'):	
			contents+='<tr><td><img src=' + i.logo+ '"align="midle" /></td>'
		else:
			contents+="<tr><td>no tiene logo</td>"
		contents+="<td><a href = /canales/" +str(i.id)+">"+i.title_channel+"</a></br>"+str(i.update)+ " numero total de noticias: "+str(i.total_noticias)		
		url="/borrar/"+str(i.id)
		contents+="<td><form action='"+url+"' Method='POST'{% @csrf_token %}> <input type='hidden' value='"+str(i.id)+"'> <input type='submit' value='borrar'></form>"+"</td></tr>"	
	contents+="</table>"
	return contents

def extractUrls (text):
    """Extract urls from some text"""
    words = text.split(' ')
    return [word for word in words if word.startswith('http://')]

def linkWebshot (url):
    """Return HTML for a link to the webshot of an url"""
    return '<img src="http://immediatenet.com/t/l3?Size=1024x768&amp;URL=' + \
        url + '" align="right"/>'

def extractText (html):
    """Extract relevant text from some HTML.
    Returns the text coded in HTML"""
    textTags = BeautifulSoup(html).first(('p','em'))
    if textTags:
        textHTML = ''.join(textTags.findAll(text=True))
    else:
        textHTML = 'No text found'
    return '<div>' + textHTML + '</div><hr/>'

def processEntry (entry, num):
	"""Process an entry in the RSS channel.Returns the correspondign HTML, showing text, images, etc."""
	html = ''
	urls = extractUrls(entry.title)
	html += '<h3>' +  entry.title + '</h3>'
	html+= entry.updated
	html+=entry.description
	html+=entry.link
	title=entry.title
	url=entry.link
	f=entry.published_parsed
	fecha = datetime(f[0], f[1], f[2], f[3], f[4], f[5])
	description=entry.description
	salvar_noticia(title,url,fecha,description,num)
	html += '<br/>'
	return html

def salvar_noticia(title,url,fecha,description,num):
	noticia=News(title_news=title,date_publication=fecha,url_news=url,content=description, channel=num)
	noticia.save()

@csrf_exempt
#@login_required
def channel(request):
	if request.method=='GET':
		if request.user.is_authenticated():
			#html=('canal logo mensajes actualizacion')
			#print request.user
			usuario='<br/>'+ 'Logged in as ' + request.user.username + '. <a href="/channel/logout">Logout</a>'
			content=contenido()
			#canal=form_for_channel
			users=request.user
			new_channel=True
			try:
				css=Users_Css.objects.get(usuario=users)
				dictionary={'user': usuario, 'new_channel':new_channel, 'content': content,'left_color':css.left_color,'left_background':css.left_background,'rigth_color':css.rigth_color,'rigth_background':css.rigth_background,'body_background':css.body_background}		
			except:	
				dictionary={'user': usuario, 'new_channel':new_channel, 'content': content}
			t=loader.get_template('channel.html')
		else:
			usuario='<br/>'+'Not logged in '+'<a href="/channel/login">Login</a>'
			content='Por favor autentifiquese para ver el contenido'
			users=""
			new_channel=False
			dictionary={'user': usuario, 'new_channel':new_channel, 'content': content}
			t=loader.get_template('channel_login.html')
		template=t.render(Context(dictionary))		
		return HttpResponse(template)
	elif request.method=='POST':
		try:
			username = request.POST['username']
			password = request.POST['password']
			user = auth.authenticate(username=username, password=password)
			if user is not None and user.is_active:
				auth.login(request, user)
			return HttpResponseRedirect("/canales")
		except:
			pass
		try:
		#comprobar si es valido		
			url= request.POST['URL']
			canal=url		
			feed = feedparser.parse(canal)
			page = '<html><body>'
			if feed.status==200 and not Channel.objects.filter(rss=canal).exists():
				urlsFeed = []
				title=feed.feed.title
				page+=title    	
				contador=0			
				html = urllib2.urlopen(canal)
				soup = BeautifulSoup(html)
				#soup.prettify()
				try:
					src_img="sin imagen"
					imgs = soup.findAll(['image'])
					for j in imgs:
						img = str(j).split()
						for k in img:
							k = k.strip('</url>')
							if (k.startswith('http://') or k.startswith('https://')) \
									and ((k.endswith('.png') or k.endswith('.PNG')) or (k.endswith('.jpg') or k.endswith('.JPG')) or (k.endswith('.gif') or k.endswith('.GIF'))):
								src_img = k
				except:
					src_img="sin imagen"
				logo=src_img
				try:
					fecha=feed.feed.updated_parsed
					#[u"'time.struct_time(tm_year=2013, tm_mon=5, tm_mday=8, tm_hour=11, tm_min=55, tm_sec=5, tm_wday=2, tm_yday=128, tm_isdst=0)' value has an invalid date format. It must be in YYYY-MM-DD format."]
					update = datetime.datetime(fecha[0], fecha[1], fecha[2], fecha[3], fecha[4], fecha[5])
				except:
					update=datetime.now()
				page+=str(update)
				link=feed.feed.link
				page+=link
				url_rss=canal
				page+=canal
				salvar_canal(title,link,url_rss,logo,contador,update)
				canales=Channel.objects.get(title_channel=title)
				num=canales.id
				page+=str(num)
				for entry in feed.entries[:]:
					page += processEntry (entry, num)
					contador=contador+1

				print contador
				page+="numero de noticias "+str(contador)
				page += '</body></html>'
				canales.total_noticias=contador
				canales.save()
			return HttpResponseRedirect("/canales")
		except:
			return HttpResponseRedirect("/canales")


def salvar_canal(title,link,rss,logo,contador,update):	
	canal=Channel(title_channel=title,rss=rss,logo=logo, url_channel=link, update=update,total_noticias=contador)
	canal.save()

@csrf_exempt
def elegir(request, num):
	user=request.user
	if request.user.is_authenticated() and not Users_News.objects.filter(id_new=num,usuario=user).exists():
		usuario=request.user
		un=Users_News(id_new=num,usuario=usuario)
		un.save()
		canal=News.objects.get(id=num).channel
		fecha=datetime.now()
 		if not Users.objects.filter(usuario=usuario).exists():
 			mag="revista "+str(usuario)
 			usuario=Users(usuario=usuario, name_mag=mag, fecha=fecha)
 			usuario.save()
		else:
			u=Users.objects.get(usuario=usuario)
			u.fecha=fecha
			u.save()
	canal=News.objects.get(id=num).channel
	return HttpResponseRedirect("/canales/"+str(canal))

def number_cannel(num):
	num=int(num)	
	contents=""
	noticias=News.objects.filter(channel=num).order_by('-date_publication')
	for noti in noticias:
		contents+="<table>"
		url="/elegir/"+str(noti.id)
		contents+="<tr><a href=" + noti.url_news+ ">"+noti.title_news+"</a></tr></td>"
		contents+="<td><tr><form action='"+url+"' Method='POST'{% @csrf_token %}> <input type='hidden' value='"+str(noti.id)+"'> <input type='submit' value='elegir'></form></tr><br></br>"
		contents+="  Publicada en:"+ str(noti.date_publication)+'<br>'
		contents+=noti.content
		contents+='<br></br>'
		contents+="</table>"
	return contents

@csrf_exempt
def num_channel(request, num):
	num=str(num)
	Canales=Channel.objects.filter(id=num)
	for channel in Canales:
		title="<table>"
		title+="<td><h1><a href =" +channel.url_channel+">"+channel.title_channel+"</a>   "+"<a href="+channel.rss+">(canal)</a><h2>"+str(channel.update)+"</h2></h1></td>"
		url="/actualizar/"+str(num)
		title+="<td><form action='"+url+"' Method='POST'{% @csrf_token %}> <input type='hidden' value='"+str(num)+"'> <input type='submit' value='actualizar'></form>"
		title+="</table>"
	contenido=number_cannel(num)
	if request.method =='GET':
		if request.user.is_authenticated():
			usuario='<br/>'+'Logged in as ' + request.user.username + '.  <a href="/canales/'+num+'/logout">logout</a>'
			t=loader.get_template('channel_num.html')	
			users=request.user		
			try:
				css=Users_Css.objects.get(usuario=users)
				dictionary={'user':usuario,'title':title, 'content':contenido,'left_color':css.left_color,'left_background':css.left_background,'rigth_color':css.rigth_color,'rigth_background':css.rigth_background,'body_background':css.body_background}			
			except:	
				dictionary={'user':usuario,'title':title, 'content':contenido}
		else:
			t=loader.get_template('num_login.html')
			dictionary={'content':contenido}
	#contenido de la pagina principal: nombre de la revista del usuario, usuario, fecha de actualizacion		
		template=t.render(Context(dictionary))
		return HttpResponse(template)
	elif request.method=='POST':
		username = request.POST['username']
		password = request.POST['password']
		user = auth.authenticate(username=username, password=password)
		if user is not None and user.is_active:
			auth.login(request, user)
		return HttpResponseRedirect("/canales/"+num)

def user_registrado(usuario):
 	if User.objects.filter(username=usuario).exists():
 		if not Users.objects.filter(usuario=usuario).exists():
 			usuario=Users(usuario=usuario, name_mag="revista de " + usuario, fecha=datetime.now() )
 			usuario.save()
 		return True
 	else:
 		return False


def content_user(usuario):
	un=Users_News.objects.filter(usuario=usuario).order_by('-date_selection')
	contador=0
	contents=""
	for i in un:
		if contador<10:
			num=i.id_new
			noticia=News.objects.get(id=num)
			num_canal=noticia.channel
			canal=Channel.objects.get(id=num_canal)
			contents+="<a href="+noticia.url_news+">"+noticia.title_news+"</a href>"
			contents+="  Publicada en: "+str(noticia.date_publication)+"  "
			contents+="<a href=/canales/"+str(num_canal)+">"+canal.title_channel+"</a href><br></br>"		
			contents+=noticia.content
			contents+=" Elegida en: "+str(i.date_selection)	
			url=usuario+"/borrar/"+str(i.id_new)
			contents+="<td><form action='"+url+"' Method='POST'{% @csrf_token %}> <input type='hidden' value='"+str(num)+"'> <input type='submit' value='borrar'></form>"
			contents+="<br></br>"	
		else:
			pass
		contador=contador+1
	return contents
	
@csrf_exempt
def usuario(request, usuario):
	users_registrado=user_registrado(usuario)
	content=""
	if Users_Count.objects.filter(usuario=usuario).exists():
		contador=Users_Count.objects.get(usuario=usuario)
		counts=contador.count+1
		contador.delete()
		contador=Users_Count(usuario=usuario, count=counts)
		contador.save()
	else:
		contador=Users_Count(usuario=usuario, count=1)
		contador.save()
	if users_registrado:
		content+=content_user(usuario)
		mag=Users.objects.get(usuario=usuario).name_mag
		if request.method =='GET':
			if request.user.is_authenticated():
				user='<br/>'+ 'Logged in as ' + request.user.username + '. <a href="/'+usuario+'/logout">Logout</a>'
				t=loader.get_template('user.html')
				users=request.user
				try:
					css=Users_Css.objects.get(usuario=users)
					dictionary={'u':users,'user':user,'revista': mag,'content':content, 'usuario':usuario,'left_color':css.left_color,'left_background':css.left_background,'rigth_color':css.rigth_color,'rigth_background':css.rigth_background,'body_background':css.body_background}
				except:	
					dictionary={'u':users,'user':user,'revista': mag,'content':content, 'usuario':usuario}
			else:
				t=loader.get_template('user_login.html')
				dictionary={'revista': mag,'content':content, 'usuario':usuario}
	#contenido de la pagina principal: nombre de la revista del usuario, usuario, fecha de actualizacion
			template=t.render(Context(dictionary))
			return HttpResponse(template)
		elif request.method=='POST':
			username = request.POST['username']
			password = request.POST['password']
			user = auth.authenticate(username=username, password=password)
			if user is not None and user.is_active:
				auth.login(request, user)
			return HttpResponseRedirect("/"+usuario)
	else:
		t=loader.get_template('user_no_register.html')
		template=t.render(Context())
		return HttpResponse(template)

@csrf_exempt
def nombre_revista(request):
	user=request.user
	usuario=user
	if request.method=='GET':
		if request.user.is_authenticated():
			usuario='<br/>'+ 'Logged in as ' + request.user.username + '. <a href="/">Logout</a>'
			revista=Users.objects.get(usuario=user).name_mag
			t=loader.get_template('name_mag.html')
			try:
				css=Users_Css.objects.get(usuario=user)
				dictionary={'usuario':usuario,'user':user,'revista':revista,'left_color':css.left_color,'left_background':css.left_background,'rigth_color':css.rigth_color,'rigth_background':css.rigth_background,'body_background':css.body_background}
			except:	
				dictionary={'usuario':usuario,'user':user,'revista':revista}
			#t=loader.get_template('user.html')
			#users=request.user
		else:
			pass
		
		template=t.render(Context(dictionary))
		return HttpResponse(template)
	elif request.method=='POST':
		revista=Users.objects.get(usuario=usuario)
		mag=request.POST['revista']
		revista.name_mag=mag
		revista.save()
		url="/"+str(usuario)
		return HttpResponseRedirect(url)

@csrf_exempt
def borrar_canal(request,num):
	c=Channel.objects.get(id=num)
	c.delete()
	new=News.objects.filter(channel=num)
	for noti in new:
		un=Users_News.objects.filter(id_new=noti.id)
		for n in un:
			n.delete()
		noti.delete()
	return HttpResponseRedirect("/canales")


@csrf_exempt
def borrar_noticia(request,usuario, num):
	if request.method=='POST':
		noticia=Users_News.objects.get(id_new=num,usuario=usuario)
		noticia.delete()
	url="/"+usuario
	return HttpResponseRedirect(url)


@csrf_exempt
def crear_user(request):
	if request.method=='GET':
		formulario=UserCreationForm()
	elif request.method=='POST':
		formulario=UserCreationForm(request.POST)
		if formulario.is_valid():
			formulario.save()
			users=request.POST['username']
			usuario=User.objects.get(username=users).username
			username = request.POST['username']
			password = request.POST['password1']
			user = auth.authenticate(username=username, password=password)
			if user is not None and user.is_active:
				auth.login(request, user)
			print usuario
			user_registrado(usuario)
			return HttpResponseRedirect('/')		
	return render_to_response('newuser.html',{'formulario':formulario}, context_instance=RequestContext(request))

@csrf_exempt
def usuario_css(request):
	if request.method=='GET':
		if request.user.is_authenticated():
			usuario='<br/>'+ 'Logged in as ' + request.user.username + '. <a href="/">Logout</a>'
			t=loader.get_template('css.html')
			users=request.user
			try:
				css=Users_Css.objects.get(usuario=users)
				dictionary={'usuario':usuario,'revista': "cambiar css",'left_color':css.left_color,'left_background':css.left_background,'rigth_color':css.rigth_color,'rigth_background':css.rigth_background,'body_background':css.body_background}
			except:	
				dictionary={'usuario':usuario,'revista': "cambiar css"}
			
		else:
			dictionary={}
		template=t.render(Context(dictionary))
		return HttpResponse(template)
	elif request.method=='POST':
		username=request.user
		background=request.POST['back_color']

		left_color=request.POST['left_color']
		left_back=request.POST['left_back']
		rigth_color=request.POST['rigth_color']
		rigth_back=request.POST['rigth_back']
		if Users_Css.objects.filter(usuario=request.user).exists():
			user=Users_Css.objects.get(usuario=request.user)
			user.delete()
			user=Users_Css(usuario=username,left_color=left_color,left_background=left_back,rigth_color=rigth_color,rigth_background=rigth_back,body_background=background)
			user.save()
		else:
			css=Users_Css(usuario=username,left_color=left_color,left_background=left_back,rigth_color=rigth_color,rigth_background=rigth_back,body_background=background)
			css.save()
		url="/css"
		return HttpResponseRedirect(url)