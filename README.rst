lightweight-django第二章
========================

本章使用单个的py文件实现了一个简单的image占位服务.
通过使用PIL模块,返回一个黑色背景写有图片大小信息的固定大小的图片。
图片大小是由客户端传递过来，使用PIL模块生成.使用form来验证客户端参数.
并通过使用缓存的方式来加速.

另外实现了一个简单的首页，来返回使用和帮助信息.

收获
----

1) 使用etags来完成客户端缓存。具体的就是django的etags包装器。
2) 使用BytesIO来做字节码处理，返回图片数据.
3) 通过设置content-type配置图片2进制数据，直接返回一个图片.

其他
----

一直想实现一个图片服务器用来完成图片上传.
模仿七牛的处理方式, 做图片服务里使用callback的形式完成信息同步.
图片服务负责图片的上传和保存，之后通过http callback的信息来通过信息到应用服务器.

现在看过这章提供了一些不错的思路::
    1) 不在一次性生成多中规格的缩略图,而且与寻客户端求情特定大小的图片，然后做缩略图，并配合缓存使用.

    2) 考虑把原图直接存储在mongodo数据库中,通过生成图片缓存的方式来使用。但是要考虑能否配合nginx做良好的cdn转好，不然还是要考虑直接存图片文件的方式.

疑问
----

1) 单文件django project如何写单元测试.
