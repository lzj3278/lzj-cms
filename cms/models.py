# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# from ckeditor.fields import RichTextField



class NewUser(AbstractUser):
	profile = models.CharField('prifile', default='', max_length=256)
	avatat = models.ImageField(upload_to='avatar/%Y/%m', default='avatar/default.png', max_length=256, blank=True)
	
	def __unicode__(self):
		return self.username


class Column(models.Model):
	name = models.CharField('column_name', max_length=256)
	intro = models.TextField('introduction', default='')
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		verbose_name = '分类'
		verbose_name_plural = 'columns'
		ordering = ['name']


class Article(models.Model):
	column = models.ForeignKey('Column', blank=True, null=True, verbose_name='belong to')
	title = models.CharField(max_length=200)
	author = models.ForeignKey('Author')
	user = models.ManyToManyField('NewUser', blank=True)
	content = models.TextField('content')
	pub_date = models.DateTimeField(auto_now_add=True, editable=True)
	update_date = models.DateTimeField(auto_now=True, null=True)
	published = models.BooleanField('notdraft', default=True)
	poll_num = models.IntegerField(default=0)
	comment_num = models.IntegerField(default=0)
	keep_num = models.IntegerField(default=0)
	
	def __unicode__(self):
		return self.title
	
	class Meta:
		verbose_name = 'article'
		verbose_name_plural = 'article'


class Comment(models.Model):
	user = models.ForeignKey('NewUser', null=True)
	article = models.ForeignKey('Article', null=True)
	content = models.TextField()
	pub_date = models.DateTimeField(auto_now_add=True, editable=True)
	poll_num = models.IntegerField(default=0)
	
	def __unicode__(self):
		return self.content


class Author(models.Model):
	name = models.CharField(max_length=256)
	profile = models.CharField('profile', default='', max_length=256)
	password = models.CharField('password', max_length=256)
	register_date = models.DateTimeField(auto_now_add=True, editable=True)
	
	def __unicode__(self):
		return self.name


class Article_Poll(models.Model):
	user = models.ForeignKey('NewUser', null=True)
	article = models.ForeignKey('Article', null=True)


class Comment_poll(models.Model):
	user = models.ForeignKey('NewUser', null=True)
	comment = models.ForeignKey('Comment', null=True)
