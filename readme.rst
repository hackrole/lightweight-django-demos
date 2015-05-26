light-weight-django第一章
=========================

通过单一文件实现一个django hello-world app.

在文件的开头用django.conf.settings.configure来配置django settings.
并设置url file为__file__.

接下来的内容及时view/urls.

需要注意::
    1) urlpattern必须定义，用于找到url列表.
    2) application必须定义，用于wsgi启动

最后通过__name__ == "__main__" 来执行django命令.

收获
----

django功能划分
~~~~~~~~~~~~~~

django的设计思路是讲一个大而复杂的service, 分解为功能相对集中单一，可单独安装使用(可复用，低依赖)的app.
这点其实很困难，而且必须在项目开始时就考虑如果良好的划分功能模块.也是最能区分程序员水平地方。

uwsgi vs gunwsgi
~~~~~~~~~~~~~~~~~

uwsgi性能想对于gunwsgi提高大约有10%-15%.
但是问题是uwsgi配置复杂，而且有相当多的坑.
而gunuwsgi配置相对简单医用，而且执行启动脚本这点也是杀手级features.
后续可以多考虑使用gunwsgi取代uwsgi

django sign
~~~~~~~~~~~

django1.7新增一些安全相关的特性::
    1) settings必须执行allow_host.
    2) django.sign(具体还不太了解)

django template
~~~~~~~~~~~~~~~

django startproject可以制定一个特定目录,
可以自己创建一个模板用于app初始化
