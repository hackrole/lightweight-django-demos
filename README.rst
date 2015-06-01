lightweight-django第四章
========================

本章使用django-rest-framework完成一个scrum任务管理服务.
配合django-filter做url查询和过滤.

sprint表为冲刺目标, task为子任务表. 配合使用django auth模块的user表完成认证和权限管理.

需要注意的是书中使用python3, 语法上和python2.7有写区别会导致部分bug.
还有由于使用的djangorestframework版本较低导致部分bug的问题。

收获
----

1) django-auth是相对通用化的一个app,应该在项目中尽可能的使用.

2) 考虑分离用户数据和用户认证相关的密码帐号也是不错的设计。

3) 使用viewmixin多继承来使代码有更低的重复性，同时要注意不要有太复杂的类继承管理.代码重复和类继承管其之间要取得一个平衡。

4) django的serializer是很好的设计，不过用django紧耦合导致无法在tornado中使用.

5) 设计api前应该先设计url.

未完成的任务
------------

1) 学习django-viewset的流程，在tornado中复用这一设计.

2) 学习django-filter.

3) 学习taskpie,比较用djagnorestframework的区别.

4) 实现tornado-serializer模块.

5) 完成单元测试.

为解决的疑问
------------

1) 使用django-filters会导致url的不可见性，前端需要猜测api参数来完成调用。在浏览器上也需要手动拼写url参数.

2) 是否应该在api中格式化时间和返回status_diplay, 简化客户端处理同时使得后台对前台有一定的控制.当同时增加服务端的逻辑复杂程度，增加运维上的成本, 并且这种展示和内容分离的设计感觉上并不优雅.利弊之间需要多做权衡。

3) url连通的作用现在有点模糊，通过后台控制前端这样的设计由于c/s模式的一些特性未必是个很好的选择，现在看来最大的好处在于接口调试时可以更加方便,还有就是能避免拼接url导致的一些问题。
