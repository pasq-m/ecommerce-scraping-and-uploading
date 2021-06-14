#Prima parte del bot per automatizzare la pubblicazione di inserzioni su ebay.
#Questo script cerca su Amazon (andando anche su ebay a fare delle verifiche) oggetti idonei, in base a determinati filtri impostati (tra cui il prezzo), e li pubblica su un account ebay.
#Questa prima parte utilizza il modulo BeautifulSoup

#-FEATURES-
#-Analizza i risultati di ricerca su Amazon in base ai seguenti filtri:

#-Disponibilita': lo script controlla se il prodotto e' presente, se si e se ci sono almeno 3 pezzi rimasti viene salvato il suo link con relativo numero di disponibilita' sulla seconda colonna nel file .csv.
#-Prezzo: tramite alcuni calcoli lo script analizza il prezzo dell'oggetto su Amazon e lo compara con i prezzi degli stessi oggetti su Ebay (se sono presenti) pubblicati dai competitors e decide se ci puo' essere un
# eventuale guadagno; in base a quello viene salvato o meno il link.
#-Spese di spedizione: nel calcolo del prezzo vengono tenute di conto anche le spese di spedizione utilizzate dai competitors su Ebay per ogni oggetto.
#-Su Ebay viene controllato che non ci siano piu' di 8 inserzioni per lo stesso oggetto gia' pubblicate dai competitors.


#Il link di un oggetto (in caso con eventuale numero di pezzi rimasti) viene salvato sul file .csv solo quando l'elemento analizzato risulta positivo per ogni filtro applicato.

from bs4 import BeautifulSoup
from itertools import izip
from shutil import copyfile

import numpy as np
import os
import re
import csv
import urllib2
import requests
import string
import codecs



text = None

csvfile = "test.csv"

global_dict = {}
good_dict = {}
new_list = []


#IMPORTANTE: NON UTILIZZARE INDIRIZZI CON "HTTPS" MA BENSI' SOLTANTO "HTTP" POICHE' CREA PROBLEMATICHE O CON IL BEAUTIFULSOUP O CON IL REQUESTS PERCHE' EVIDENTEMENTE, UNO DEI DUE (O ENTRAMBI?) NON RIESCE A SCARICARNE I DATI.
#IMPORTANTE: CON LINK NUOVO DOBBIAMO CAMBIARLO ANCHE SOTTO ALLA VARIABILE "NEXT PAGE URL"

url = 'http://www.amazon.it/s/ref=sr_pg_1?rh=n%3A635016031%2Cp_76%3A490210031%2Cp_6%3AA11IL2PNWYJU7H&page=1&bbn=635016031&ie=UTF8&qid=1467368199'


#Item counter

counter = 3840                                          #Questo counter puo' essere modificato per far partire l'analisi degli oggetti da un determinato numero nei risultati di Amazon, a patto che sia complementare con la relativa
                                                        #pagina in cui tale oggetto specificato si trova. Es.: l'oggetto numero 240 si trovera' all'inizio della pagina 10 dei risultati su amazon, quindi nel counter sotto
                                                        #(page_counter) dovremmo mettere come valore "10".
    
#Counter for changing page
counter2 = 0

#Page counter											 #IMPORTANTE - per batch da 25 pagine l'uno ricordarsi che il secondo batch parte non dalla 25esima pagina ma dalla 26esima: infatti l'oggetto numero "600" e' il primo della
                                                         #26esima. E dopo andremmo alla 51esima (partendo con counter = 1200) e non alla 50esima.


page_counter = 161                                       #IMPORTANTE:se si parte dalla prima pagina NON mettere "1" ma bensi' "0" , per il resto leggere commento sopra a "counter".


#Lo script parte da 0 (primo oggetto su Amazon in alto a sinistra) fino al 23 (ultimo in basso a destra della prima pagina) e cambia pagina per continuare l'analisi degli altri oggetti (24,25,26,etc) fino all'ultimo oggetto
#della seconda pagina (numero 47) e passa alla pagina successiva - aggiungendo il numero dell'ultimo oggetto nella pagina al codice e' possibile creare degli "spartiacque"
#per far cambiare pagina allo script e far continuare l'analisi degli oggetti in modo sequenziale.

counter_key_value = 0                                               #Counter per modificare il nome della chiave per aggiungere il valore prezzo al 20% ad ogni rispettivo oggetto al file finale (se non cambiassi nome sovrascriverebbe ogni volta il solito valore).


