# MAC OS mosquito 安装

## 安装

安装mosquitto

```shell
brew install mosquitto
```

安装paho-mqtt库

```shell
pip install paho-mqtt --user
```

在MAC下安装会遇到权限问题，在后面加`--user`



## 配置启动

```shell
ln -sfv /usr/local/opt/mosquitto/*.plist ~/Library/LaunchAgents
```

或者：

```shell
brew services start mosquitto
```

如果改变了配置需要重新启动：

```shell
brew services restart mosquitto
```

可以查看启动了哪些服务：

```shell
brew services list
```

如果卸载了mosquitto，清理配置：

```shell
brew services cleanup
```

可以查看下`/usr/local/opt/mosquitto/homebrew.mxcl.mosquitto.plist`，内容如下：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>homebrew.mxcl.mosquitto</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/opt/mosquitto/sbin/mosquitto</string>
    <string>-c</string>
    <string>/usr/local/etc/mosquitto/mosquitto.conf</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <false/>
  <key>WorkingDirectory</key>
  <string>/usr/local/var/mosquitto</string>
</dict>
</plist>
```

可以看到配置文件的位置。



## 配置mosquitto

修改`/usr/local/etc/mosquitto/mosquitto.conf`：

```shell
allow_anonymous false
password_file /usr/local/etc/mosquitto/passwd
```

生成密码：

```shell
mosquitto_passwd -c /usr/local/etc/mosquitto/passwd rpi2-zerodayhong
# 输入密码
```


## 测试mosquitto

SUB

```shell
mosquitto_sub -u rpi2-zerodayhong -P rpi2rpi2 -t rpi2-zerodayhong/led
```

PUB

```shell
mosquitto_pub -u rpi2-zerodayhong -P rpi2rpi2 -t rpi2-zerodayhong/led -m "Hello World"
```


## RPI代码中使用

```python
import paho.mqtt.client as mqtt
client = mqtt.Client()
client.username_pw_set('rpi2-zerodayhong', 'rpi2rpi2')
client.connect("localhost")

# 关闭LED
client.publish('rpi2-zerodayhong/led', 0)

# 打开LED
client.publish('rpi2-zerodayhong/led', 1)
```

