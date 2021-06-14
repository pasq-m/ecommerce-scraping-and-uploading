#Seconda parte del bot per automatizzare la pubblicazione di inserzioni su ebay.
#Questo script estrae i link salvati con lo script della "parte 1" e, uno ad uno, visita le pagine di amazon per estrarre i dati testuali che ci interessano, salvandoli su singoli files .csv.
#Come modulo principale utilizza BeautifulSoup

from bs4 import BeautifulSoup


import os
import re
import csv
import urllib
import urllib2
import requests
import string
import codecs
import time


#CONTEGGIO NUMERO LINKS PRESENTI NEL FILE .CSV
with open("good_items_final_list.csv") as f:															#Con questo blocco di codice apro un loop per contare il numero di righe presenti nel file .csv, cosicche' da poter sapere
    #reader = csv.reader(f,delimiter = ",")																#su quanti oggetti dovro' lavorare (ogni file avra' verosimilmente un numero di link differenti per questo non posso lavorare
    #data = list(reader)																				#su un numero predefinito.
    #row_count = len(data)																				#In pratica crea una lista mentre legge il file .csv e successivamente ne conta gli elementi.
    data = f.readlines()																				 
    																									
    sep = ','																							
    data = [x.strip('\n') for x in data]																#"readlines()" crea alla fine di ogni elemento della lista caratteri non voluti "\n" e "\r" che dobbiamo rimuovere con il
    data = [x.strip('\r') for x in data]																#metodo "strip()".
    del data[:1]                                                                                        #Rimuovo il primo elemento della lista che sarebbe "Links", che altrimenti non viene rimosso perche' prima della prima virgola (vedi sotto).
    data = [item.split(sep, 1)[0] for item in data]                                           			 
                                                                                                        
                                                                                                        #Il filtro applicato dice "rimuovi tutto dopo la virgola in ogni elemento".                                                                                             
            
    row_count = len(data)																				#Conto il numero di elementi presenti nella lista, cosicche' possa utilizzare tale numero successivamente nel counter
    row_count = row_count - 1                                                                           #Sottraggo di 1 per togliere la prima linea che rappresenta i field names nel file .csv.
    
    
    
#USIAMO UN LOOP BASATO SU UN COUNTER EQUIVALENTE AL NUMERO DI LINKS TROVATI (VARIABILE ROW_COUNT)

counter = 0
list_counter = 0                                                                                        #Va impostata di default su "1" altrimenti legge anche il field name.
file_numb_counter = 1
next_counter = 0


