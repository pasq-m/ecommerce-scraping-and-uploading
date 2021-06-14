#Parte terza del bot per pubblicare inserzioni su ebay.
#Script che analizza i files .csv creati dalla "parte 2" contenenti i dati da inserire nei form di pubblicazione inserzione su ebay.
#Utilizza come modulo Selenium

#IMPORTANTE: a bozza nuova (1 volta al mese) ebay cambia il codice numerico e quindi tocca aggiornarlo a mano.

from path import path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains                                                                                 #ActionsChains e' una classe che serve a generare una sequenza di azioni come ad es. il movimento e il
from selenium.common.exceptions import ElementNotVisibleException                                                           #click del mouse.
import time                                                                                                                 
import os
import csv
import glob
import shutil
import stat
import itertools
import re
import Tkinter as tk
import pickle

#UTILIZZIAMO QUESTA PARTE DI CODICE PER COPIARE LE IMMAGINI DALLA CARTELLA DEL SECONDO SCRIPT A QUELLA DI QUESTO PER POTERLE POI CARICARE NELLE INSERZIONI.

#IMPORTANTE: QUANDO LO SCRIPT SARA' FUNZIONANTE E DEFINITIVO DOVREMO AGGIUNGERE DEL CODICE IN QUESTA SEZIONE CHE SI OCCUPERA' DI ELIMINARE LE IMMAGINI PASSATE PER EVITARE CHE OGNI VOLTA CHE FACCIAMO GIRARE IL SECONDO SCRIPT,
#QUESTE SI ACCUMULINO INSIEME A QUELLE VECCHIE.

#Funzione da utilizzare in ambiente Linux per copiare i file (immagini) dalla cartella dove lo script 2 ha pubblicato le immagini, a quella contenente lo script 3; inoltre cambia i permessi
#dei file assegnando quelli dell'user attuale invece che quelli root che imposta di default

def CopyPasteMultipleFilesSameExt(src, dest):                                                                               
    files = glob.iglob(os.path.join(src, "*.jpg"))                                                                          
    for file in files:                                                                                                      
        file_stat = os.stat(file)                                                                                           
        owner = file_stat[stat.ST_UID]
        group = file_stat[stat.ST_GID]
        #print "Owner: %d  Group: %d" % (owner, group)  # for diagnostics
        shutil.copy2(file, dest)
        os.chown(dest, owner, group)

#Qua dobbiamo inserire la dir dei file di origine (dove è contenuto lo script 2) e quella dei file di destinazione (dove c'è lo script 3)
CopyPasteMultipleFilesSameExt("DIR ORIGINE", "DIR DESTINAZIONE")

        
#CONTIAMO IL NUMERO DI LINEE DEL FILE CREATO DAL PRIMO SCRIPT PER UTILIZZARE TALE NUMERO COME COUNTER-LIMITE NEL WHILE.

file_read = csv.reader(open("/home/blackpenny/Desktop/bot_ebay_amazon/Parte_1_bot_ebay_amaz/good_items_final_list.csv"))	#Contiamo le linee del file creato dal primo script, ovvero il file contenente i links buoni da
row_count = sum(1 for row in file_read)																					  #utilizzare negli altri due script.

row_count = row_count - 1                                                                                               #Sottraggo di 1 per togliere la prima linea che rappresenta i field names nel file .csv.
#print row_count
file_cnt = 25																										 #counter che rappresenta il numero di files .csv creati dal secondo script
#dal_sec_in_poi = 0