while counter < 4441:                                               #numero di oggetti per x pagine

    try:    
    
        if page_counter > 0:

            if page_counter == 1:                                       #Dato che il primo url (quello in cima allo script) e l'url che si creerebbe utilizzando il "page_counter = 1" (ovvero dopo il primo giro di while)
                                                                        #porterebbero alla stessa pagina (analizzeremmo due volte la prima pagina), dobbiamo usare uno stratagemma per saltare il valore 1 del page_counter
                page_counter = 2                                        #e passare direttamente al valore 2 - infatti vediamo che quando page_counter e' = 1 lo trasformiamo in = a 2 e risolviamo.

				#Questo next_page_url sotto va modificato con il link modificato che Amazon da quando si va in qualsiasi pagina della ricerca che non sia la prima (dalla 2 in poi).									
				#Anche nel next_page_url sotto (dove c'e' la nota) va posizionata la stessa struttura link delle pagine successive alla prima di Amazon, tenendo conto pero' che quello verra' sempre utilizzato per primo
				#tutte le volte che si modificheranno a mano i counter per andare avanti in profondita' nelle ricerche a scaglioni di pagine su Amazon (es. dopo le prime X pagine che partono dalla prima, dobbiamo modificare
				#i counter per analizzare altre tot pagine, e lo script andra' direttamente ad analizzare questa struttura link.
				
                next_page_url = 'http://www.amazon.it/s/ref=sr_pg_' + str(page_counter) + '?rh=n%3A635016031%2Cp_76%3A490210031%2Cp_6%3AA11IL2PNWYJU7H&page=' + str(page_counter) + '&bbn=635016031&ie=UTF8&qid=1467368199'

                url = next_page_url

                print ('seconda pagina costruct:', url)

                #counter = 0

            #NOTA: leggere commento precedente
				
            next_page_url = 'http://www.amazon.it/s/ref=sr_pg_' + str(page_counter) + '?rh=n%3A635016031%2Cp_76%3A490210031%2Cp_6%3AA11IL2PNWYJU7H&page=' + str(page_counter) + '&bbn=635016031&ie=UTF8&qid=1467368199'           

            url = next_page_url

            print ('seconda pagina costruct:', url)

            #counter = 0    

        base_url = "http://www.amazon.it"
        page_array = []

        print ('prova url fuori if:', url)

        f = csv.writer(open("good_urls_for_ebay.csv", "w"))

    
    #A questo punto il Soup ci fornisce i dati di una pagina filtrata con due filtri attivi (Prime e venduti da Amazon)


    #IN THIS SECTION THE BOT WOULD FIND THE LINKS OF THE AMAZON'S ITEMS DISPLAYED AS RESULTS	

        html = requests.get(url)
        soup = BeautifulSoup(html.content, "html.parser")

        #result_var = '\'result_' + str(counter) + '\''						#"result_var" sta ad identificare l'oggetto da analizzare nella pagina dei risultati di Amazon come ad es. "result_234" e' il 234esimo oggetto in ricerca.
        result_var = 'result_' + str(counter)								#FONDAMENTALE: il "result_x" viene riconosciuto solo se NON aggiungiamo gli apici "'\''" (come es. sopra) nella definizione della variabile
        print result_var
        
        tag = 'li'
        first_attr = 'id'
        second_attr = result_var											#Il "first_result" sara' l'attributo-valore da cercare con il soup che cambia ogni volta a seconda del numero dell'oggetto e che viene utilizzato per
        tag_attrs = {first_attr: second_attr}								#analizzare il link e il prezzo del prodotto nella pagina ricerca.
        first_result = soup.find(tag, **tag_attrs)							#il "**tag_attrs" si basa su un comando di solito utilizzato nelle funzioni, ovvero "**kwargs", che serve ad estrarre tutti gli oggetti definiti come argomenti della funzione non presenti nella definizione del metodo della funzione
																			#in questo caso, "**tag_attrs" utilizza gli oggetti forniti, sotto forma di attriburo-valore, nella variabile "tag_attrs"
        
   
 #PARTE SULLA RICERCA DELLA DISPONIBILITA' DEL PRODOTTO
        
        tag_href_product = first_result	
        #print "Trova l'oggetto?", tag_href_product
        if not tag_href_product:                                            #Se su Amazon il browser salta un oggetto (es.: "result_105","result_106","result_108" - il 107 non c'e') con questo if
            print "Oggetto assente - passo oltre"                           #dico allo script di tornare all'inizio se la variabile "tag_href_product" risulta vuota (valore "None").    
            
            counter = counter +1                                                               

            counter2 = counter2 +1

            #Il check sottostante controlla che il counter2 non abbia valore 24: se questo accade fa avanzare la pagina da analizzare di +1 e resetta il counter2 a 0 di modo che possa iniziare il conteggio da capo per la pagina nuova.
            if counter2 == 24:
                page_counter = page_counter +1

                counter2 = 0
                continue

            continue
        
        try:
            #Proviamo a controllare che l'oggetto in esame non abbia l'opzione "Visualizza di piu'": se si, lo script va avanti e controlla se l'oggetto e' disponibile, altrimenti, va all'eccezione e valuta altre ipotesi.

            amaz_more_choices = tag_href_product.find('div', {'class' : 'a-section a-spacing-none a-text-center'})  #per quanto riguarda la ricerca del tag "span" (nella prima ipotesi deve arrivare all'ottavo "span" per
            amaz_more_choices = amaz_more_choices.find('span', {'class' : 'a-color-secondary'})
            print amaz_more_choices
            amaz_more_choices = amaz_more_choices.get_text()
            print "Try beccato", amaz_more_choices
            if 'Visualizza' in amaz_more_choices.split():
                amaz_no_avail = tag_href_product.find_all('span')[6]                                    #Quando gli oggetti hanno l'etichetta "visualizza di piu'" dobbiamo selezionare il tag span al SESTO posto (in posizione 7
                amaz_no_avail = amaz_no_avail.get_text()                                                #all'interno del documento html - parte da 0 il conteggio quindi viene "6").
                amaz_no_avail = amaz_no_avail.encode('utf-8')
                print "Visualizza piu' elementi", amaz_no_avail

                if "Solo" in amaz_no_avail:
                    amaz_no_avail = str(amaz_no_avail)                                                  #Dobbiamo trasformare la variabile in stringa per poterla utilizzare sotto col "re.sub"    
                    amaz_no_avail_only_numb = re.sub("[^0-9]", "", amaz_no_avail)                       #Col regex mi dava problemi e ho tolto tutti i caretteri tranne le lettere usando il "re.sub"
                    amaz_no_avail_only_numb = int(amaz_no_avail_only_numb)
                    print "Quantita' oggetti rimasti:", amaz_no_avail_only_numb

                    if amaz_no_avail_only_numb < 3:                                                     #Se gli oggetti rimasti sono meno di 3 torniamo all'inizio del loop e non registriamo il prodotto.
                        
                        print "Pochi oggetti rimasti"

                        amaz_no_avail_only_numb = None

                        counter = counter +1

                        counter2 = counter2 +1

                        #Il check sottostante controlla che il counter2 non abbia valore 24: se questo accade fa avanzare la pagina da analizzare di +1 e resetta il counter2 a 0 di modo che possa iniziare il conteggio da capo per la pagina nuova.
                        if counter2 == 24:

                            page_counter = page_counter +1

                            counter2 = 0
                            continue

                        continue
                    
                if "disponibile" in amaz_no_avail.split():                                              #Lo ".split()" serve a far trovare tutta la parola completa "disponibile" e non solo "dispo" ad es..

                    print "Non disponibile 1"

                    amaz_no_avail_only_numb = None                                                      #Resetto la variabile contenente il numero di oggetti ancora disponibili (se presente) per evitare che resti in memoria per
                                                                                                        #il prossimo loop e vada ad incasinare la coppia (quando presente) "link : numero ogg. disponibili" che viene scritta nella
                    counter = counter +1                                                                # lista finale.

                    counter2 = counter2 +1

                    #Il check sottostante controlla che il counter2 non abbia valore 24: se questo accade fa avanzare la pagina da analizzare di +1 e resetta il counter2 a 0 di modo che possa iniziare il conteggio da capo per la pagina nuova.
                    if counter2 == 24:
                        page_counter = page_counter +1

                        counter2 = 0
                        continue

                    continue

        except AttributeError:
            
            #L'oggetto non ha la dicitura "Visualizza di piu'" e di conseguenza ha il tag che ci serve in posizione "5" anziche' "6"
            
            try:                                                                                    #Utilizziamo un altro "try" per mettere nella relativa eccezione sottostante una parte di codice atta a gestire differenti
                                                                                                    #(inferiori) numeri di span (es. span [4] - span [3] - etc).
                amaz_no_avail = tag_href_product.find_all('span')[5]                                #con ".find_all('span')[5]" cerchiamo come se fosse una lista, il sesto (parte da 0 quindi ha il numero "5" nello script) tag "span"
                print "Print lettura tag:", amaz_no_avail
                amaz_no_avail = amaz_no_avail.get_text()
                amaz_no_avail = amaz_no_avail.encode('utf-8')
                amaz_no_avail = str(amaz_no_avail)

                #Se non trova nessun testo al quinto posto significa che stiamo analizzando un'oggetto che ha il tag della disponibilita' su un'altra posizione (la 7) e di conseguenza utilizziamo quest'altro pezzo di codice.

                if not amaz_no_avail:                                                               #E' un modo "elegante" per verificare se una stringa sia vuota: se lo e' si esegue il codice sottostante che in questo caso                                                                                    
                                                                                                    #analizza il "TAG 8", ovvero quegli oggetti che hanno tag "span" in piu' (3 in piu' rispetto agli altri) e che quindi non
                                                                                                    #non sarebbero analizzati correttamente senza questo "if".
                    amaz_no_avail = tag_href_product.find_all('span')[7]
                    print "Here it comes TAG 7:", amaz_no_avail
                    amaz_no_avail = amaz_no_avail.get_text()
                    amaz_no_avail = amaz_no_avail.encode('utf-8')
                    amaz_no_avail = str(amaz_no_avail)

                    if "disponibile" in amaz_no_avail.split() or "Generalmente" in amaz_no_avail.split():   #Se trova la parola "disponibile" nel testo estratto (proverrebbe da "non disponibile") significa che il prodotto non e'
																											#presente e quindi si torna all'inizio del loop while saltando tutto.        
                        print "Non disponibile TAG 7"                                               		#La stessa cosa vale per il termine "Generalmente" poiche' riferito ad un prodotto non presente nei magazzini Amazon.

                        amaz_no_avail_only_numb = None

                        counter = counter +1

                        counter2 = counter2 +1

                        #Il check sottostante controlla che il counter2 non abbia valore 24: se questo accade fa avanzare la pagina da analizzare di +1 e resetta il counter2 a 0 di modo che possa iniziare il conteggio da capo per la pagina nuova.
                        if counter2 == 24:

                            page_counter = page_counter +1

                            counter2 = 0
                            continue

                        continue


                    if "Solo" in amaz_no_avail:

                        amaz_no_avail = str(amaz_no_avail)                                                  #Dobbiamo trasformare la variabile in stringa per poterla utilizzare sotto col "re.sub"    
                        amaz_no_avail_only_numb = re.sub("[^0-9]", "", amaz_no_avail)                       #Col regex mi dava problemi e ho tolto tutti i caretteri tranne le lettere usando il "re.sub"
                        amaz_no_avail_only_numb = int(amaz_no_avail_only_numb)
                        print "Solo - Sola TAG 7:", amaz_no_avail
                        print "Quantita' oggetti rimasti:", amaz_no_avail_only_numb

                        if amaz_no_avail_only_numb < 3:

                            print "Pochi oggetti rimasti"

                            amaz_no_avail_only_numb = None

                            counter = counter +1

                            counter2 = counter2 +1

                            #Il check sottostante controlla che il counter2 non abbia valore 24: se questo accade fa avanzare la pagina da analizzare di +1 e resetta il counter2 a 0 di modo che possa iniziare il conteggio da capo per la pagina nuova.
                            if counter2 == 24:

                                page_counter = page_counter +1

                                counter2 = 0
                                continue

                            continue


                        #Qua conserviamo la variabile relativa a quanti oggetti sono rimasti
                        #per scrivere poi il suo contenuto nel file .csv.

                elif "disponibile" in amaz_no_avail.split() or "Ricevilo" in amaz_no_avail.split() or "Prenotalo" in amaz_no_avail.split():          
                                                                                                            
                    print "Print da TAG 5:", amaz_no_avail
                                                                                                            
                    print "Non disponibile TAG 5"

                    amaz_no_avail_only_numb = None

                    counter = counter +1

                    counter2 = counter2 +1

                    #Il check sottostante controlla che il counter2 non abbia valore 24: se questo accade fa avanzare la pagina da analizzare di +1 e resetta il counter2 a 0 di modo che possa iniziare il conteggio da capo per la pagina nuova.
                    if counter2 == 24:

                        page_counter = page_counter +1

                        counter2 = 0
                        continue

                    continue                    

                elif "Solo" in amaz_no_avail.split():

                    print "Solo - Sola TAG 5:", amaz_no_avail
                    amaz_no_avail = str(amaz_no_avail)                                                  #Dobbiamo trasformare la variabile in stringa per poterla utilizzare sotto col "re.sub"    
                    amaz_no_avail_only_numb = re.sub("[^0-9]", "", amaz_no_avail)                       #Col regex mi dava problemi e ho tolto tutti i caretteri tranne le lettere usando il "re.sub"
                    amaz_no_avail_only_numb = int(amaz_no_avail_only_numb)
                    print "Quantita' oggetti rimasti:", amaz_no_avail_only_numb

                    if amaz_no_avail_only_numb < 3:

                        print "Pochi oggetti rimasti"

                        amaz_no_avail_only_numb = None

                        counter = counter +1

                        counter2 = counter2 +1

                        #Il check sottostante controlla che il counter2 non abbia valore 24: se questo accade fa avanzare la pagina da analizzare di +1 e resetta il counter2 a 0 di modo che possa iniziare il conteggio da capo per la pagina nuova.
                        if counter2 == 24:

                            page_counter = page_counter +1

                            counter2 = 0
                            continue

                        continue                                       
                                
            except IndexError:                                                                          #L'eccezione viene alzata quando nel rispettivo try viene trovato un numero di tag "span" inferiore a 6 (effettivi...ovvero [5])
                class FindPrimeInsideSpanTag(Exception): pass                                           #di conseguenza ci sarebbe un "IndexError" per out of range.
                try:
                    print "EXCEPT: INDEX OUT OF RANGE"                                                      
                    amaz_no_avail = tag_href_product.find_all('span')[2]
                    amaz_no_avail = amaz_no_avail.get_text()
                    amaz_no_avail = amaz_no_avail.encode('utf-8')
                    amaz_no_avail = str(amaz_no_avail)
                    if "Prime" in amaz_no_avail:
                        print "Oggetto senza info su disponibilita' - ma DISPONIBILE"
                    else:
                        print "OUT OF RANGE per altro motivo...cerchiamo su altro tag span il Prime"
                        raise FindPrimeInsideSpanTag()
                except FindPrimeInsideSpanTag:
                    amaz_no_avail = tag_href_product.find_all('span')[4]
                    amaz_no_avail = amaz_no_avail.get_text()
                    amaz_no_avail = amaz_no_avail.encode('utf-8')
                    amaz_no_avail = str(amaz_no_avail)
                    if "Prime" in amaz_no_avail:
                        print "Oggetto senza info su disponibilita' - ma DISPONIBILE"
                    else:
                        print "OUT OF RANGE per altro motivo..."
                
