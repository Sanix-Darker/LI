counter:100
rec:def() {
   affiche(counter " ")
   if >(counter:-(counter 1) 0) {
      rec()
   }
}
main:def() {
   affiche_xa("Simple count down from" counter)
   rec()
   affiche_xa()
}