while file_cnt <= row_count:																						 #finche' non superiamo il numero di file presenti lo script gira
																													
    #CARICHIAMO DAL FILE .CSV I DATI DA INSERIRE NEL FORM DELLA NUOVA INSERZIONE
    try:                                                                                                                   #Mettiamo un try perche' in caso ci siano uno o piu' oggetti (e quindi linee nel file final list) ma, per 
                                                                                                                           #qualche motivo lo script 2 non abbia creato i rispettivi files, il while andrebbe in tilt continuando 
                                                                                                                           #a cercare file quando non ce ne sono piu' - cosi' con l'except ci salviamo e chiudiamo lo script avendo gia'         
                                                                                                                           #finito di pubblicare gli oggetti di tutti i files. 
        file_cnt = str(file_cnt)                                                                                           #Diventa stringa per poter essere concatenato sotto nell'apertura dei files.
    except IOError:
        #CANCELLAZIONE DI TUTTI I FILE CONTENENTI I DATI PER CREARE LE INSERZIONI - PER SICUREZZA (CANCELLA ANCHE LA FINAL LIST POICHE' ANCH'ESSA HA COME ESTENSIONE ".CSV" MA VERRA' RICOPIATA LA PROSSIMA VOLTA QUANDO VENGONO FATTI GIRARE
        #DA CAPO TUTTI GLI SCRIPT).

        filelist = [ f for f in os.listdir("/home/blackpenny/Desktop/bot_ebay_amazon/Parte_2_bot_ebay_amaz/") if f.endswith(".csv") ]
        for f in filelist:
            os.remove(f)

        #CANCELLAZIONE DI TUTTE LE IMMAGINI SEMPRE NELLA DIRECTORY DEL SECONDO SCRIPT E IN QUELLA DEL TERZO

        filelist = [ f for f in os.listdir("/home/blackpenny/Desktop/bot_ebay_amazon/Parte_2_bot_ebay_amaz/") if f.endswith(".jpg") ]
        for f in filelist:
            os.remove(f)

        filelist = [ f for f in os.listdir("/home/blackpenny/Desktop/bot_ebay_amazon/Parte_3_bot_ebay_amaz/") if f.endswith(".jpg") ]
        for f in filelist:
            os.remove(f)
        print "IOERROR EXCEPT RAISED: SCRIPT 3 COMPLETED AND FILES DELETED" 
        
    try:
    
        mycsv = csv.reader(open("/home/blackpenny/Desktop/bot_ebay_amazon/Parte_2_bot_ebay_amaz/file_" + file_cnt + ".csv"))
        for row in mycsv:
            nome_imm = row[0]
            var_prezzo_buona = row[1]
            dimens = row[2]
            codice = row[3]
            peso = row[4]
            quantity = row[5]
            marca = row[6]
            titolo = row[7]
            descr = row[8]
       
    except IOError:
        print "IOERROR FILE MANCANTE - SALTIAMO E PASSIAMO AL PROSSIMO DA ANALIZZARE"
        file_cnt = int(file_cnt)                                                                                       #Va fatto tornare "int" altrimenti ad ogni loop non puo' essere paragonato come numero.
        file_cnt = file_cnt +1
        continue
    
    file_cnt = int(file_cnt)                                                                                           
    
    if quantity == "":                                                                                                 #Se il row del file csv della quantita' e' vuoto - "" - mette "10" di default, altrimenti mette il numero presente
        quantity = 10                                                                                                  #nel row.
    #print "QUANTITA' AFTER:",quantity
    
    if "NO DESCRIPTION" in descr:                                                                                      #Se nel file creato dal secondo script abbiamo "NO DESCRIPTION" invece di una normale descrizione utilizzeremo
        descr = titolo                                                                                                 #il titolo dell'oggetto come descrizione. 
    
    if "NO CODE" in codice:                                                                                            #Come sopra solo lasciamo in caso vuoto il campo.     
        codice = ""
    
    var_prezzo_buona = var_prezzo_buona.replace(".", ",")                                                              #Sostituiamo il punto con la virgola nella cifra del prezzo o ebay non ne accettera' l'inserimento.
    
    
