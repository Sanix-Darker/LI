# LINO

A Fork from Li but only for Arduino.

## Requirements

- Python (3.x) is all you need.
- PyInstaller (pip3 install pyinstaller) |Optional, if you want to generate the executable of li
- Any lib required.

## Features

 - Easily extendable with modules.
 - First class functions.
 - String, list, number, dictionary, null, and function types

## PreInstallation

- For Lino to run on your Arduino board, you need to install Arduino IDE (it will come with drivers and many other stuff)
- Copy `./StandardFIrmata.ino`, check and upload it on your Arduino Board !
- We all done, for the Hardware part, now we need to finish the software part with Lino interpreter.

## Build the portable version of Lino

Using Pyinstaller, hit this command to install pyinstaller :

```
pip3 install pyinstaller
```

Then to build the li portable version :

```
cd to/the/project
pyinstaller ./lino.py --onefile --name lino
```

pyinstaller will generate the executable for Li in `./dist`, so that you will now run :
```
cd dist
./lino ./blink.lo
```

## With Source-code

Or using the sour-code by running li's script with :
`python lino.py ./blink.lo`


## Examples and tests

Example of LI code :
INPUT:
```
allumes_et_eteins:fonc(pin){
    affiche_xa(">> Haha, LED ON")
    allumes(pin) attends(1)

    affiche_xa("<< Oups, LED OFF")
    eteins(pin) attends(1)
}

main:fonc(){
    port_arduino("/dev/ttyACM0")
    tantque =(1 1) {
        allumes_et_eteins(13)
    }
}
```

OUTPUT:
```
Lino 0.1 Build using Li 0.1
Hit `lino script.lo`, for more information contact @sanixdarker.
--
>> Haha, LED ON
<< Oups, LED OFF
>> Haha, LED ON
<< Oups, LED OFF
>> Haha, LED ON
<< Oups, LED OFF
>> Haha, LED ON
<< Oups, LED OFF
...
```
With your LED Blinking...

## Syntax

 The Documentation + Synthax is in progress...

## Author

- Sanix-darker