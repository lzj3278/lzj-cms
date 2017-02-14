from django.contrib import admin
from . import models


# Register your models here.

class ArticleAdmin(admin.ModelAdmin):
	
	class Media:
		js = (
			'/static/kindeditor-4.1.7/kindeditor-min.js',
			'/static/kindeditor-4.1.7/lang/zh_CN.js',
			'/static/kindeditor-4.1.7/config.js',
		)


admin.site.register(models.NewUser)
admin.site.register(models.Article,ArticleAdmin)
admin.site.register(models.Author)
admin.site.register(models.Column)
admin.site.register(models.Comment)
admin.site.register(models.Article_Poll)