#PRENDIAMO L'IMMAGINE DELL'INSERZIONE ATTUALE E ANDIAMO A CARICARLA SU X - PRENDIAMO IL LINK E LO CONSERVIAMO IN UNA VARIABILE DA UTILIZZARE POI PER MODIFICARE IL TEMPLATE INSIEME ALLA DESCRIZIONE
         
    time.sleep(3)
    browser_pic = webdriver.Chrome()
    #browser = webdriver.Firefox()
    #browser.get("http://postimage.org/") 
    #browser.get("http://imgur.com")
    #browser.get("http://screenshot.net/free-image-uploader")
    
    browser_pic.get("http://www.hostpic.org/")
    time.sleep(6)
    
    upload_file = browser_pic.find_element_by_xpath("//form[@id='newupload']//input[@class='input2']")
    upload_file.send_keys("DIR CARTELLA IMMAGINE" + nome_imm)																#Inserire dir della cartella dove salvare l'immagine
    time.sleep(2)
    upload_btt = browser_pic.find_element_by_xpath("//div[@class='buttons']//input[@id='submit1']").click()
    time.sleep(6)
    select_direct_link_field = browser_pic.find_element_by_xpath("//textarea[@name='url2[]']").click()
    time.sleep(1)
    actionchains_0 = ActionChains(browser_pic)
    actionchains_0.key_down(Keys.CONTROL).send_keys("c").key_up(Keys.CONTROL).perform()                                     #Copio il contenuto della riga selezionata contenente il link da filtrare.
    time.sleep(2)
    #actionchains_0.key_down(Keys.CONTROL).send_keys("n").key_up(Keys.CONTROL).perform()
    #time.sleep(2)
    
    root = tk.Tk()                                                                                                          #Utilizzo il modulo Tkinter per usare una funzione che permette di inserire il contenuto della clipboard
    # keep the window from showing                                                                                          #su una variabile.
    root.withdraw()

    # read the clipboard
    copied_url_clear = root.clipboard_get()
    
    browser_pic.close()
    
        
