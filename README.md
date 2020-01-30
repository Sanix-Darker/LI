# LI

In French "langage interprété" Or `IL` in english for Interpreted Language, is a simple programming language Based on some Python Classes.

## Requirements

- Python (3.x) is all you need
- Any lib required


## Example of li code

Example of LI code :
INPUT:
```
main:def() {
    affiche_xa("Hello World !!!")
    affiche( "Taille de [1,2,3] =" taille( [1,2,3] ) )
}
```

OUTPUT:
```
Li 0.1 Build using Python 3.7.3
Hit `run li your_script.l`, for more information contact @sanixdarker.
--
Hello World !!!
Taille de [1,2,3]  : 3
```

## Tests

You can performs some tests now :

Hit theese commands:

```shell
# The simple hello world script
python li.py ./hello.l

# The count-down from 100 to 0
python li.py ./tests/count.l

# Another tests
python li.py ./tests/test.l
```

## Author

- Sanix-darker