#FINE PARTE RICERCA DISPONIBILITA' PRODOTTI
                    
        
    #troviamo dentro "links_products" il punto dove e' contenuto il testo del prezzo del prodotto e lo inseriamo in una variabile che successivamente scriveremo/utilizzaremo per la comparazione su ebay

        amaz_price = tag_href_product.find('span', {'class' : 'a-size-base a-color-price s-price a-text-bold'})
        print ('amaz price:', amaz_price)
        amaz_price_for_if = amaz_price.get_text()    
        amaz_price_clean_for_if = amaz_price_for_if.replace(".", "").replace(",", ".").replace(" ", "").replace("\'", "").replace("EUR", "")
        print ('Amaz price filtrato:', amaz_price_clean_for_if)

    #troviamo il titolo del prodotto e lo inseriamo dentro alla variabile 'amaz_title_product'
    #Utilizziamo un "try" perche' in alcuni casi (non ho capito il perche') il valore dell'attributo contenente il titolo cambia (viene aggiunto "scx-truncate") creando errori e bloccando lo script; in questo modo possiamo dare   
    # due alternative allo script.    
        try:
        
            amaz_title_product = tag_href_product.find('h2', {'class' : 'a-size-base a-color-null s-inline scx-truncate s-access-title a-text-normal'})         #Questo e' il tag specifico del titolo ma a volte non viene trovato (causa ignota)
																																								#Anche qua e' contenuto il titolo e dovrebbe dare meno problemi (parent del tag sopra)
            print "Qua il titolo:", amaz_title_product            
            amaz_title_product = amaz_title_product.get_text()
            print 'Titolo amazon', amaz_title_product        

            if "&" in amaz_title_product.strip():
                amaz_title_product = amaz_title_product.replace("&", "")  
                
        except AttributeError:
            
            amaz_title_product = tag_href_product.find('h2', {'class' : 'a-size-base a-color-null s-inline s-access-title a-text-normal'})
            print "Qua il titolo except:", amaz_title_product
            amaz_title_product = amaz_title_product.get_text()
            print 'Titolo amazon', amaz_title_product

            if "&" in amaz_title_product.strip():
                amaz_title_product = amaz_title_product.replace("&", "")


    #WE CHECK IF THE AMAZON PRICE OF THE ITEM IS BETWEEN A CERTAIN RANGE (ABOVE 14 EURO AND BELOW 46) - IF NOT WE BREAK THE LOOP AND WE GET BACK TO THE START WITH THE NEXT ITEM

        amaz_price_if_definitive = float(amaz_price_clean_for_if)

        if amaz_price_if_definitive < 15 or amaz_price_if_definitive > 45:

            print 'Price out of range'        

            #Il blocco sottostante aggiunge +1 a due distinti counters: il primo (counter) e' il counter globale che va avanti finche' non raggiunge il limite posto sul while; il secondo counter (counter2) e' il counter che serve
            #a far cambiare pagina - ogni 24 oggetti analizzati manda avanti la pagina di +1 agendo sul contatore page_counter e resettandosi successivamente di modo che ogni 24 oggetti possa scorrere le pagine.
            amaz_no_avail_only_numb = None
            
            counter = counter +1

            counter2 = counter2 +1

            #Il check sottostante controlla che il counter2 non abbia valore 24: se questo accade fa avanzare la pagina da analizzare di +1 e resetta il counter2 a 0 di modo che possa iniziare il conteggio da capo per la pagina nuova.
            if counter2 == 24:

                page_counter = page_counter +1

                counter2 = 0

            continue  


    #WE ARE GOING TO EBAY WITH OUR TWO VARS (LINK AND PRICE) TO START THE COMPARISON PROCESS    

        eby_home = requests.get('http://www.ebay.it/')
        soup = BeautifulSoup(eby_home.content, "html.parser")

    #Costruiamo il link di ricerca su ebay aggiungendo la variabile con il nome creata precendentemente (estratta da amazon) ad un url preimpostato sempre uguale per la ricerca su ebay

        eby_base_search_url = 'http://www.ebay.it/sch/i.html?_from=R40&_sacat=0&_nkw='

        eby_base_search_url_part_2 = '&rt=nc&_dmd=2'

        link_eby_search = eby_base_search_url + amaz_title_product + eby_base_search_url_part_2
        
        print 'Ebay link', link_eby_search
    #Ridefiniamo la pagina da analizzare per BeautifulSoup

        eby_searched_page_product = requests.get(link_eby_search)
        soup = BeautifulSoup(eby_searched_page_product.content, "html.parser")

    #WE WILL FIND THE NUMBER OF RESULTS TO KNOW IF WE CAN GO ON OR STOP THE PROCESS IF THEY ARE TOO MANY


        div = soup.find('div', {'class' : 'bclt'})					                                                #andiamo a cercare una classe principale sotto la quale si trova il tag che cerchiamo
        
        count_span = div.find('span' , {'class' : 'listingscnt'})			                                        #qua specifichiamo ancora piu' in dettaglio quale testo vogliamo selezionare (il numero delle inserzioni su ebay)
    
        count_text = count_span.get_text()
        print ('testo inserzioni:', count_text)

        count_clear = count_text.replace(" ", "").replace("inserzioni", "").replace("inserzione", "").replace(",", "")	#Qua con il regex tolgo le lettere
        print ('Num inserzioni:', count_clear)

        count_clear = int(count_clear)																				#Rendiamo il numero di inserzioni un tipo numerico per poterlo soppesare aritmeticamente piu' giu' nel calcolo numero di inserzioni differente da 0

        if count_clear == 0 or count_clear > 8 :                                                                    #Se ci sono 0 inserzioni o piu' di 8 lo script torna all'inizio saltando l'oggetto
            print '0 inserzioni, passo'
            
            amaz_no_avail_only_numb = None
                
            counter = counter +1

            counter2 = counter2 +1

            if counter2 == 24:

                page_counter = page_counter +1

                counter2 = 0
            
            continue																					#Se il numero degli oggetti su Ebay e' maggiore di 8 lo script deve tornare all'inizio e passare all'oggetto successivo su Amazon
        else:
            
    #HERE WE LOOK FOR THE EBAY'S PRICE OF THE ITEMS
            
            eby_csv = open("eby_prices.csv", "w")						#IMPORTANTE: aprire l'open da solo e con un altra variabile aprire l'oggetto csv.writer sotto cosi' da poter chiudere la variabile "open" in fondo con "eby_csv.close()
            eby_writer = csv.writer(eby_csv)
    
            searching_prices = soup.find('ul' , {'id' : 'GalleryViewInner'})							#trova tutto quello SOLO dentro al primo 'GalleryViewInner'

            try:                                                                                        #TRY che serve ad alzare un'eccezione se invece di un prezzo normale nell'HTML troviamo un range di prezzi.
            
                for products_prices in searching_prices.find_all('span', {'class' : 'bold'}):
																										#Metto il risultato della lista (ResultSet object) derivata da 'find_all' in una variabile     
                    only_numbers = products_prices.find(text=re.compile('\d'))                          #Qua con il regex tolgo le lettere
                    only_numbers_w_out_spaces = only_numbers.replace(",", ".").replace(" ", "")         #e qua rimuovo gli spazi e trasformo le virgole in punti per poter sotto convertire tutto in "int"
                    print only_numbers_w_out_spaces
                    eby_writer.writerow([only_numbers_w_out_spaces])                                    #Se non e' nell'indent del for sopra (quello dei prezzi) nella lista scrive solo l'ultimo prezzo - deve restare dentro per iterare comandata dal for, fuori dal for trova 1'elemento e si ferma
            
            except UnicodeEncodeError:
                print "PRICE RANGE DETECTED - SKIP ITEM AND START AGAIN"
                counter = counter +1

                counter2 = counter2 +1

                if counter2 == 24:

                    page_counter = page_counter +1

                    counter2 = 0

                #counter = counter +1 
                continue
            
            eby_csv.close() 																#<------ FONDAMENTALE: serve a chiudere l'oggetto "scrittura" prima di aprire l'oggetto sotto "lettura" (altrimenti apre un file vuoto)
            
    #HERE WE WORK TO GET THE SHIPPING FEES OF EVERY OBJECT

            eby_base_search_url = 'http://www.ebay.it/sch/i.html?_from=R40&_sacat=0&_nkw='

            eby_base_search_url_part_2 = '&rt=nc&_dmd=1'

            link_eby_search_list_view = eby_base_search_url + amaz_title_product + eby_base_search_url_part_2


            eby_searched_page_productx = requests.get(link_eby_search_list_view)
            soupx = BeautifulSoup(eby_searched_page_productx.content, "html.parser")
        

            eby_ship_csv = open("eby_shipping_prices.csv", "w")						#IMPORTANTE: aprire l'open da solo e con un'altra variabile aprire l'oggetto csv.writer sotto cosi' da poter chiudere la variabile "open" in fondo con "wby_csv.close()
            eby_ship_writer = csv.writer(eby_ship_csv)	


        #CHECK OUT IF THE INSERTIONS' NUMBER IS 0 - IF YES (TRUE) BREAK AND GET BACK TO THE START OF WHILE LOOP
        #IF, INSTEAD, IT'S NOT (FALSE) THE SCRIPT KEEP GOING ON AND WORKS ON THE LIST FOR THE SHIPPING PRICES

            if count_clear <= 0:
                print 'counter 0'
                
                amaz_no_avail_only_numb = None
                    
                counter = counter +1

                counter2 = counter2 +1

                if counter2 == 24:

                    page_counter = page_counter +1

                    counter2 = 0
					
                continue
            else:		

                start = soupx.find('ul' , {'id' : 'ListViewInner'})
                lis = []
    
                for li in start.find_all(('li'), recursive=False):											#QUESTO RISOLVE: "recursive = false" (di default True) dice al parser di analizzare solo i primi "children" dell'oggetto da cui parte l'analisi (in questo caso "('ul' , {'id' : 'ListViewInner'})") senza analizzare anche gli altri elementi collegati presenti nei livelli piu' profondi' di
                    if li.find('div' , {'class' : 'expHeader'}):											
																											#DUPLICA ALCUNI RISULTATI PERCHE' PROBABILMENTE PRIMA ANALIZZA IL <LI> PRINCIPALE CHE CONTIENE TUTTI GLI ALTRI TAG <LI> E DOPO UNO AD UNO RIANALIZZA I VARI <LI> - 1 ALL'INIZIO PIU' GLI ALTRI E VENGONO DUE DI OGNUNO
                        break																				#ANALIZZA IL PRIMO LIVELLO E POI IL SECONDO LIVELLO IN PROFONDITA' DEI TAG <LI> E QUINDI SCRIVE DUE VOLTE I RISULTATI
                    lis.append(li)
                for fee_tag in lis:
        
                    for shipping_prices in fee_tag.find_all('span', {'class' : 'ship'}):
                        shipping_prices_csv = shipping_prices.get_text()
            
                        var_without_spaces = shipping_prices_csv.replace("\n","").replace("Spedizione gratuita","0").replace(" ","").replace("spedizione","").replace("+EUR","").replace("\t","").replace(",",".")	#Rimuoviamo: spazi TAB, spazi bianchi, spazi a capolettera, cambiamo "Spedizione gratuita" con "0", la virgola con il punto per poter cambiare la lista in "float type", rimuoviamo "spedizione" e "+EUR" per ottenere in fine soltanto numeri
            
                        print ('Sped. filtrate:', var_without_spaces)
            
                        eby_ship_writer.writerow([var_without_spaces])

            eby_ship_csv.close() 																#<------ FONDAMENTALE: serve a chiudere l'oggetto "scrittura" prima di aprire l'oggetto sotto "lettura" (altrimenti apre un file vuoto)


    #HERE WE OPEN THE SHIPPING PRICES'S .CSV TO LET THE NUMBERS INSIDE COMPUTABLE

            ff_ship = open("eby_shipping_prices.csv", "rb")
            reader = csv.reader(ff_ship)
            make_list_from_csv_ship = list(reader)

            changed_type_num_ship = np.array(make_list_from_csv_ship).astype(np.float)                   #Usando la libreria numpy trasformiamo la lista in un tipo "numerico"


    #WE CALCULATE THE NUMBER OF SHIPPING PRICES ITEMS - GREATER THAN 0 - CONTAINED INSIDE THE "EBY_SHIPPING_PRICES.CSV"

            not_zero_list = []																			#Creiamo fuori dal loop for una lista vuota

            for i in changed_type_num_ship:																#Analizziamo i singoli valori uno ad uno rappresentati dalle spese di spedizione con un loop for - 

                if i > 0:																				#- se il valore che stiamo analizzando durante il loop e' superiore allo 0 (quindi si tratterebbe di normali valori di spedizione quando essa non e' gratuita)

                    not_zero_list.append(i)																# lo aggiungiamo alla lista "not_zero_list" creata sopra

                    print ('Not Zero List:', not_zero_list)

            not_zero_list_lenght = len(not_zero_list)													#FUORI dal loop for misuriamo il numero degli elementi presenti nella nuova lista

            print ('ZERO Lenght:', not_zero_list_lenght)

            if not_zero_list_lenght > 2:																#Se tale numero e' superiore a 2 (quindi almeno 3) possiamo eliminare il valore minimo (differente da 0) e quello massimo dalla lista

                min_superior_to_zero = min(i for i in changed_type_num_ship if i > 0)					# "i" sta ad indicare un numero intero (credo...). Usando un "generatore di espressioni" possiamo selezionare come valore minimo solo un valore minimo DIVERSO da 0 (quindi dall'1 in poi)
                max_for_shipping = max(changed_type_num_ship)

                array_to_list_ship = changed_type_num_ship.tolist()										#Cambiamo tipo da Array a Lista
                remove_min_ship = array_to_list_ship.remove(min_superior_to_zero)                       #Rimuovo il valore minimo dalla lista (rimuovendo val min e val max posso avere una media meno influenzata dagli estremi - la media ponderata "weighted" non e' pensabile visto che i valori sarebbero probabilmente sempre differenti e quindi non conteggiabili per analizzarne il "peso")

                remove_max_ship = array_to_list_ship.remove(max_for_shipping)                           #Rimuovo il valore massimo dalla lista

                print ('Array list printed:', array_to_list_ship)

            else:

                array_to_list_ship = changed_type_num_ship.tolist()										#Cambiamo tipo da Array a Lista

            print ('Lista da csv:', make_list_from_csv_ship)      

            ff_ship.close() 																#<------ FONDAMENTALE: serve a chiudere l'oggetto "scrittura" prima di aprire l'oggetto sotto "lettura" (altrimenti apre un file vuoto)


    #HERE WE MAKE CHANGES ON LIST - EBAY'S PRICES


            ff = open("eby_prices.csv", "rb")
            reader = csv.reader(ff)
            make_list_from_csv = list(reader)

            if count_clear <= 2:

                list_length = len(make_list_from_csv)                                           #Lunghezza lista: opzionale per il momento, puo' tornare comodo

            if count_clear >= 3:

    #Questa parte sulla rimozione dei valori minimi e massimi prima di effettuare la media va fatta soltanto DOPO il calcolo prezzi + spese di spedizione

                list_max = max(make_list_from_csv)

                list_min = min(make_list_from_csv)

                remove_min = make_list_from_csv.remove(list_min)                                #Rimuovo il valore minimo dalla lista (rimuovendo val min e val max posso avere una media meno influenzata dagli estremi - la media ponderata "weighted" non e' pensabile visto che i valori sarebbero probabilmente sempre differenti e quindi non conteggiabili per analizzarne il "peso")

                remove_max = make_list_from_csv.remove(list_max)                                #Rimuovo il valore massimo dalla lista

                list_length = len(make_list_from_csv)                                           #Lunghezza lista: opzionale per il momento, puo' tornare comodo

            ff.close() 

    #HERE WE WORK ON THE ARITHMETIC MEAN


    #elementi.lista.prezzi + elementi.lista.shipping
    #_______________________________________________    =     ottengo una media che prende in considerazione la somma degli dei prezzi con le spese di sped. divisa per il numero dei prodotti (i prezzi) senza considerare il numero dei prezzi delle spese di sped. perche' sfaserebbe tutto il calcolo
    #     var.lunghezza.elementi.lista.prezzi


            joined_lists = make_list_from_csv + array_to_list_ship

            print joined_lists
            print list_length
            changed_type_num_prices = np.array(joined_lists).astype(np.float)                  	#Usando la libreria numpy trasformiamo la lista in un tipo "numerico"

            summed = sum(changed_type_num_prices)												#Sommo valori spese di sped. (tranne minimo sopra 0 e val. max) con valori prezzi oggetti ebay

            media_a_mano = summed / list_length													#Ottengo la media dividendo il numero degli oggetti trovati su ebay (num. inserzioni) con la somma delle due liste (prezzi piu' val. filtrati spese di sped.)

            print ('Media a mano:', media_a_mano)

            eby_pp_fees_subtracted = media_a_mano												#va definito "eby_pp_fees_subtracted" prima di poterlo utilizzare sotto

            eby_pp_fees_subtracted = eby_pp_fees_subtracted * (1 - 0.15)						#la percentuale va calcolata in questo modo - (1 - 0.15) e' uguale a 15%

            print eby_pp_fees_subtracted

            val_rifer = (1 + 0.20)															    #prova con 20% - dobbiamo guadagnarci almeno il 20% in piu' rispetto al prezzo medio su ebay al netto delle spese ebay-paypal che dobbiamo sostenere al momento della vendita

            if eby_pp_fees_subtracted >= amaz_price_if_definitive * val_rifer:					#qua calcoliamo se merita utilizzare l'oggetto in base al guadagno che ne otterremo: prendiamo il prezzo medio sottratto del 15% delle tariffe che pago e lo compariamo
        																					    #con il prezzo di Amazon aggiungendo un 20% in piu' che rappresenta il guadagno minimo. Se l'oggetto non raggiunge la soglia minima di guadagno richiesta non viene aggiunto, altrimenti si.

        #Mettiamo i valori "buoni" (il link dell'oggetto su amazon) dentro una lista, alla fine (fuori dal "while") prima di chiudere lo script scriviamo gli oggetti dentro la lista su un file .csv
                
            
                #Applico un range di percentuali specifiche a range differenti di prezzo:
                
                if amaz_price_if_definitive <= 17.50:
                    
                    price_plus_percent = amaz_price_if_definitive * (1 + 0.60)
            
                if amaz_price_if_definitive > 17.50 and amaz_price_if_definitive <= 20:
                    
                    price_plus_percent = amaz_price_if_definitive * (1 + 0.55)
            
                if amaz_price_if_definitive > 20 and amaz_price_if_definitive <= 22.50:
                    
                    price_plus_percent = amaz_price_if_definitive * (1 + 0.50)
            
                if amaz_price_if_definitive > 22.50 and amaz_price_if_definitive <= 25:
                    
                    price_plus_percent = amaz_price_if_definitive * (1 + 0.45)
            
                if amaz_price_if_definitive > 25 and amaz_price_if_definitive <= 35:
                    
                    price_plus_percent = amaz_price_if_definitive * (1 + 0.40)
                
                if amaz_price_if_definitive > 35 and amaz_price_if_definitive <= 45:
                    
                    price_plus_percent = amaz_price_if_definitive * (1 + 0.35)
                           
                                
                links_effettivi = links_effettivi['href']
				
                #COMPARIAMO IL LINK BUONO CON QUELLI PRESENTI ALL'INTERNO DELLA GLOBAL LIST - SE PRESENTE SI BLOCCA LO SCRIPT E SI RIPARTE DA CAPO, ALTRIMENTI SI CONTINUA E SI AGGIUNGE ALLE DUE LISTE (FINAL E GLOBAL)
                
				print 'EFFETTIVI: ',links_effettivi
                
                class StopLookingForThings(Exception): pass
                
                try:
                    with open("/home/blackpenny/Desktop/bot_ebay_amazon/Parte_1_bot_ebay_amaz/global_list.csv", "r") as file_global_file:
                        file_global_reader = csv.reader(file_global_file)

                        for row in file_global_reader:                                                                                      #L'oggetto csv.reader con il primo for ci fornisce una lista di rows, quindi serve un secondo for
                            for field in row:                                                                                               #per iterare linea per linea e quindi comparare il link con quelli presenti nel file csv.
                                print 'FIELD:' ,field
                                if field == links_effettivi:
                                    print("Item already inside global list - start again with another item")
                                    #file_global_reader.close()
                                    links_effettivi = None
                                    amaz_no_avail_only_numb = None
                                    price_plus_percent = None
                                    raise StopLookingForThings()
                                    
                except StopLookingForThings:
                    print "EXCEPTION RAISED"
                    counter = counter +1                                                               

                    counter2 = counter2 +1

                    #Il check sottostante controlla che il counter2 non abbia valore 24: se questo accade fa avanzare la pagina da analizzare di +1 e resetta il counter2 a 0 di modo che possa iniziare il conteggio da capo per la pagina nuova.
                    if counter2 == 24:
                        print 'Avanzamento pagina'
                        page_counter = page_counter +1

                        counter2 = 0
                        continue

                    continue
                print "NO EXCEPTION"
                
                #AGGIUNGIAMO - 1 AGLI OGGETTI RIMASTI (SE DIVERSI DA "NONE") POICHE' EBAY AGGIUNGE SEMPRE UN OGGETTO IN PIU' AL CONTEGGIO.
                #ESEMPIO: OGGETTI RIMASTI SU AMAZON 5, SU EBAY DIVENTANO 6
                               
                if amaz_no_avail_only_numb == None:                                                                                     #Se la variabile e' "None" allora la trafsormo in "0" per renderla un numero intero di modo che
                    amaz_no_avail_only_numb = 0                                                                                         #possa essere comparata nell'if sottostante.
                if 1 <= amaz_no_avail_only_numb <= 9:                                                                                   #In questo modo se la variabile e' compresa fra 0 e 9 viene diminuita di "-1"
                    amaz_no_avail_only_numb = amaz_no_avail_only_numb - 1                
                if amaz_no_avail_only_numb == 0:                                                                                        #Riportiamo il None da 0 al suo valore dopo che e' stato utilizzato nella comparazione.
                    amaz_no_avail_only_numb = None                                                                                      #Se avessimo lasciato il None cosi' c'era il rischio di seri incasinamenti tra variabili nulle
                                                                                                                                        #o stringhe con i numeri (falsi positivi o falsi negativi).
                #COLLEGHIAMO LE VARIABILI AL DIZIONARIO DELLA FINAL LIST PER ASSOCIARLE AI RISPETTIVI FIELD NAMES               
                
                good_dict.setdefault("Links",[]).append(links_effettivi)                                                                #Creiamo un dizionario di liste dove come chiavi abbiamo i nomi che diventeranno i field names nel
                good_dict.setdefault("Pezzi_rimasti",[]).append(amaz_no_avail_only_numb)                                                #file .csv: "Links","Pezzi_rimasti" e "Prezzo_con_20_percento".
                good_dict.setdefault("Prezzo_con_percentuale_calcolata",[]).append(price_plus_percent)                                  #Come valori aggiungeremo i rispettivi dati estratti dallo script.
                                                                                                                                        #"good_dict" rappresenta il dizionario.
                
                #COLLEGHIAMO LA VARIABILE RELATIVA AI LINKS AL DIZIONARIO DELLA GLOBAL LIST PER ASSOCIARLA AL FIELD NAME "ITEM PUBLISHED"
                
                global_dict.setdefault("Items Published",[]).append(links_effettivi)
                                
            else:
        #Qua andra' il "continue" per far tornare all'inizio del loop while se non ci interessa l'oggetto in questione
                print "Prezzo calcolato troppo basso - non merita venderlo"
            
                amaz_no_avail_only_numb = None
                
                counter = counter +1

                counter2 = counter2 +1

                if counter2 == 24:

                    page_counter = page_counter +1

                    counter2 = 0
					
                continue

        amaz_no_avail_only_numb = None
            
        counter = counter +1

        counter2 = counter2 +1

        if counter2 == 24:

            page_counter = page_counter +1

            counter2 = 0
            
    #except Exception:
    except EnvironmentError:                                                                    #Ho messo "EnvironmentError" per escludere momentaneamente a fini di test l'except
        
        amaz_no_avail_only_numb = None
        
        counter = counter +1

        counter2 = counter2 +1

        if counter2 == 24:

            page_counter = page_counter +1

            counter2 = 0
    
        pass
      

