# ABookDownloader

一款用于在[高等教育出版社Abook网站](http://abook.hep.com.cn)上下载资源的下载器。

## 如何使用？

[点击下载](https://github.com/HEIGE-PCloud/ABookDownloader/releases/download/1.0.2/ABookDownloaderV1.0.2.zip)

[备用地址](https://onedrive.gimhoy.com/1drv/aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBdFRLUzh6ZVEyU1NrT2h6c3Q1c1ljMXZqUDdldlE/ZT1pSmZ0aEY=..zip)

下载完成后解压缩

然后进入解压完的目录，双击打开`ABookDownloader.exe`即可使用啦！

### 如果出现乱码如何解决？

安装[Windows Terminal](https://www.microsoft.com/zh-cn/p/windows-terminal/9n0dx20hk701)

将`ABookDownloader.exe`文件拖入`Windows Terminal`的窗口中

按下回车键，即可运行ww！

### 输入密码时发现无密码显示是什么情况？

为了保证密码的安全性，该脚本进行特意的设置避免明文密码暴露。

**在输入密码时不会显示密码，也不会显示`*`一类的占位符。**

**但只需要照常正确输入密码即可使用。**

## 已知问题

1. 由于使用的是默认的cmd终端，可能会有中文字符显示错误的问题。（都0202年了，请使用[Windows Terminal](https://www.microsoft.com/zh-cn/p/windows-terminal/9n0dx20hk701)）

   可行的临时修复方法：
   1. 进入控制面板
   2. 进入区域（region）
   3. 进入管理（Administrative）选择卡
   4. 点击更改系统区域设置（Change System Local...）按钮
   5. 将区域选择为中文（简体，中国）Chinese (Simplified, China)
   6. 确认设置并重新启动Windows

## 1.0.3版本更新

修复了文件中包含不合法字符时出现的下载失败问题。

## 1.0.2版本更新

修复了带有子目录的课程资源的显示与下载问题。

优化了登录流程。

## 1.0.1版本更新

增加了下载进度与速度显示，提高下载大文件/视频文件时的体验。

## 1.0版本正式发布啦！🎉

目前支持的功能：
1. 通过账号密码登录Abook，同时记住账号密码，方便下次登录。
2. 拉取所有绑定的书本，并支持一键下载所有课程资源！
3. 可单独选择一本书本，或其中某一章节进行下载。
4. 自动对下载的文件进行文件夹分类与命名。

可能添加的功能：
1. 完整的图形界面，彻底避免字符问题。
2. 可自定义的文件保存地址。
3. 账号本地储存加密。
4. and so on!

如果在使用过程中遇到问题，欢迎提交issue！
玩得开心www🎈


## 目前正处于早期开发之中。

如果觉得对您有帮助，欢迎投喂奶茶qwq
![miaow](https://ed1toa.bn.files.1drv.com/y4mvxzPxCdZAMpxhZAi6ghIkRKhj3OYl6BR37714KsBvir85uzfCYDPkzjkBIjiRiqCJkIC9dw5myG2Oqbqc9UIgkrOTt3mYAcsGhrO2nBgkcA3IyPlkiKr_DuFBYaea-tqdBhvdj8l0CzVksRJNQRLwaWus-NUHHWZPXYBtZIxtUdoGHAdjY3Y6uEZg8c521hl01S3ZbObnH1FWXg288Qyjg?width=356&height=356&cropmode=none)