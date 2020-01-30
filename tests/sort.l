
qsort:fonc(l c) {
   if >(len(l) 1) {
      p:l(0)
      lo:qsort(filter(def(x) { c(p x) } l) c)
      hi:qsort(filter(def(x) { c(x p) } l) c)
      eq:filter(def(x) { =(p x) } l)
      +(lo eq hi)
   } else {
      l
   }
}

main:fonc() {
    l:[2 23 6 1 26 923 5 0 92]
    affiche_xa("Unsorted:          " l)
    affiche_xa("Sorted high to low:" qsort(l <))
    affiche_xa("Sorted low to high:" qsort(l >))
}
