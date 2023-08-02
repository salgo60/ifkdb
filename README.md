# [ifkdb]()
Koppla ihop Wikipedia med [ifkdb](https://ifkdb.se/) en databas med IFK Göteborgs spelare... Wikidata [Property:P11905](https://www.wikidata.org/wiki/Property:P11905)

* [X] ladda upp koppling i Wikidata för [dom som har som har artikel i Wikipedia](https://w.wiki/77gS)
* [X] lägga in mall **ifkdb** i sv:Wikipedia artikeln - [lista saknar mall](https://petscan.wmflabs.org/?psid=25469508)
* [X] se om vi kan koppla en:Wikipedia se [#2](https://github.com/salgo60/ifkdb/issues/2) - [artiklar utan mallen](https://petscan.wmflabs.org/?psid=25476325)
* [X] |[spelare kopplade i Wikidata till ifkdb och vilka språk dom finns på](https://w.wiki/7A$9)
    * [X] men saknar atrtikel på [svenska Wikipedia](https://w.wiki/7A$M) / [engelska Wikipedia](https://w.wiki/7A$L)
* [X] skapa utkast Entity schema för svensk fotbollsspelare [#11](https://github.com/salgo60/ifkdb/issues/11)
* [X] söka ut IFKspelare i WIkidata och se om det finns bilder hos Svenskt Porträttarkiv [#12](https://github.com/salgo60/ifkdb/issues/12)
----
### Lesson learned
Wikipedia/Wikidata har enormt skitigt "fotbolls data" - "klippa och klistra" skalar inte --> blir bara mer och mer ruttet för varje dag...
* skulle kunna bli magiskt bra om vi byggde upp ett datadrivet ekosystem som uppdaterar varandra och kollar konsistens...
   * gissar att lite saker måste styras upp men ingen rocket science 
----
* Mall [ifkdb](ss)
   * Spårbar kategori [Kategori:Ifkdb.se](https://sv.wikipedia.org/wiki/Kategori:Ifkdb.se)
* WD prop [Property:P11905](https://www.wikidata.org/wiki/Property:P11905)
   * [Lista kopplade](https://w.wiki/77gS) = 349 stycken
     * [Lista WD kopplade men saknar mall ifkdb i Wikipedia artikeln](https://petscan.wmflabs.org/?psid=25469508)

### Antal artiklar om IFK spelare i WIkipedia per språk
* [lista](https://w.wiki/77ip) --> engelska är större en svenska... kanske en engelsk ifkdb?

<img width="1210" alt="image" src="https://github.com/salgo60/ifkdb/assets/14206509/01a495d5-734b-42c1-b6f5-02b5c48b50ab">

### Antal sidvisningar 
#### hos artiklar som har mall ifkdb på svenska wikipedia
* [Sidvisningar i år](https://pageviews.wmcloud.org/massviews/?platform=all-access&agent=user&source=category&range=this-year&subjectpage=0&subcategories=0&sort=views&direction=1&view=list&target=https://sv.wikipedia.org/wiki/Kategori:Ifkdb.se) > 541 865

<img width="1210" alt="image" src="https://github.com/salgo60/ifkdb/assets/14206509/80643a04-334f-44bf-9b0a-f97b51192d62">

#### engelska Wikipedia 
* Kategori [IFK Göteborg players](https://en.wikipedia.org/wiki/Category:IFK_G%C3%B6teborg_players)
* [Sidvisningar i år](https://pageviews.wmcloud.org/massviews/?platform=all-access&agent=user&source=category&range=this-year&subjectpage=0&subcategories=0&sort=views&direction=1&view=list&target=https://en.wikipedia.org/wiki/Category:IFK_G%25C3%25B6teborg_players) > 1 miljon visningar

<img width="1210" alt="image" src="https://github.com/salgo60/ifkdb/assets/14206509/bbb3645a-cca1-443d-b0e8-acde903c3242">

### Open Refine - ladda in kopplingen
Kör in dom som har länk WIkipedia afrtikel = 285 stycken 
<img width="1210" alt="image" src="https://github.com/salgo60/ifkdb/assets/14206509/09a885c8-efcd-4fc4-8bad-2648d627a03c">
* verkar inte ha Wikipedia artikel = 51 stycken
* de som laddats [SPARQL](https://w.wiki/77gS)
