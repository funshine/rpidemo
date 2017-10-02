# 树莓派驱动OLED屏幕

## 连接引脚

![pin](pic/oledpin.png)



连接如下表（来自luma.oled的例子）:


| OLED Pin | Name | Remarks      | RPi Pin | RPi Function   |
| -------- | ---- | ------------ | ------- | -------------- |
| 1        | VCC  | +3.3V Power  | P01-17  | 3V3            |
| 2        | GND  | Ground       | P01-20  | GND            |
| 3        | D0   | Clock        | P01-23  | GPIO 11 (SCLK) |
| 4        | D1   | MOSI         | P01-19  | GPIO 10 (MOSI) |
| 5        | RST  | Reset        | P01-22  | GPIO 25        |
| 6        | DC   | Data/Command | P01-18  | GPIO 24        |
| 7        | CS   | Chip Select  | P01-24  | GPIO 8 (CE0)   |

主要的不同是RST和DC引脚的接法。




## luma.oled注意事项

### 黑屏

运行测试程序时，程序正常退出，屏幕没有任何显示。

原因：luma.oled驱动默认在退出时将屏幕清除了。

解决方案：

```python
def do_nothing(obj):
    pass

device = sh1106(serial)
device.cleanup = do_nothing
```



设置cleanup为空函数。

