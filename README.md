## Django 从0到1快速入门🎄

### 1. 运行仓库代码🚀

如果你需要深入学习django，请访问并仔细阅读

[Django官方文档]: https://docs.djangoproject.com/zh-hans/5.2/

本项目只是笔者对于django的一些看法，便于初学者学习与理解，如果有错误欢迎指正。如果该项目帮助到你，我将无比兴奋。你可以下载该仓库中的代码，同时确保你的windows系统中已经安装了MySQL。请在django/management/settings中配置你的数据库，具体配置方法如下

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'xxx',	# input your table name here
        'USER': 'root',
        'PASSWORD': 'xxx',	# input your password here
        'HOST': 'localhost',
        'PORT': '3306',		# input your sql serve port here, commonly 3306
    }
}
```

将本项目定义好的数据库进行迁移

```shell
cd /django
python manage.py makemigrations
python manage.py migrate
```

完成上述步骤后运行

```
python manage.py runserver
```

如果无误的话，恭喜你成功运行了本仓库中展示的客户信息管理系统！

### 2.Django从0到1🌋

Django是一个完整的前后端开发框架，在成功安装Django后，你可以使用如下指令在目标文件夹target_dir创建一个项目site。

此时target_dir文件夹下的目录结构如下。

```shell
django-admin startproject site target_dir

# 目录结构
target_dir/
    manage.py
    site/
        __init__.py
        settings.py
        urls.py
        asgi.py
        wsgi.py
```

其中，manage.py是Django中封装好的工具管理器。你可以发现manage.py中并没有写任何有关其功能的代码，但是其实Django已经将相关功能封装在python包中，并统一通过manage.py进行管理。因此你可以通过manage.py执行相当多的工作，如开启服务器、执行数据库修改等操作。site目录下存放的是该项目的主站点，urls中定义了该项目所有定义的路径。主站点一般不用来实际编写前后端代码。

Django允许你在上述的项目中创建多个子应用。

```powershell
python manage.py startapp myapp

# 目录结构
myapp/
    __init__.py
    admin.py
    apps.py
    migrations/
        __init__.py
    models.py
    tests.py
    views.py
```

这将在你的代码中创建一个子应用myapp，你可以将其配置到主站点中，从而通过主站点调用你创建的若干个应用程序。该目录结构中，models.py文件用来定义数据库模型，urls中用来规定该应用程序的相对路由，views中用来撰写各个urls对应的响应方法。



如果是初次使用Django，我建议在该应用程序的目录下建立文件夹templates用来存放前端代码。

```shell
cd /myapp
mkdir templates
```

此时你可以在templates建立一个前端界面

```html
<!-- hello.html -->
<div>
Hello, {{username}}!
</div>
```

接着在views.py中配置响应视图。可以通过context字典将后端值传入到前端界面并显示。

```python
def helloView(request):
	username = "Django"
	context = {
		'username': username,
	}
	
	return render(request, "hello.html", context)
```

在/myapp/urls.py中为该视图分配urls：

```python
from django.urls import path
from . import views


urlpatterns = [
    path('', views.helloView, name='hello'),
] 
```

在主站点site/urls.py文件中

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include('myapp.urls'))
]
```

运行主站点

```
python manage.py runserver
```

此时你将发现自己编写的html代码已经成功打印在服务器上，同时执行了views中的视图函数，成功将views中的值传入到前端页面。使用上述方法，你可以轻而易举的通过views从数据库中提取你需要的相关信息，并且通过context传入到前端代码，在前端代码中只需要通过`{{name}}`的方式即可调用

