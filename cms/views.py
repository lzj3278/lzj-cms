# -*- coding:utf-8 -*-
import urlparse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger

from . import forms
from . import models


# Create your views here.
def index(request):
	loginform = forms.LoginForm()
	last_article_list = models.Article.objects.get_queryset().order_by('-pub_date')
	paginator = Paginator(last_article_list, 4)
	try:
		page = int(request.GET.get('page', 1))
		last_article_list = paginator.page(page)
	except (EmptyPage, InvalidPage, PageNotAnInteger):
		last_article_list = paginator.page(1)
	content = {'contacts': last_article_list, 'loginform': loginform}
	return render(request, 'index.html', content)


def log_in(request):
	if request.method == 'GET':
		form = forms.LoginForm()
		return render(request, 'login.html', {'form': form})
	if request.method == 'POST':
		form = forms.LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['uid']
			password = form.cleaned_data['pwd']
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				return redirect('/cms/')
			else:
				return render(request, 'login.html', {'form': form, 'error': '用户或密码不正确'})
		else:
			return render(request, 'login.html', {'form': form})


@login_required()
def log_out(request):
	logout(request)
	return redirect('/cms/')


def article(request, article_id):
	article = get_object_or_404(models.Article, id=article_id)
	# content = markdown2.markdown(article.content, extras=["code-friendly",
	# 													  "fenced-code-blocks", "header-ids", "toc", "metadata"])
	commentform = forms.CommentForm()
	loginform = forms.LoginForm()
	comments = article.comment_set.all()
	contents = {
		'article': article,
		'content': article.content,
		'commentform': commentform,
		'loginform': loginform,
		'comments': comments
	}
	return render(request, 'article_page.html', contents)


@login_required()
def comment(request, article_id):
	form = forms.CommentForm(request.POST)
	if form.is_valid():
		new_comment = form.cleaned_data['comment']
		user = request.user
		article = models.Article.objects.get(id=article_id)
		models.Comment.objects.create(user=user, content=new_comment, article_id=article_id)
		article.comment_num += 1
		article.save()
	url = urlparse.urljoin('/cms/', article_id)
	return redirect(url)


@login_required()
def get_keep(request, article_id):
	logged_user = request.user
	article = models.Article.objects.get(id=article_id)
	articles = logged_user.article_set.all()
	url = urlparse.urljoin('/cms/', article_id)
	if article not in articles:
		article.user.add(logged_user)
		article.keep_num += 1
		article.save()
		return redirect(url)
	else:
		article.user.remove(logged_user)
		article.keep_num -= 1
		article.save()
		return redirect(url)


@login_required()
def get_poll_article(request, article_id):
	logged_user = request.user
	article = models.Article.objects.get(id=article_id)
	polls_article = logged_user.article_poll_set.all()
	articles = []
	url = urlparse.urljoin('/cms/', article_id)
	for poll in polls_article:
		articles.append(poll.article)
	if article not in articles:
		article.poll_num += 1
		article.save()
		models.Article_Poll.objects.create(user=logged_user, article=article)
		
		return redirect(url)
	else:
		models.Article_Poll.objects.get(user=logged_user, article=article).delete()
		article.poll_num -= 1
		article.save()
		return redirect(url)


@login_required()
def get_poll_comment(request, comment_id, article_id):
	logged_user = request.user
	comment = models.Comment.objects.get(id=comment_id)
	polls_comment = logged_user.comment_poll_set.all()
	comments = []
	url = urlparse.urljoin('/cms/', article_id)
	for poll in polls_comment:
		comments.append(poll.comment)
	if comment not in comments:
		comment.poll_num += 1
		comment.save()
		models.Comment_poll.objects.create(user=logged_user, comment=comment)
		return redirect(url)
	else:
		models.Comment_poll.objects.get(user=logged_user, comment=comment).delete()
		comment.poll_num -= 1
		comment.save()
		return redirect(url)


def register(request):
	error1 = "用户已经注册"
	valid = "用户名可用"
	if request.method == 'GET':
		form = forms.RegisterForm()
		return render(request, 'register.html', {'form': form})
	if request.method == 'POST':
		form = forms.RegisterForm()
		if request.POST.get('raw_username', 'asdasda212asd2!@#') != 'asdasda212asd2!@#':
			try:
				user = models.NewUser.objects.get(username=request.POST.get('raw_username', ''))
			except ObjectDoesNotExist:
				return render(request, 'register.html', {'form': form, 'msg': valid})
			else:
				return render(request, 'register.html', {'form': form, 'msg': error1})
		else:
			form = forms.RegisterForm(request.POST)
			if form.is_valid():
				username = form.cleaned_data['username']
				email = form.cleaned_data['email']
				password1 = form.cleaned_data['password1']
				password2 = form.cleaned_data['password2']
				if password1 != password2:
					return render(request, 'register.html', {'form': form, 'msg': '两次密码不一致'})
				else:
					user = models.NewUser(username=username, email=email)
					user.set_password(password1)
					user.save()
					return redirect('/cms/login/')
			else:
				return render(request, 'register.html', {'form': form})


def search_article(request):
	keyword = request.GET.get('keyword', '')
	if keyword:
		article_list = models.Article.objects.get_queryset().order_by('-pub_date').filter(
			Q(title__contains=keyword) |
			Q(content__contains=keyword)
		)
	else:
		article_list = models.Article.objects.get_queryset().order_by('-pub_date')
	
	paginator = Paginator(article_list, 4)
	try:
		page = int(request.GET.get('page', 1))
		article_list = paginator.page(page)
	except (EmptyPage, InvalidPage, PageNotAnInteger):
		article_list = paginator.page(1)
	return render(request, 'search_result.html', {'contacts': article_list,'keyword':keyword})
