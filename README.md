# Ecommerce-Arbitrage

## DISCLAIMER

Questo programma è stato pensato e sviluppato soltanto per scopi educativi e di apprendimento.<br>
Se alcune parti del programma dovessero danneggiare in qualche modo i diritti dei proprietari dei siti web utilizzati al suo interno, i diretti interessati possono contattare l'assistenza di GitHub 
che provvederà a notificarmi il problema: se necessario rimuoverò o modificherò tali parti ben volentieri.

------------------------

This program has been developed just for educational purposes.<br>
If some parts of the program should in some way infringe the rights of the owners of the web sites used in the app, they can contact the GitHub
assistance that will then notify to me the issue: if necessary, I will gladly remove or change the interested pieces of code.

------------------------
## A cosa serve questo programma

Ho scritto questo codice, che necessita di ulteriore lavoro per essere rifinito e migliorato, con l'idea di trovare un metodo relativamente semplice per comparare i prezzi da un ecommerce ad un altro, scegliere i prodotti più convenienti e automatizzare il processo di creazione dell'inserzione per pubblicare tali prodotti sul secondo ecommerce.

Per schematizzare, gli step del programma principali sono:

- Individuazione, nel primo ecommerce, di prodotti adatti alla rivendita sul secondo ecommerce in base a determinati filtri (es. prezzo);
- Questa individuazione avviene comparando anche i prodotti trovati con le eventuali inserzioni già presenti sul secondo ecommerce;
- Il programma durante questo processo genera dei file .csv con tutti i dati del prodotto necessari (estratti dal primo ecommerce) che verranno poi utilizzati per creare le inserzioni sulla seconda piattaforma.
- Infine, esso accede automaticamente al secondo ecommerce dove compila le inserzioni da pubblicare utilizzando i dati contenuti nei file .csv insieme alle immagini del prodotto scaricate precedentemente.

Questo processo in genere nel commercio viene denominato "Arbitrage", concetto che ho sfruttato come stimolo per scrivere questo programma a scopo di apprendimento, per imparare e migliorare la mia conoscenza di Python e della programmazione in generale.

----------------------
## The purpose of the program

This app was created with the idea to find a relatively simple method to compare prices between two different ecommerce web sites, to find the more convenient products and to automate the process of listing creation to publish those products in the second ecommerce.

To recap, the main steps involved are:

- Identification, on the first ecommerce, of the products suitable to be sold in the second ecommerce, based on specific filters (price, for ex.);
- This identification is made by comparing even the products found with the potential available listings already published on the second ecommerce web site.
- The app during this process will generates .csv files containing all the needed product's data (extracted from the first ecommerce) that will then used to create the listings on the second platform.
- Finally, it  automatically accesses the second ecommerce where it compiles the listings to be published using the data contained inside the .csv files together with the pics of the product previously downloaded.

This process is normally called "Arbitrage", a concept that I've used as an incentive to write this app for a personal educational purpose, to learn and improve my knowledge of Python and coding in general.