#FINE DEL WHILE LOOP
   
       
print "GOOD DICT BEFORE:" ,good_dict
def remove_empty_keys(d):
    for k in d.keys():
        if not d[k]:
            del d[k]
            
remove_empty_keys(good_dict)
print "GOOD DICT AFTER:" ,good_dict

#SCRITTURA SUL FILE FINAL        
keys = sorted(good_dict.keys())                                                                                 #NON MI E' CHIARA L'ULTIMA RIGA ma scrive un dizionario di liste e lo ordina per ordine alfabetico delle sue chiavi
with open("good_items_final_list.csv", "wb") as outfile:                                                        #quando va a scriverlo sul file .csv, mettendo le chiavi come field names e i rispettivi valori sotto in ogni singolo
    writer = csv.writer(outfile)#, delimiter = "\t")                                                            #row.
    writer.writerow(keys)
    writer.writerows(zip(*[good_dict[key] for key in keys]))                                                    #In questa riga con lo "zip" si prendono le coppie di "chiavi : valori" del dizionario "good_dict" e utilizzando il  
                                                                                                                #"for" le possiamo scrivere nella stessa colonna (da quello che ho capito il for in questo caso e' indispensabile
                                                                                                                #poiche' itera tra i vari row della colonna del rispettivo field name - ovvero della chiave - scrivendo tutti i dati
                                                                                                                #collegati a quella chiave.               
                
