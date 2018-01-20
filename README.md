# Micropython Turnstile

This is my dummy repo for playing with nodeMCU board trying to make a working
turnstile.

## NodeMCU & Micropython

- [NodeMCU Official Documentation](https://nodemcu.readthedocs.io/en/master/)
- [Micropython ESP8266 Download](http://micropython.org/download#esp8266)
- [How to flash NoceMCU with Micropython (Spanish Version)](http://leo.bitson.com.ar/blog/micropython-en-la-nodemcu/)

## Connect to your board not using sudo

It's a big a chance that your USB device can only be accessed by `root`. Check
your device permissions with `ls`:

```bash
ls -lah /dev/ttyUSB0
crw-rw----. 1 root dialout 188, 0 ene 20 19:41 /dev/ttyUSB0
```
Here you can see that the device can be read & write by `root` and by the
`dialout` group. So, here is the solution. Add your user to the `dialout`
group.

```bash
usermod -aG dialout $USER
```
__Voilà!__ In your next login your user will have access to the USB device
without typing `sudo`



