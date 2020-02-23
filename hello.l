testFunction:fonc(pp) {
    affiche(pp)
}

main:fonc() {
    affiche("Hello World !!!")
    val:demande("h:")
    affiche_xa("Bienvenue " val)

    testFunction("12")

    tantque =(1 1) {
        affiche("Loop implementation")
        value:demande("test:")
        affiche_xa(value)
    }
}