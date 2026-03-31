# Hemoglobiinin tunnistus demo
Optiset mittaukset Senno-laitteella ja data-analyysi neuroverkon avulla -opinnäyte työn hemoglobiinin tunnistus demo. Kansiossa kaikki tarvittava softa demon testausta varten. Neuroverkkojen koulutuksesta ja datasta tarkemmin [täällä](https://github.com/martrahu/Oppari/tree/main/21.01.2026).

**Senno_main** - Aja tämä

**default_ABCD_red_blue_green_yellow_decimate4_hemo** - Sennon configuraatiotiedosto

**raw-kansio** - Hb mittaukset. Vahvin konsentraatio 1mg/ml, josta tehty laimennukset: 0.5mg/ml, 0.25mg/ml ja 0.125mg/ml. Lisäksi vesimittaukset. Yhteensä 5 eri labelia.

**mittaukset_todentamista_varten_25_2_2026** - koulutusdatan ulkopuolista mittausdataa.

**malliX.keras** -  valmiit mallit 1-4

**inference.py** - kutsuu kansiossa olevaa mallia. Funktio palauttaa mallien 1 ja 4 ennusteet pääohjelmalle, jossa mallin 4 ennuste näkyvissä käyttöliittymän predictio-kentässä ja mallin 1 ennuste kommentoitu piiloon.

## mallien koulutustiedostot
ajetaan erikseen.

**dnn1.py** - Luokittelu DNN, labelit 0-4, jossa 0 on vesi ja 4 Hb100. Päästään val_acc 1,0 tasoon 15 epochilla. Verkon kouluttamisessa käytetty 6 synteettista featurea (kts edellä olevat kuvat). Koulutettu malli tallennettu nimellä 'malli1.keras'.

**dnn2.py** - Regressio DNN. Kouluttamisessa käytetty konsentraatiota Hb0 (=vesi), Hb12.5 ja Hb100 (vahvuudet 25 ja 50 jätetty pois). Malli tallennettu nimellä 'malli2.keras'. Antaa arvon väliltä 0-100 (=mitä luulee olevan liuoksen konsentraatio).

**dnn3.py** - Luokittelu DNN joka ennustaa onko mittaus tehty purkilla A vai B. Optimaaliseen verkkorakenteen löytämiseen käytin KerasTuneria, paras tulos saadaan 5 kerroksella jossa jokaisessa 20 neuronia. Ottaen huomioon että labeleita on vaan kaksi niin todennäköisesti neuroverkko on löytänyt vaan kohinaa eikä purkilla ole ollut vaikutusta mittaustulokseen. Myös opiskelukäyrässä alkaa n 60 epochin kohdalla tapahtumaan ylioppimista. Malli tallennettu nimellä 'malli3.keras'.

**dnn4.py** Regressio DNN. Kouluttamisessa käytetty konsentraatiota kaikkia raw-kansion väkevyyksiä. Malli tallennettu nimellä 'malli4.keras'. Antaa arvon väliltä 0-100 (=mitä luulee olevan liuoksen konsentraatio).