#SCRITTURA SUL FILE GLOBAL
                                                                                      
keys = global_dict.keys()                                                                                                   
with open('/home/blackpenny/Desktop/bot_ebay_amazon/Parte_1_bot_ebay_amaz/global_list.csv', 'a') as file_global_write:    
    writer = csv.writer(file_global_write)
    writer.writerow(keys)
    writer.writerows(zip(*[global_dict[key] for key in keys]))                                                                  
        
#PULIAMO IL FILE GLOBAL LIST DALLE RIPETIZIONI DI "ITEMS PUBLISHED"

f1 = open('/home/blackpenny/Desktop/bot_ebay_amazon/Parte_1_bot_ebay_amaz/global_list.csv', 'rb')
object_reader = csv.reader(f1)
writer = open("/home/blackpenny/Desktop/bot_ebay_amazon/Parte_1_bot_ebay_amaz/global_list_cleared.csv", "wb")
writer_object = csv.writer(writer)
global_list = set()
for element in object_reader:
    for line in element:
        if line in global_list: continue # skip duplicate

        global_list.add(line)
        writer_object.writerow([line])
f1.close()
writer.close()

#QUA TOGLIAMO TUTTE LE LINEE VUOTE

f1 = open('/home/blackpenny/Desktop/bot_ebay_amazon/Parte_1_bot_ebay_amaz/global_list_cleared.csv', 'rb')
object_reader = csv.reader(f1)
writer = open("/home/blackpenny/Desktop/bot_ebay_amazon/Parte_1_bot_ebay_amaz/global_list_cleared_final.csv", "wb")
writer_object = csv.writer(writer)
global_list = set()
for row in object_reader:    
    for line in row:
        #print line
        if line.strip():
            writer_object.writerow([line])                                                                             #IMPORTANTE METTERE LE QUADRE PER "LINE" O VERRANNO SCRITTI I LINK LETTERA PER LETTERA IN OGNI ROW...        