#QUESTA PARTE DI CODICE SOTTOSTANTE VIENE ESEGUITA DAL SECONDO LOOP IN POI
        
    #with open("/home/blackpenny/Desktop/bot_ebay_amazon/Parte_3_bot_ebay_amaz/template_eby_modi", 'r') as content_file:
        #template_modi = content_file.read(5000)
        #template_modi = template_modi.decode('utf-8')                                                   					#Decodifichiamo da utf-8 a ASCII perche' cosi' a quanto pare non da problemi per essere
																															#letto dal Selenium.
    time.sleep(2)
    
    var1 = "superkeyword"
    var_marca = "supermarca"
    var_modello = "supermodello"
    var_colore = "supercolore"
	#var_quantita = 10
    var_prezzo = 999
    var_quantita_oggetti = 10

    #browser = webdriver.Firefox()
    browser = webdriver.Chrome()
    browser.get("https://signin.ebay.it/ws/eBayISAPI.dll?SignIn&ru=http%3A%2F%2Fwww.ebay.it%2F") 
    time.sleep(3)

    username = browser.find_element_by_xpath("//form[@id='SignInForm']//input[@type='text']")			
    password = browser.find_element_by_xpath("//form[@id='SignInForm']//input[@type='password']")
    username.send_keys("xxxxxxxx")																		#Qua inseriremo l'user del nostro account di Ebay
    password.send_keys("xxxxxxxx")																		#Qua la password
	#login_attempt = browser.find_element_by_xpath("//*[@type='submit']")								
	#login_attempt.submit()
    submit_button = browser.find_element_by_id("sgnBt")													#Selezioniamo il tasto submit per il login su ebay
    submit_button.submit()																				#Lo clicchiamo
    time.sleep(3)
    #browser.implicitly_wait(5)
	
    #DA ADESSO SIAMO LOGGATI DENTRO ALL'ACCOUNT

	#time.sleep(5)
	#browser.get("http://cgi5.ebay.it/ws/eBayISAPI.dll?SellHub3&from=wn") 								#Andiamo al modulo di messa in vendita avanzato per creare l'inserzione
	#wait = WebDriverWait(browser, 10)																	#Aspettiamo che lo script "trovi" l'id "keywords" sottostante nell'html prima di andare avanti ed inviargli un input
	#wait.until(EC.presence_of_element_located((By.ID, "keywords")))									#per evitare errori e interruzione script
	#job_name = browser.find_element_by_css_selector("h1.title").text

	#form_nome_inserz = browser.find_element_by_id("keywords")											#Selezioniamo il form per l'inserimento del nome dell'inserzione
	#form_nome_inserz.send_keys(var1)																	#Qua possiamo inviare il testo desiderato anche sottoforma di variabile (fondamentale per raccogliere variabili da altri script
																										#di scraping)
	#start_sell_butt = browser.find_element_by_id("aidZ4")												#Qua selezioniamo e sotto "clicchiamo" sul submit per registrare il nome dell'inserzione e passare alla pagina successiva
	#start_sell_butt.submit()

	#PAGINA DELLA SCELTA DELLE CATEGORIE

	#var_key_inserz = var1																				#ridefiniamo la variabile per il nome dell'inserzione (var1) con un'altra da utilizzare dinamicamente (ogni volta infatti i nomi
																										#delle inserzioni saranno diversi) e la inseriamo nell'url sottostante per scegliere direttamente anche la categoria (con id "11704")
																										
	#time.sleep(3)
	#browser.get("http://cgi5.ebay.it/ws/eBayISAPI.dll?NewListing&itemid=&sid=570330208910&cpg=3&js=1&aid=6&keywords=" + var_key_inserz + "&cat1=11704")
	#category_button = browser.find_element_by_id("aidZ1")												#Selezioniamo e clicchiamo il tasto per avanzare alla pagina successiva
	#category_button.submit()

	#PAGINA "CREA L'INSERZIONE"

	#SI RIPRENDE LA BOZZA CON I DATI SALVATI DI DEFAULT
    
    #Torniamo alla pagina di selezione della bozza che selezioneremo tramite click su icona immagine per evitare di trovare il nome con codice nuovo che viene creato per ogni bozza nuova.
    browser.get("http://csr.ebay.it/cse/start.jsf")
    time.sleep(8)
    click_draft_pic = browser.find_element_by_xpath("//a[@class='resume-draft']")
    click_draft_pic.click()
    time.sleep(2)
    tasto_ok = browser.find_element_by_xpath("//button[@class='btn btn-primary']")						#Si clicca su "ok" nella finestra pop-up che appare
    tasto_ok.click()
    time.sleep(6)    
    
	#PARTE INSERIMENTO TITOLO
	
    window_before = browser.window_handles[0]
    time.sleep(3)
    browser.find_element_by_id("title").clear()															#Eliminiamo per sicurezza eventuali titoli rimasti da inserzioni passate
    time.sleep(1)
    print('Titolo originale da modificare: ', titolo)													#Parte in cui mostriamo il titolo estratto dal file .csv e chiediamo all'utente di modificarlo - lo script resta in standby
    print 'Suffisso finale da copiare: - Spedizione GRATUITA | NUOVO'                                   #durante il processo.
    while True:																						   
        input_titolo_modi = raw_input("> ")																#C'e' un check sul numero di caratteri da inserire: se oltre gli 80 appare un messaggio e si deve reinserire nuovamente il
        if len(input_titolo_modi) <= 80:																#titolo modificato.
            break
        else:
            print("Your input should not be longer than 80 characters - try again")
											
    time.sleep(2)
    browser.switch_to_window(window_before)	
    browser.implicitly_wait(3)
    title_name = browser.find_element_by_id("title")													#Selezioniamo di nuovo il form adesso pulito e sotto inseriamo il titolo attuale
    title_name.send_keys(input_titolo_modi)
    select_nuovo = browser.find_element_by_xpath("//select[@id='itemCondition']/option[@value='1000']").click()			#Selezioniamo "Nuovo" nelle condizioni dell'oggetto
    time.sleep(4)
    try:																								#Con il "try" proviamo a vedere se e' presente il tasto "Elimina tutte le foto" - se e' presente viene letto il codice
																										#dentro al "try", se assente si solleva l'eccezione e si salta questa parte (non c'e' bisogno di cancellare le foto).
        #window_before = browser.window_handles[0]														#Creiamo un "handle" (da capire cos'e' - penso una sorta di referenza per riconoscere la finestra attuale, quella di base)
        rimuoviamo_tutte_foto = browser.find_element_by_xpath("//div[@id='removeallLyr']/a[@id='removeall']")
        rimuoviamo_tutte_foto.click()
        #window_pop_up_rmv_foto = browser.window_handles[1]
        #browser.switch_to_window(window_pop_up_rmv_foto)
        time.sleep(1)                                                                                   #Importante utilizzare i "time.sleep" per dare il tempo allo script di trovare la finestra pop up.
        alert = browser.switch_to_alert()                                                               #L'alert rappresenta una finestra pop-up.
        time.sleep(1)
        alert.accept()
        selenium.get_confirmation()																		#IMPORTANTE: a quanto pare dobbiamo inserire questa linea di codice perche' altrimenti selenium dopo aver gestito l'alert
        #browser.switch_to_window(window_before)														#non riesce ad andare avanti generando errori.
    except Exception:																					#in realta' qua il try genera comunque un errore che viene ignorato da "Exception" ma a quanto pare lo script va avanti
        print "Errore sconosciuto che non influenza lo svolgimento corretto dello script"				#comunque in modo corretto.
        pass
	time.sleep(2)
	upl_foto = browser.find_element_by_id("clUploadBtn").click()										#Clicchiamo sul pulsante per caricare foto che ci apre la seconda finestra
    time.sleep(2)
    window_after = browser.window_handles[1]															#Creiamo handle per la seconda finestra aperta (suppongo)
    browser.switch_to_window(window_after)																#Cambiamo il focus sulla seconda finestra aperta per poterci lavorare
	#browser.implicitly_wait(5) # seconds																#Con questo comando lo script dovrebbe aspettare che venga trovato l'elemento alla linea successiva per X secondi
    time.sleep(6)
    browser.find_element_by_id("useEPSlnkBasic").click()												#Andiamo alla versione base per caricare la foto (nella nuova finestra)
    time.sleep(5)
		
    browser.find_element_by_id("d").send_keys(os.getcwd()+ "/" +nome_imm)								#Seleziona la foto desiderata - NOTA BENE: "os.getcwd()" e' un metodo di python che rappresenta la directory dove sta girando il processo
																										#ovvero dove abbiamo avviato lo script, di conseguenza dobbiamo mettere le immagini nella stessa directory dello script per poterle caricare
    time.sleep(5)
    browser.find_element_by_id("uploadPics").click()													#Carica la foto
    time.sleep(8)
    browser.switch_to_window(window_before)																
    time.sleep(2)															
    element = browser.find_element_by_id('gtin_dd')														#EAN code: Selezioniamo la freccettina del dropdown menu prima, altrimenti non si renderanno visibili le opzioni
    element.click()																					    #E' importante mettere il click in seconda battuta perche' a quanto pare non funziona se messo direttamente insieme alla selezione
    browser.find_element_by_id("noGTIN").click()														#Qua selezioniamo "Non Applicabile"
    if marca == "NO BRAND":                                                                             #Se nel field marca troviamo "NO BRAND" allora seleziona "Marca generica/senza marca" nel form, senno' inserisci normalmente
        no_marca = browser.find_element_by_id("st_selval_0_0")                                          #la marca.
        no_marca.clear()
        no_marca = browser.find_element_by_id('DownArrow_0')                                            
        no_marca.click()     
        no_marca = browser.find_element_by_id('TagValueOptionList_0_option_1')
        no_marca.click()
    else:    
        form_marca = browser.find_element_by_id("st_selval_0_0")        								#MARCA: selezioniamo direttamente il form di testo e ci inseriamo la variabile per la marca dell'oggetto e cancelliamo il contenuto in ogni caso per sicurezza.
        form_marca.clear()
        form_marca.click()																				#IMPORTANTE: click in seconda battuta
        form_marca.send_keys(marca)    
    
	#MODELLO
    
    modello_try = browser.find_element_by_xpath("//input[@id='st_tmdata_0_1']")								   #Controlliamo se il primo blocco e' relativo al modello o meno.
    get_value = modello_try.get_attribute('value')															   #Estraiamo il valore dall'attributo "st_tmdata_0_1" per vedere se e' il modello.
    #print get_value
    str(get_value)
    if get_value == 'Modello!?^2!?^0!?^""!?^2':																   #Controlliamo se e' il modello.IMPORTANTE: utilizzare gli apici invece delle virgolette altrimenti
        modello = browser.find_element_by_xpath("//div[@id='TagOuterLayer_1']//input[@id='st_selval_0_1']")	   #si incasina con la coppia di virgolette presenti tra i caratteri dopo "Modello..."
        modello.clear()
        modello.click()
        modello.send_keys(codice)
        print "PRIMO BUONO"
        counter_layer_da_reset = 1

    else:																										#Se non e' buono il primo controlliamo il secondo blocco.
        modello_try = browser.find_element_by_xpath("//input[@id='st_tmdata_0_2']")
        get_value = modello_try.get_attribute('value')
        str(get_value)
        if get_value == 'Modello!?^2!?^0!?^""!?^2':																 #Controlliamo se e' il modello.
            modello = browser.find_element_by_xpath("//div[@id='TagOuterLayer_2']//input[@id='st_selval_0_2']")
            modello.clear()
            modello.click()
            modello.send_keys(codice)
            print "SECONDO BUONO"
            counter_layer_da_reset = 2
			
    
