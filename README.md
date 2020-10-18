# TestPlatform

### 介绍
本项目是使用 Python+Django 搭建的测试平台，目前已初步完成接口自动化测试。

### 设计思路
测试执行的最小单元为测试用例，不同的测试用例组合成为一个测试场景，不同的测试场景组合成为一个测试计划。在不同的测试计划中，测试场景和测试用例是可以复用的。

### 已有功能
1、接口自动化功能；<br>
2、相似的测试用例和测试场景可以快速复制；<br>
3、基于Python的前置和后置处理器，可以方便的对测试用例进行定制化配置；<br>
4、测试用例、测试场景、测试计划可以方便的可视化管理；<br>
5、灵活的测试任务执行方式；<br>


### 使用
1、克隆项目<br>
 ```
 git clone https://github.com/leeyoshinari/TestPlatform.git
```
 
2、安装MySQL数据库，并创建一个数据库；

3、建议安装FastDFS，用于测试报告、测试截图保存；

4、修改配置文件`config.conf`；如使用FastDFS，则还要修改`client.conf`；

5、数据库表结构初始化
```
python manage.py makemigrations
python manage.py migrate
```

6、创建超级管理员，用于访问Django后台进行权限控制和新建用户
```
python manage.py createsuperuser
```

7、启动
```
python manage.py runserver 127.0.0.1:12121
```

8、添加普通用户 <br>
    访问 `http://ip:port/admin`，用超级管理员登陆，访问Django后台，可添加普通用户；
    
9、使用测试平台 <br>
    访问 `http://ip:port`，可进入测试平台；

### 部署
Django部署采用Nginx+uWSGI架构，整个部署的链路是 Nginx -> uWSGI -> Django Web程序，步骤如下：<br>
1、安装uwsgi
```
pip3 install uwsgi
```
安装完成后，一般无法直接输入uwsgi命令执行，需要建立软连接
```
ln -s /usr/local/python37/bin/uwsgi /usr/bin/uwsgi
```
2、修改uwsgi配置文件`uwsgi.ini`，只需要修改项目根目录，可根据需要选择是否修改端口

3、配置nginx，nginx安装部署请自行百度，这里只列出nginx配置文件。配置完成后，重启nginx
```
server {
        listen 12020;
        server_name localhost;
        location / {
                include uwsgi_params;
                # 这里的配置和uwsgi.ini中的socket一样
                uwsgi_pass 127.0.0.1:12121;
        }

        location /static {
                # 项目静态文件路径
                alias /home/TestPlatform/static;
        }
}
```
4、启动uwsgi
```
uwsgi uwsgi.ini
```
5、部署完成，访问nginx端口即可

### Requirements
1、Django >= 3.1.1 <br>
2、requests >= 2.24.0 <br>
3、PyMySQL >= 0.10.0 <br>
4、uWSGI >= 2.0.19.1 <br>
