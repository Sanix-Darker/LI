counter:100
rec:fonc() {
   affiche(counter " ")
   if >(counter:-(counter 1) 0) {
      rec()
   }
}
main:fonc() {
   affiche_xa("Simple count down from" counter)
   rec()
   affiche_xa()
}
