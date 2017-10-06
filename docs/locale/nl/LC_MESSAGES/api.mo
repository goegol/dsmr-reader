��    ^           �      �  3   �     -     K  �   `     	     '	     8	     I	  [   b	  Y   �	  p   
  s   �
  n   �
  q   l  r   �  �   Q            �   "     �  �   �    >  =   P     �  I   �  G   �  
   ?     J     R      q  #   �     �  -   �  (   �  -     %   D  &   j     �  
   �  �   �  �   A     �  q   �  t   S  z   �  2   C     v  f   }  B   �  m   '  Z   �  >   �  �   /  -   �  p   �  X   f  v   �  �   6  �   �     k     o     �     �     �  |   �  �   O     �     �       $   (     M     j  f   �  K   �  l   ;  %   �  t   �  s   C  b   �  i     �   �  �     l   �  c      s   v   �   �      l!  Y   �!  Y   F"  Y   �"  x   �"  }   s#  |   �#  S  n$  /   �%     �%     &  �   &     �&     �&     '     '  [   0'  `   �'  k   �'  k   Y(  n   �(  m   4)  X   �)  �   �)     �*     �*  �   �*     p+  �   ~+  %  ,  @   E-     �-  Z   �-  R   �-     Q.  	   a.  #   k.  '   �.  <   �.     �.  0    /  *   1/  0   \/  (   �/  )   �/     �/  
   �/  �   �/  �   �0     S1  n   k1  n   �1  v   I2  9   �2     �2  l   3  H   n3  z   �3  e   24  N   �4  �   �4  /   u5  k   �5  b   6  �   t6  �   7  �   �7     p8     t8     �8     �8     �8  z   �8  �   J9     �9     :     :  $   6:     [:     x:  �   �:  X   ;  z   p;  %   �;  n   <  n   �<  K   �<  X   ;=  �   �=  �   >  �   �>  d   (?  �   �?  �   '@  �   �@  ]   uA  ]   �A  ]   1B  v   �B  �   C  �   �C     7          1   &                     K   /   \       T   L       3   S   H      $   6       %   ^   ;             '   *      #   I   N   U   [   "       F   >   D   0         Y   .      P   Z   =              J                        ]       E       B   (   M   X         4   A   8               R       V           5              +   G             
                )   9   2   	   @           ?   :   Q   O                 W      <       !           -   C             ,       (using the ``requests`` library available on PIP):: **Data structure returned**:: **Data** to insert:: **Please note**: Readings are processed simultaneously. Inserting readings **retroactively** might result in undesired results due to the data processing, which is always reading ahead. **Result**:: **Supervisor**:: **VirtualEnv**:: **[R]** = Required field **[R]** ``electricity_currently_delivered`` (*float*) - Current electricity delivered in kW **[R]** ``electricity_currently_returned`` (*float*) - Current electricity returned in kW **[R]** ``electricity_delivered_1`` (*float*) - Meter position stating electricity delivered (low tariff) in kWh **[R]** ``electricity_delivered_2`` (*float*) - Meter position stating electricity delivered (normal tariff) in kWh **[R]** ``electricity_returned_1`` (*float*) - Meter position stating electricity returned (low tariff) in kWh **[R]** ``electricity_returned_2`` (*float*) - Meter position stating electricity returned (normal tariff) in kWh **[R]** ``timestamp`` (*datetime*) - Timestamp indicating when the reading was taken, according to the smart meter **datetime format** = ``YYYY-MM-DDThh:mm[:ss][+HH:MM|-HH:MM|Z]``, i.e.: ``2017-01-01T12:00:00+01`` (CET), ``2017-04-15T12:00:00+02`` (CEST) or ``2017-04-15T100:00:00Z`` (UTC). API All parameters are optional. All the :ref:`generic DSMRREADING examples <generic-examples-anchor>` apply here as well, since only the ``timestamp`` field differs. Authenticating Below is a more detailed script you can use to run via Supervisor. It will send telegrams to one or multiple instances of DSMR-reader. Besides allowing the API to listen for requests, you will also need send your API key with each request. The API key can be found on the same page as in the screenshot above. The application generates one for you initially, but feel free to alter the API key when required. Client file in ``/home/dsmr/dsmr_datalogger_api_client.py``:: Configuration & authentication Creates a reading from direct values, omitting the need for the telegram. Don't forget to insert your own configuration below in ``API_SERVERS``. Enable API Example Example 1 - Fetch all readings Example 2 - Fetch latest reading Example 3 - Fetch readings by month Examples Full path: ``/api/v1/datalogger/dsmrreading`` Full path: ``/api/v2/consumption/today`` Full path: ``/api/v2/datalogger/dsmrreading`` Full path: ``/api/v2/statistics/day`` Full path: ``/api/v2/statistics/hour`` None. Parameters Please note that all timestamps **returned** are in **UTC (CET -1 / CEST -2)**. This is indicated as well by the timestamps ending with a 'Z' (Zulu timezone). Please note that the datalogger may interfere. If your stats are not correctly after regenerating, try it again while having your datalogger disabled. Response Retrieves any **aggregated day statistics**. Please note that these are generated a few hours **after midnight**. Retrieves any **aggregated hourly statistics**. Please note that these are generated a few hours **after midnight**. Retrieves any readings stored. The readings are either constructed from incoming telegrams or were created using this API. Returns the consumption of the current day so far. Script Since ``DSMR-reader v1.6`` this call now returns ``HTTP 201`` instead of ``HTTP 200`` when successful. Supervisor config in ``/etc/supervisor/conf.d/dsmr-client.conf``:: The API is disabled by default in the application. You may enable it in your configuration or admin settings. The application has an API allowing you to insert/create readings and retrieve statistics. The serial connection in this example is based on ``DSMR v4``. Therefor inserting historic data might require you to delete all aggregated data using the ``./manage.py dsmr_backend_delete_aggregated_data`` command. These API calls are available since ``v1.7``. This allows you to insert a raw telegram, into the application as if it was read locally using the serial cable. This demonstrates how to fetch all readings stored, without using any of the parameters. This demonstrates how to fetch all readings within a month. We limit the search by specifying the month start and end. This demonstrates how to fetch the latest reading stored. Therefor we request all readings, sort them descending by timestamp and limit the result to only one. This will process all readings again, from the very first start, and aggregate them (and **will** take a long time depending on your reading count). URI Using **cURL** (commandline):: Using **requests** (Python):: Using ``cURL``:: Using ``requests``:: You should pass it in the header of every API call. The header should be defined as ``X-AUTHKEY``. See below for an example. You will still require the ``dsmr`` user and VirtualEnv, :doc:`as discussed in the install guide<installation>` in **chapters 3 and 6**! [API v1] Remote datalogger [API v2] RESTful API ``GET`` - ``consumption/today`` ``GET`` - ``datalogger/dsmrreading`` ``GET`` - ``statistics/day`` ``GET`` - ``statistics/hour`` ``HTTP 200`` on success. Body contains the result(s) in JSON format. Any other status code on failure. ``HTTP 201`` on success, with empty body. Any other status code on failure. ``HTTP 201`` on success. Body contains the reading created in JSON format. Any other status code on failure. ``POST`` - ``datalogger/dsmrreading`` ``day__gte`` (*date*) - Limits the result to any statistics having their date **higher or equal** to this parameter. ``day__lte`` (*date*) - Limits the result to any statistics having their date **lower or equal** to this parameter. ``extra_device_delivered`` (*float*) - Last value read from the extra device connected (gas meter) ``extra_device_timestamp`` (*datetime*) - Last timestamp read from the extra device connected (gas meter) ``hour_start__gte`` (*datetime*) - Limits the result to any statistics having their datetime (hour start) **higher or equal** to this parameter. ``hour_start__lte`` (*datetime*) - Limits the result to any statistics having their datetime (hour start) **lower or equal** to this parameter. ``limit`` (*integer*) - Limits the resultset size returned. Omit for maintaining the default limit (**25**). ``offset`` (*integer*) - When iterating large resultsets, the offset determines the starting point. ``ordering`` (*string*) - Use ``-day`` to sort **descending**. Omit or use ``day`` to sort **ascending** (default). ``ordering`` (*string*) - Use ``-hour_start`` to sort **descending**. Omit or use ``hour_start`` to sort **ascending** (default). ``ordering`` (*string*) - Use ``-timestamp`` to sort **descending**. Omit or use ``timestamp`` to sort **ascending** (default). ``phase_currently_delivered_l1`` (*float*) - Current electricity used by phase L1 (in kW) ``phase_currently_delivered_l2`` (*float*) - Current electricity used by phase L2 (in kW) ``phase_currently_delivered_l3`` (*float*) - Current electricity used by phase L3 (in kW) ``telegram`` (*string*) - The raw telegram string containing all linefeeds ``\n``, and carriage returns ``\r``, as well! ``timestamp__gte`` (*datetime*) - Limits the result to any readings having a timestamp **higher or equal** to this parameter. ``timestamp__lte`` (*datetime*) - Limits the result to any readings having a timestamp **lower or equal** to this parameter. Project-Id-Version: DSMR Reader v1.x
Report-Msgid-Bugs-To: Dennis Siemensma <github@dennissiemensma.nl>
Last-Translator: Dennis Siemensma <github@dennissiemensma.nl>
Language-Team: 
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 2.3.4
Language: nl
X-Generator: Poedit 1.8.7.1
 (met de ``requests`` tool beschikbaar in PIP):: **Datastructuur**:: **Data** te verwerken:: **Let op**: Metingen worden gelijktijdig verwerkt. Wanneer je metingen met **terugwerkende kracht** toevoegt, kan dit leiden tot ongewenste resultaten in de dataverwerking, die altijd vooruit werkt. **Resultaat**:: **Supervisor**:: **VirtualEnv**:: **[R]** = Verplicht veld **[R]** ``electricity_currently_delivered`` (*float*) - Huidig elektriciteitsverbruik in kW **[R]** ``electricity_currently_returned`` (*float*) - Huidige teruglevering elektriciteit in kW **[R]** ``electricity_delivered_1`` (*float*) - Meterstand van verbruikte elektriciteit (laagtarief) in kWh **[R]** ``electricity_delivered_2`` (*float*) - Meterstand van verbruikte elektriciteit (piektarief) in kWh **[R]** ``electricity_returned_1`` (*float*) - Meterstand van teruggeleverde elektriciteit (laagtarief) in kWh **[R]** ``electricity_returned_2`` (*float*) -Meterstand van teruggeleverde elektriciteit (piektarief) in kWh **[R]** ``timestamp`` (*datetime*) - Moment waarop de meting is gedaan, volgens de meter **datetime formaat** = ``YYYY-MM-DDThh:mm[:ss][+HH:MM|-HH:MM|Z]``, bijvoorbeeld: ``2017-01-01T12:00:00+01`` (CET), ``2017-04-15T12:00:00+02`` (CEST) of ``2017-04-15T100:00:00Z`` (UTC). API Alle parameters zijn optioneel. Alle :ref:`generieke DSMRREADING voorbeelden <generic-examples-anchor>` zijn hier tevens van toepassing, gezien alleen het ``timestamp`` field afwijkt. Authenticatie Hieronder staat een uitgebreider script die je via Supervisor kan draaien. Dit script stuurt telegrammen door naar één of meerdere instanties van DSMR-reader. Naast het inschakelen van de API, zul je bij elke request de API-key moeten meesturen. De API-key kun je inzien op dezelfde pagina's als die in de screenshot hierboven. De applicatie maakt standaard een API-key voor je aan. Deze kun je eventueel zelf wijzigen wanneer daar de behoefte voor is. Client bestand in ``/home/dsmr/dsmr_datalogger_api_client.py``:: Configuratie & authenticatie Maakt een meting aan zonder het telegram op te sturen, op basis van de meegegeven waarden. Vergeet niet om je eigen configuratie hieronder in te stellen in  ``API_SERVERS``. API inschakelen Voorbeeld Voorbeeld 1 - Haal alle metingen op Voorbeeld 2 - Haal de laatste meting op Voorbeeld 3 - Haal alle metingen van een specifieke maand op Voorbeelden Volledig pad: ``/api/v1/datalogger/dsmrreading`` Volledig pad:``/api/v2/consumption/today`` Volledig pad: ``/api/v2/datalogger/dsmrreading`` Volledig pad: ``/api/v2/statistics/day`` Volledig pad: ``/api/v2/statistics/hour`` Geen. Parameters Let op dat alle **teruggegeven** (datum)tijdstippen in **UTC (CET -1 / CEST -2)**-formaat zijn. Dit is ook te zien aan elke instantie die eindigt met 'Z' (Zulu tijdzone). N.B.: De datalogger kan soms in de weg zitten. Mocht blijken dat de statistieken niet kloppen na hergenereren, dan kun je het eventueel nogmaals proberen de datalogger uitgeschakeld. Respons (van de server) Haalt **geaggregeerde dagstatistieken** op. Deze worden elke dag een paar uur **ná middernacht** gegenereerd. Haalt **geaggregeerde uurstatistieken** op. Deze worden elke dag een paar uur **ná middernacht** gegenereerd. Haalt opgeslagen metingen op. De metingen komen ofwel voort uit telegrammen of zijn handmatig aangemaakt via deze API. Geeft het verbruik (tot nu toe) van de huidige dag terug. Script Sinds ``DSMR-reader v1.6`` geeft deze call ``HTTP 201`` terug in plaats van ``HTTP 200``, wanneer succesvol. Supervisor configuratie in ``/etc/supervisor/conf.d/dsmr-client.conf``:: Standaard is de API in de applicatie uitgeschakeld. Je kunt deze inschakelen in het configuratiescherm of beheerderpaneel. De applicatie heeft een API waarmee metingen kunt aanmaken/opvragen en diverse statistieken uitlezen. De seriële verbinding in het voorbeeld hieronder is gebaseerd op ``DSMR v4``. Daarom kan het nodig zijn dat je alle geaggregeerde gegevens verwijdert met het ``./manage.py dsmr_backend_delete_aggregated_data`` commando. Deze API-calls zijn beschikbaar sinds ``v1.7``. Dit staat je toe om een ruwe telegram aan de applicatie door te geven, wanneer je deze op afstand uitleest. Dit toont hoe je alle opgeslagen metingen kunt ophalen, zonder gebruik te maken van de parameters. Dit toont hoe je alle metingen van één maand kan ophalen. Hiervoor beperken we de zoekopdracht tot het begin en einde van de betreffende maand. Dit laat zien hoe je de laatst opgeslagen meting ophaalt. Hiervoor vragen we alle metingen op, sorteren deze aflopend op tijdstip en beperken het resultaat tot één. Dit zorgt ervoor dat de applicatie alle metingen opnieuw inleest, helemaal vanaf het begin, en ze opnieuw aggregeert. Dit **zal** lang duren, afhankelijk van hoeveel metingen er opgeslagen zijn. URI Met **cURL** (commandline):: Met ``requests`` (Python):: Met ``cURL``:: Met ``requests``:: Je moet deze gebruiken voor elke API call die je uitvoert. De header heet ``X-AUTHKEY``. Zie hieronder voor een voorbeeld. Je hebt nog steeds de ``dsmr`` gebruiker en VirtualEnv nodig, :doc:`zoals besproken in de installatiehandleiding<installation>` in **hoofdstukken 3 en 6**! [API v1] Remote datalogger [API v2] RESTful API ``GET`` - ``consumption/today`` ``GET`` - ``datalogger/dsmrreading`` ``GET`` - ``statistics/day`` ``GET`` - ``statistics/hour`` ``HTTP 200`` wanneer succesvol. Het antwoord bevat de resultaten in JSON-formaat. Geeft elke andere status code terug bij falen. ``HTTP 201`` wanneer succesvol, met een lege respons. Elke andere status code bij falen. ``HTTP 201`` wanneer succesvol. Elke andere status code bij falen. De respons bevat de aangemaakte meting in JSON-formaat. ``POST`` - ``datalogger/dsmrreading`` ``day__gte`` (*date*) - Beperkt het resultaat tot alle datums die **hoger of gelijk zijn aan** deze parameter. ``day__lte`` (*date*) - Beperkt het resultaat tot alle datums die **lager of gelijk zijn aan** deze parameter. ``extra_device_delivered`` (*float*) - Meterstand van de externe (gas)meter ``extra_device_timestamp`` (*datetime*) - Tijdstip van meting door de externe (gas)meter ``hour_start__gte`` (*datetime*) - Beperkt het resultaat tot alle (datum)tijdstippen die **hoger of gelijk zijn aan** deze parameter. ``hour_start__lte`` (*datetime*) - Beperkt het resultaat tot alle (datum)tijdstippen die **lager of gelijk zijn aan** deze parameter. ``limit`` (*integer*) - Beperkt het aantal resultaten dat teruggegeven wordt. Laat deze parameter weg voor de standaardwaarde (**25**). ``offset`` (*integer*) - Bij het doorlopen van vele resultaten kun je hiermee het startpunt bepalen. ``ordering`` (*string*) - Gebruik ``-day`` om **aflopend** te sorteren. Laat de parameter weg of gebruik ``day`` om **oplopend** te sorteren (standaard). ``ordering`` (*string*) - Gebruik ``-hour_start`` om **aflopend** te sorteren. Laat de parameter weg of gebruik ``hour_start`` om **oplopend** te sorteren (standaard). ``ordering`` (*string*) - Gebruik ``-timestamp`` om **aflopend** te sorteren. Laat de parameter weg of gebruik ``timestamp`` om **oplopend** te sorteren (standaard). ``phase_currently_delivered_l1`` (*float*) - Huidig elektriciteitsverbruik in fase L1 (in kW) ``phase_currently_delivered_l2`` (*float*) - Huidig elektriciteitsverbruik in fase L2 (in kW) ``phase_currently_delivered_l3`` (*float*) - Huidig elektriciteitsverbruik in fase L3 (in kW) ``telegram`` (*string*)  - De ruwe telegram tekenreeks inclusief alle regeleindes ``\n`` en 'carriage returns' ``\r``. ``timestamp__gte`` (*datetime*) - Beperkt het resultaat tot alle (datum)tijdstippen die **hoger of gelijk zijn aan** deze parameter. ``timestamp__lte`` (*datetime*) - Beperkt het resultaat tot alle (datum)tijdstippen die **lager of gelijk zijn aan** deze parameter. 