#AGGIUNGIAMO LA DESCRIZIONE, L'URL DELL'IMMAGINE E DEL THUMB E IL TITOLO AL FILE DI TESTO DI DEFAULT DEL TEMPLATE DI EBAY        
#Creiamo un file nuovo modificato cosi' da poter conservare l'originale da utilizzare ogni volta che gira il loop per ogni prodotto - i file modificati vengono invece cancellati dopo il loro utilizzo.

    replacements = {'descrizione_da_rimuovere':descr, 'img_da_rimuovere':copied_url_clear, 'thumb_da_rimuovere':copied_url_clear, 'Product title goes here':input_titolo_modi}

    with open("/home/blackpenny/Desktop/bot_ebay_amazon/Parte_3_bot_ebay_amaz/template_eby") as infile, open("/home/blackpenny/Desktop/bot_ebay_amazon/Parte_3_bot_ebay_amaz/template_eby_modi", 'w') as outfile:
        for line in infile:
            for src, target in replacements.iteritems():
                line = line.replace(src, target)
            outfile.write(line) 
    
#SEZIONE DETTAGLI
    
    html_btt = browser.find_element_by_id("htmlMode")
    html_btt.click()
    browser.implicitly_wait(1)
    
    edit_field = browser.find_element_by_id("rte")                                                       #Troviamo l'iframe contenente il campo di testo dove inseriamo il template.
    edit_field.click()    
    
    #PARTE DA USARE CON BROWSER FIREFOX
    
    #actionChains = ActionChains(browser)                                                                #Utilizziamo la classe ActionChains per creare una serie di movimenti (in questo caso ci serve per utilizzare il tasto destro
    #actionChains.context_click(edit_field).perform()                                                    #del mouse). Context_click equivale a premere il tasto destro.
    time.sleep(1)
    #edit_field.send_keys(Keys.DOWN, Keys.DOWN, Keys.DOWN, Keys.DOWN, Keys.ENTER)                        #Qua navighiamo con la tastiera dentro al menu del tasto destro del mouse e selezioniamo "select_all", diamo invio.
    #edit_field.send_keys(Keys.DELETE)
    
    #PARTE DA USARE CON CHROME
    
    edit_field.send_keys(Keys. CONTROL + 'a', Keys.DELETE)                                               #Qua cancelliamo tutto il testo selezionato.
                                                                       
    time.sleep(5)
       
    with open("/home/blackpenny/Desktop/bot_ebay_amazon/Parte_3_bot_ebay_amaz/template_eby_modi", 'r') as content_file:
        template_modi = content_file.read()
        #template_modi = template_modi.decode('utf-8')
        template_modi = unicode(template_modi, "UTF-8")
        template_modi = template_modi.replace(u"\u00A0", "")
    
    def chunks(s, n):                                                                                   #Definiamo e utilizziamo con il for (sotto) una funzione che prende 2500 caratteri alla volta dal file aperto sopra e li copia
        """Produce `n`-character chunks from `s`."""                                                    #nel box di testo del template su ebay.
        for start in range(0, len(s), n):                                                               #Tutto cio' per evitare che si blocchi il browser inserendo troppi caretteri tutti in una volta.
            yield s[start:start+n]

    nums = template_modi
    #nums = nums.decode('utf-8')
    for chunk in chunks(nums, 2500):
        #print chunk
        edit_field.send_keys(chunk)
       
    time.sleep(2)
    standard_label = browser.find_element_by_id("stdMode")                                              #Riclicco su "standard" dopo aver inserito l'html per vedere se così le foto vengono caricate correttamente quando pubblico
    standard_label.click()                                                                              #l'oggetto.        
    time.sleep(3)
    