with open('/home/blackpenny/Desktop/bot_ebay_amazon/Parte_1_bot_ebay_amaz/good_items_final_list.csv') as f:     
    reader = csv.reader(f)                                                                                              

    while counter <= row_count:
        #print 'NEXT COUNTER:' ,next_counter
        #print 'ROW COUNTER:' ,row_count
		
    #PARTE SULL'ESTRAZIONE DEL PREZZO DAL FILE "GOOD_ITEMS_FINAL_LIST.CSV"    
        time.sleep(2)                                                                                   #Diamo una pausa di 2 secondi tra un oggetto e l'altro per ridurre l'eventualita' di un "service unavailable 503 error".
        if counter == 0:                                                                                #Utilizza il counter di base perche' ci serve un modo per far fare un avanzamento in piu' (un "next") SOLO la prima volta
            row1 = next(reader)                                                                         #che gira il loop while e quindi lo script.    
        if next_counter <= row_count:                                                                   #Avanza di linea in linea ad ogni loop tante volte quanti sono i links presenti nel file "good_items_final_list.csv".
            row_next = next(reader)
            #row_next = next(reader)
            row_quantity = row_next[1]
            row_price = row_next[2]
            
            
        next_counter = next_counter +1

        #print row_reading
        quantity_var = row_quantity
        prezzo_var = row_price
        #print 'PREZZO VAR:' ,prezzo_var
        file_numb_counter_str = str(file_numb_counter)                                                      #Rendiamo la variabile definita prima del loop while "file_numb_counter" una stringa per poterla concatenare piu' giu'
                                                                                                            #durante la creazione del nome del file .csv da creare.
        #print 'DATA + COUNTER:' ,data[list_counter]														#In questo modo dovrei selezionare uno specifico elemento all'interno della lista in ordine crescente dal primo all'ultimo
                                                                                                            #basandomi sul counter "list_counter" che aumenta di +1 ad ogni fine di loop.

        url = data[list_counter]																			#Alla variabile "url" adesso abbiamo collegato il link di amazon pulito (il link della prima riga sul .csv e con 
                                                                                                            #"[list_counter]" gli indichiamo di volta in volta di scegliere i link posizionati alle righe successive) su cui poter
                                                                                                            # lavorare - tale link avanzera' di +1 alla volta poiche' "list_counter" e' un counter che aumenta alla fine di ogni loop.
        html = requests.get(url)																			#Utilizziamo il modulo "requests" per ottenere una pagina web completa, collegandola alla variabile "html" che rappresenta
                                                                                                            #un oggetto "Response" da cui possiamo lavorare sui dati della pagina.
        soup = BeautifulSoup(html.content, "html.parser")													#Utilizziamo i dati completi scaricati da requests e li "leggiamo" in modo pulito tramite il BeautifulSoup, 
																											#collegando il tutto alla variabile "soup"

    #ANDIAMO A TROVARE E A SALVARE IN UNA VARIABILE IL TITOLO DEL PRODOTTO NELLA PAGINA
        
        #Per prima cosa controlliamo se il prodotto e' venduto e spedito da Amazon o venduto da terzi e soltanto spedito da Amazon (a noi ci vanno bene entrambe le cose - ovvero che sia spedito da Amazon).
        
        try:                                                                                                #Verifichiamo la presenza di un tag specifico presente quando il prodotto e' SOLO spedito da Amazon.
            check_sell_amaz = soup.find('a', {'id' : 'SSOFpopoverLink'})
            print check_sell_amaz 
            check_sell_amaz_text = check_sell_amaz.get_text()
            check_sell_amaz_text = "".join(check_sell_amaz_text.split())
            if check_sell_amaz_text != "speditodaAmazon":                                                   #If messo per sicurezza ma probabilmente inutile: se esiste quel tag credo che il testo controllato dall'if ci sia per
                print "NOT SHIPPING BY AMAZON - PROCEEDING TO THE NEXT ITEM"                                #forza, nel dubbio faccio comunque il condizionale.
                counter = counter + 1
                list_counter = list_counter + 1
                file_numb_counter = file_numb_counter + 1
                continue
            
            print "ITEM SHIPPED BY AMAZON AND SOLD BY OTHERS - IT'S GOOD"                                   #Messaggio per informare del try positivo riscontrato: il prodotto e' venduto da altri ma spedito da Amazon, e' ok.
            
        except AttributeError:                                                                              #Il tag non esiste e si alza un'eccezione sotto la quale controlliamo i testi normalmente presenti negli oggetti venduti
            print "NOT SOLD BY VENDOR AND SHIPPED BY AMAZON - CHECK NEXT CONDITIONAL"                       #e spediti da Amazon.
        
            check_amazon_vendor = soup.find('div', {'id' : 'merchant-info'})
            #print check_amazon_vendor
            check_amazon_vendor_text = check_amazon_vendor.get_text()
            check_amazon_vendor_text = "".join(check_amazon_vendor_text.split())
            print check_amazon_vendor_text
            #Se l'oggetto non contiene ne' la prima fra ne' la seconda allora il condizionale e' vero e viene eseguita la parte di codice compresa dentro all'if: l'ogg. non e' venduto da Amazon e (dal try precedente) ne' spedito da loro.        
            if check_amazon_vendor_text != "VendutoespeditodaAmazon.Confezioneregalodisponibile." and check_amazon_vendor_text != "VendutoespeditodaAmazonconimballaggioaperturafacilecertificato.Confezioneregalodisponibile.":   
                print "NOT SELLING BY AMAZON - PROCEEDING TO THE NEXT ITEM"
                counter = counter + 1
                list_counter = list_counter + 1
                file_numb_counter = file_numb_counter + 1
                continue
        
        try:

            amaz_title = soup.find('span', {'class' : 'a-size-large'})											#Troviamo il punto nel documento html dove e' contenuto il titolo.
            print amaz_title
            amaz_title_text = amaz_title.get_text()															    #Col comando "get_text()" filtriamo i dati e otteniamo solo il testo, ovvero il titolo ripulito da caratteri non necessari
            #amaz_title_text = amaz_title_text.encode("utf-8")                                                  #Codifichiamo il testo in "utf-8" per comprendere anche eventuali caratteri non compresi all'interno dell' ASCII, come ad
                                                                                                                #esempio tutti i caratteri accentati.
            amaz_title_text = amaz_title_text.strip()                                                           #Con "strip()" rimuoviamo tutti gli spazi e i tabs prima e dopo la stringa di testo vera e propria.
            print amaz_title_text                                                                               

        except AttributeError:

            error_503_title = soup.title.string                                                                 #L'eccezione controlla se si tratta di un errore di pagina 503 di Amazon o (piu' sotto) di un errore di altra natura. 
            print 'ERROR 503:' ,error_503_title 
            if error_503_title == "503 - Service Unavailable Error":

                print "Service Unavailable Error"
                counter = counter + 1
                list_counter = list_counter + 1
                file_numb_counter = file_numb_counter + 1

            else:

                print "EXCEPTION: Unknown AttributeError"
                counter = counter + 1
                list_counter = list_counter + 1
                file_numb_counter = file_numb_counter + 1
            continue

    #SELEZIONIAMO IL NOME DEL PRODUTTORE CHE USEREMO COME "MARCA" SU EBAY
        
        try:
            amaz_brand = soup.find('a', {'id' : 'brand'})
            amaz_brand = amaz_brand.get_text()
            print amaz_brand
            amaz_brand = amaz_brand.strip()
            
        except AttributeError:
            print "NO BRAND - SETTING NONE VARIABLE FOR BRAND FIELD"
            amaz_brand = "NO BRAND"

    #ADESSO SELEZIONIAMO E SCARICHIAMO LA PRIMA IMMAGINE DEL PRODOTTO

        #amaz_img_url = soup.find('div', {'class' : 'imgTagWrapper'})

        amaz_img_url = soup.find('img', {'id' : 'landingImage'})											#Navighiamo dentro al tag "img"

    #Utilizziamo il "try" per provare a vedere se esiste il valore dentro all'attributo "data-old-hires" - se e' presente andra' avanti e scarichera' l'immagine ad alta risoluzione, altrimenti, scarichera' quella, sempre presente,
    #a bassa risoluzione.
        try:
            amaz_img_url_var = amaz_img_url["data-old-hires"]												#Basta usare l'oggetto "amaz_img_url", che corrisponde alla parte di html contenente il link che ci interessa, e "cercarci"
            urllib.urlretrieve(amaz_img_url_var, os.path.basename(amaz_img_url_var))						#dentro (SENZA .find) con "["data-old-hires"]" per estrarre automaticamente il suo valore, ovvero il link.
        except Exception:
            amaz_img_url_var = amaz_img_url["src"]
            urllib.urlretrieve(amaz_img_url_var, os.path.basename(amaz_img_url_var))						#Scarico l'immagine nella directory dove gira lo script utilizzando "urllib.urlretrieve" (vale anche per sopra).
            pass																							

        def findnamefile(img_var):																			#Definisco una funzione chiamata "findnamefile" che ha lo scopo di rimuovere tutti i caratteri
            return img_var[38:]																				#della directory delle immagini sul sito di amazon, lasciando solo il nome del file della foto che salvero' insieme agli
                                                                                                            #altri dati nel file .csv, cosicche' da poter poi caricare, su ebay, per ogni prodotto la sua immagine corretta.
        amaz_img_stripped = findnamefile(amaz_img_url_var)													#Questa variabile contiene il nome del file dell'immagine da salvare nel file.csv.
        amaz_img_stripped = str(amaz_img_stripped)                                                          #Qua rendiamo il nome dell'immagine una variabile di tipo stringa e rimuoviamo i primi 11 caratteri rappresentanti una
        amaz_img_stripped = amaz_img_stripped[11:]                                                          #parte della directory scaricata col nome da Amazon.

    #CERCHIAMO E SALVIAMO I DETTAGLI (OVVERO LE SPECIFICHE TECNICHE PRODOTTO) DELL'INSERZIONE (OVE PRESENTI)

        try:
            wrapper_find = soup.find('div', {'id' : 'prodDetails'}) 										#Controlliamo inanzitutto che sia presente la scheda tecnica
            wrapper_tag = wrapper_find.find('div', {'class' : 'wrapper ITlocale'})
            wrapper_sec = wrapper_tag.find('div', {'class' : "secHeader"})
            wrapper_sec_spanned = wrapper_sec.span															#".span" dice al modulo di spostarsi dentro al tag "<span>" contenente "Specifiche prodotto", altrimenti dal tag precedente
                                                                                                            #prenderemmo anche una riga vuota sopra e sotto a questo testo.

            amaz_spec_tec = soup.find('div', {'class' : 'pdTab'})
            amaz_spec_code = amaz_spec_tec.find('td', {'class' : 'value'})
            amaz_spec_code_lab = amaz_spec_tec.find('td', {'class' : 'label'})
            amaz_spec_code_lab_clear = amaz_spec_code_lab.get_text()

            if amaz_spec_code_lab_clear == "Codice articolo":                
                amaz_spec_code_value = amaz_spec_code_lab.next_sibling										#Col "next_sibling" ci spostiamo lateralmente e scegliamo il td con valore "value" cosicche' da poter ottenere il valore
                amaz_spec_code_value_clear = amaz_spec_code_value.get_text()								#collegato al codice articolo (in questo caso).
                #amaz_spec_code_value_clear.encode("utf-8")
                #amaz_spec_code_value_clear
            else:
                amaz_spec_code_value_clear = 'NO CODE'
                print amaz_spec_code_value_clear

            try:

                amaz_spec_peso_find = amaz_spec_tec.find('tr', {'class' : 'size-weight'})                   #Genera un errore perche' se non e' presente il campo "Peso" non trova nemmeno i tag e passa direttamente all'except saltando
                amaz_spec_peso_lab = amaz_spec_peso_find.find('td', {'class' : 'label'})                    #il resto del codice.
                amaz_spec_peso_lab_clear = amaz_spec_peso_lab.get_text()

                if amaz_spec_peso_lab_clear == "Peso articolo":									    		#Prendiamo il valore "Peso articolo"
                    amaz_spec_peso_value = amaz_spec_peso_lab.next_sibling
                    amaz_spec_peso_value_clear = amaz_spec_peso_value.get_text()
                    amaz_spec_peso_var = amaz_spec_peso_value_clear
                    print amaz_spec_peso_var
                else:
                    amaz_spec_peso_var = 'NO WEIGHT'

            except AttributeError:
                print "No weight - inserting default value"
                amaz_spec_peso_var = 'NO WEIGHT'
                pass

            try:

                amaz_spec_dimen_find = amaz_spec_tec.find('tr', {'class' : 'size-weight'})
                amaz_spec_dimen_tag = amaz_spec_dimen_find.next_sibling.next_sibling                        #Dobbiamo in questo caso "raddoppiare" il "next_sibling" poiche' il primo restituisce linee bianche e il secondo trova
                #print amaz_spec_dimen_tag                                                                  #infine l'altro tag "size-weight" collegato alle dimensioni che ci interessano.
                amaz_spec_dimen_lab = amaz_spec_dimen_tag.find('td', {'class' : 'label'})
                amaz_spec_dimen_lab_clear = amaz_spec_dimen_lab.get_text()
                #print amaz_spec_dimen_lab_clear

                if amaz_spec_dimen_lab_clear == "Dimensioni prodotto":										#Prendiamo il valore "Dimensioni prodotto"
                    amaz_spec_dimen_value = amaz_spec_dimen_lab.next_sibling
                    amaz_spec_dimen_value_clear = amaz_spec_dimen_value.get_text()
                    amaz_spec_dimen_var = amaz_spec_dimen_value_clear
                    print amaz_spec_dimen_var
                else:
                    amaz_spec_dimen_var = 'NO SIZE'

            except AttributeError:
                print "No size - inserting default value"
                amaz_spec_dimen_var = 'NO SIZE'
                pass


    #Se la scheda tecnica non fosse presente si genererebbe un errore che dal "try" porterebbe il flusso di controllo del programma al suo "except" (qua sotto) registrando le variabili della scheda tecnica con nomi di default
    #per evitare errori nella scrittura del file .csv sottostante.

        except (AttributeError, NameError):
            print "No Scheda Tecnica - inserting default data"												#continuare l'esecuzione del programma.
            amaz_spec_code_value_clear = 'NO CODE'
            amaz_spec_peso_var = 'NO WEIGHT'
            amaz_spec_dimen_var = 'NO SIZE'
            pass

    #SEZIONE SULLA DESCRIZIONE PRODOTTO (OVE PRESENTE)

        try:
            prod_descr_find = soup.find('div', {'id' : "productDescription"})								#Trovo la descrizione completa del prodotto, se presente.
            amaz_descr_clear = prod_descr_find.get_text()
            #print amaz_descr_clear
            amaz_descr_var = amaz_descr_clear
            #amaz_descr_var = amaz_descr_var.encode("utf-8")                                                #Codifichiamo il testo in "utf-8" per comprendere anche eventuali caratteri non compresi all'interno dell' ASCII, come ad
            #amaz_descr_var_uni = amaz_descr_var.decode("utf8")#.encode("utf8")                             #esempio tutti i caratteri accentati.
            amaz_descr_var_uni_strp = amaz_descr_var.strip()

            #print amaz_descr_var_uni_strp

        except AttributeError:
            print "No Descrizione - inserting default value"
            amaz_descr_var_uni_strp = 'NO DESCRIPTION'
            pass


    #SEZIONE DI CREAZIONE DIZIONARIO E SCRITTURA DATI NEL FILE .CSV

        amaz_data_dict = {}                                                                                 #Creiamo un dizionario vuoto

        #Aggiungiamo "chiavi" e "valori" al dizionario per andare a costruire il file .csv con i dati del prodotto.

        amaz_data_dict.update({'Nome_immagine':amaz_img_stripped})
        amaz_data_dict.update({'Titolo_prodotto':amaz_title_text})
        amaz_data_dict.update({'Marca':amaz_brand})
        amaz_data_dict.update({'Descrizione_prodotto':amaz_descr_var_uni_strp})
        amaz_data_dict.update({'Codice_articolo':amaz_spec_code_value_clear})
        amaz_data_dict.update({'Peso_prodotto':amaz_spec_peso_var})
        amaz_data_dict.update({'Dimensione_prodotto':amaz_spec_dimen_var})
        amaz_data_dict.update({'Prezzo':prezzo_var})
        amaz_data_dict.update({'Quantity':quantity_var})
                

        print amaz_data_dict

        changing_file_name = "file_" + file_numb_counter_str + ".csv"

           
        #with codecs.open(changing_file_name, 'w', encoding='utf-8') as write_csv:                          #Scriviamo le coppie di dati del dizionario nel file .csv che andiamo a creare.
        with codecs.open(changing_file_name, 'w') as write_csv: 
            file_writer = csv.DictWriter(write_csv, amaz_data_dict.keys())                                  #Per visualizzare i dati correttamente all'interno dell'open office impostare "comma" come separatore e le virgolette '"'
            file_writer.writeheader()                                                                       #come delimiter di testo.            
            file_writer.writerow({k:v.encode('utf8') for k,v in amaz_data_dict.items()})

        write_csv.close() 	

    #RESETTIAMO LE VARIABILI PER IL PROSSIMO LOOP PER EVITARE "CATTIVI RICORDI" DA PRECEDENTE LOOP

        amaz_title_text = None
        amaz_brand = None
        amaz_img_stripped = None
        amaz_spec_code_var = None
        amaz_spec_peso_var = None
        amaz_spec_dimen_var = None
        amaz_descr_var_uni_strp = None


        counter = counter + 1
        list_counter = list_counter + 1
        file_numb_counter = file_numb_counter + 1
    #fine while counter
    