f1.close()
writer.close()   

#RINOMINIAMO IL NUOVO FILE CREATO "GLOBAL_LIST_CLEARED_FINAL" IN "GLOBAL_LIST" DI MODO CHE OGNI VOLTA CHE FACCIAMO GIRARE TUTTI GLI SCRIPT ABBIAMO IL FILE GLOBAL_LIST PULITO E AGGIORNATO SU CUI AGGIUNGERE EVENTUALI NUOVI LINKS E DA
#UTILIZZARE PER LA COMPARAZIONE.

for filename in os.listdir("/home/blackpenny/Desktop/bot_ebay_amazon/Parte_1_bot_ebay_amaz"):
    if filename.startswith("global_list_cleared_final"):
        os.rename(filename, filename[:11] + ".csv")                                                             		#Teniamo solo i primi 11 caratteri e ci aggiungiamo l'estensione.        
        
#COPIAMO IL FILE "GOOD_ITEMS_FINAL_LIST.CSV" NELLA DIR DEL SECONDO SCRIPT
copyfile("/home/blackpenny/Desktop/bot_ebay_amazon/Parte_1_bot_ebay_amaz/good_items_final_list.csv", "/home/blackpenny/Desktop/bot_ebay_amazon/Parte_2_bot_ebay_amaz/good_items_final_list.csv")