#FINE SEZIONE DETTAGLI

#SEZIONE PREZZO - QUANTITA'

	#open('/home/blackpenny/Desktop/Parte_2_bot_ebay_amaz/file_1.csv', 'r') as price_row:


	#df = pd.read_csv("/home/blackpenny/Desktop/bot_ebay_amazon/Parte_2_bot_ebay_amaz/file_1.csv")

	#print df
	#saved_column = df.Descrizione_prodotto

	#print saved_column
    
    browser.find_element_by_id("storeinventory").click()												#COMPRALO SUBITO SWITCH
    time.sleep(1)
    browser.find_element_by_id("binPrice").clear()  													#PREZZO
    time.sleep(1)
    prezzo = browser.find_element_by_id("binPrice")
    prezzo.click()
    time.sleep(1)
    prezzo.send_keys(var_prezzo_buona)
    time.sleep(1)
    #browser.find_element_by_id("bestOffer").click()                                                    #Deselezioniamo "Fai una proposta d'acquisto"
    #time.sleep(1)    
    browser.find_element_by_id("quantity").clear()														#QUANTITA' OGGETTI IN VENDITA
    time.sleep(1)
    quantita_oggetti = browser.find_element_by_id("quantity")
    quantita_oggetti.click()
    quantita_oggetti.send_keys(quantity)
    browser.implicitly_wait(5) # seconds
	#time.sleep(2)
	#browser.find_element_by_xpath("//select[@id='duration']/option[@value='30']").click()				#DURATA INSERZIONE: Dobbiamo utilizzare l'xpath per poter selezionare l'attributo "option" per selezionare
																									    #la voce d'interesse dal dropdown menu
	#time.sleep(2)
	#browser.implicitly_wait(5) # seconds
	#wait2 = WebDriverWait(browser, 10)
	#wait2.until(EC.presence_of_element_located((By.ID, "paypalEmail")))
	#paypal = browser.find_element_by_xpath("//input[@name='paypalEmail']").click()
	#activeelem = browser.switch_to_active_element()
	#paypal = browser.find_element_by_id("paypalEmail")													#PAYPAL
	#paypal.click()
	#suppose "element" is an input field
	#activeelem.send_keys("redragonn@libero.it")
	#activeelem.send_keys(Keys.TAB)
	#JavascriptExecutor jsExecutor = (JavascriptExecutor) driver;
	#jsExecutor.executeScript("$(arguments[0]).change();", paypal);
	#paypal.send_keys("redragonn@libero.it")
	#time.sleep(3)
	#paypal.click()																					    #Questo secondo click dopo aver inserito il testo sembra riuscire a mantenere il testo dentro al form invece di farlo scomparire
	#browser.find_element_by_id("pmMoneyXfer").click()													#Bonifico
	#browser.find_element_by_id("pmCip").click()														#Info Bonifico
