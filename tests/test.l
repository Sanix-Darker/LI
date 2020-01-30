fib:def() {
   a:0 b:1
   def() {
      b:+(a a:b)
      a
   }
}

fibPrinter:def(i f) {
   if >(i 0) {
         affiche_xa(f())
         fibPrinter(-(i 1) f)
   }
}

main:def() {
   f:fib() i:20
   affiche_xa("Displaying" i "Fibonacci numbers:")
   fibPrinter(i f)
   0
}