#SEZIONE CONTINUA E PAGINA FINALE

    continua = browser.find_element_by_id("aidZ1")
    continua.click()
    time.sleep(3)
    autorelist = continua = browser.find_element_by_id("autoRelist").click()
    time.sleep(1)
    pubblica = browser.find_element_by_id("aidZ18_btnLbl")
    pubblica.click()
    time.sleep(10)
    
    
    #Salviamo i cookies di questa sessione su un file per riutilizzarli in una nuova sessione al prossimo loop.
    #pickle.dump( browser.get_cookies() , open("cookies.pkl","wb"))
	
#SIAMO NELLA PAGINA DI AVVENUTA PUBBLICAZIONE DELL'INSERZIONE - DA QUA CLICCHIAMO SU "VENDI UN OGGETTO SIMILE" E RIUTILIZZIAMO L'INSERZIONE APPENA INSERITA COME BOZZA PER IL NUOVO OGGETTO.    
    
    #Salviamo in una variabile l'url dell'inserzione appena creata.
    #url_new_inserz = browser.find_element_by_xpath("//div[@class='idtTopSm']//a[@href='30']")
    
    #ogg_simile = browser.find_element_by_xpath("//li/a[text()='Vendi un oggetto simile']")             #Questo xpath funziona solo se selezioniamo "Vendi un oggetto simile" da dentro una inserzione gia' pubblicata.
    ogg_simile = browser.find_element_by_xpath("//div/a[text()='Vendi un oggetto simile']")             #Questo invece funziona dalla pagina di avvenuta pubblicazione dell'inserzione.
    ogg_simile.click()
    time.sleep(6)
    
    #Eliminiamo la stringa (presente o meno) dentro al form modello per evitare la modificazione del valore "Modello...carattere...carattere...etc" necessaria all'identificazione del corretto form da riempire quando inseriamo
    #il modello nell'inserzione.
    if counter_layer_da_reset == 1:                                                                                                 #Se uguale a 1 significa che sopra abbiamo inserito la variabile nel form con attributo
        delete_model_field = browser.find_element_by_xpath("//div[@id='TagOuterLayer_1']//input[@id='st_selval_0_1']")              #"st_selval_0_1" e quindi andiamo a cancellare usando lo stesso tag.
        delete_model_field.clear()
    else:                                                                                                                           #Altrimenti (ovvero quando e' uguale a 2) andiamo a cancellare nell'altra blocco.
        delete_model_field = browser.find_element_by_xpath("//div[@id='TagOuterLayer_2']//input[@id='st_selval_0_2']")
        delete_model_field.clear()
    
    #Salviamo la bozza per riaprirla al prossimo loop
    save_draft = continua = browser.find_element_by_id("sSaveDraftLater_Bottom")
    save_draft.click()
    time.sleep(3)
    browser.close()                                                                                     #IMPORTANTE: chiudiamo la sessione attuale alla fine di ogni loop
    
#SEZIONE ESTRAZIONE LINK

    #estraz_href = browser.find_element_by_xpath("//div[@class='idtTopSm']//div/a[text()='Vendi un oggetto simile']")
    #Select(driver.find_element_by_class_name("c3")).select_by_visible_text(state)
    
#FINE SEZIONE PAGINE    
    
    file_cnt = file_cnt +1
    #dal_sec_in_poi = dal_sec_in_poi +1
    
#FINE SEZIONE WHILE

#CANCELLAZIONE DI TUTTI I FILE CONTENENTI I DATI PER CREARE LE INSERZIONI - PER SICUREZZA (CANCELLA ANCHE LA FINAL LIST POICHE' ANCH'ESSA HA COME ESTENSIONE ".CSV" MA VERRA' RICOPIATA LA PROSSIMA VOLTA QUANDO VENGONO FATTI GIRARE
#DA CAPO TUTTI GLI SCRIPT.

filelist = [ f for f in os.listdir("/home/blackpenny/Desktop/bot_ebay_amazon/Parte_2_bot_ebay_amaz/") if f.endswith(".csv") ]
for f in filelist:
    os.remove(f)                                                                                       #Da controllare da errore

#CANCELLAZIONE DI TUTTE LE IMMAGINI SEMPRE NELLA DIRECTORY DEL SECONDO SCRIPT E IN QUELLA DEL TERZO

filelist = [ f for f in os.listdir("/home/blackpenny/Desktop/bot_ebay_amazon/Parte_2_bot_ebay_amaz/") if f.endswith(".jpg") ]
for f in filelist:
    os.remove(f)
    
filelist = [ f for f in os.listdir("/home/blackpenny/Desktop/bot_ebay_amazon/Parte_3_bot_ebay_amaz/") if f.endswith(".jpg") ]
for f in filelist:
    os.remove(f)
