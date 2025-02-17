��          �               �     �  a   �  l   �     h  v   p  W   �  
   ?     J     h  -   �  :   �  '   �  p        �     �  5   �  (   �  +     -   :     h     y     �  �  �     �  d   �  �   �     t  �   |  V   	  
   _	     j	  #   �	  >   �	  L   �	  (   :
  �   c
      �
       O   &  (   v  +   �  -   �     �     
        **Backend** :doc:`See here for how to enable DEBUG logging </how-to/troubleshooting/enabling-debug-logging>`. Any processes listed, should have the status ``RUNNING``. Stale or crashed processes can be restarted with:: Backend By default, only errors are logged. You can enable DEBUG logging which will make the backend log greatly more verbose. DSMR-reader technically consists of these processes and they are watched by Supervisor: Datalogger Each has its own log file(s): Hosts the GUI of DSMR-reader Local datalogger reading telegrams (if used). Most important process, handles all background processing. Or to restart them all simultaneously:: The logfiles may be stale due to rotation. To see all logs for a process, try tailing a wildcard pattern, e.g.:: Troubleshooting: Log files Webinterface You can view the status of all processes by running:: ``/var/log/supervisor/dsmr_backend.log`` ``/var/log/supervisor/dsmr_datalogger.log`` ``/var/log/supervisor/dsmr_webinterface.log`` ``dsmr_backend`` ``dsmr_datalogger`` ``dsmr_webinterface`` Project-Id-Version:  DSMR-reader
Report-Msgid-Bugs-To: Dennis Siemensma <github@dennissiemensma.nl>
POT-Creation-Date: 2022-06-07 21:23+0000
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: Dennis Siemensma <github@dennissiemensma.nl>
Language: nl
Language-Team: Dennis Siemensma <github@dennissiemensma.nl>
Plural-Forms: nplurals=2; plural=(n != 1);
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 2.10.1
 **Backend** :doc:`Bekijk hier hoe je DEBUG-logging inschakelt </how-to/troubleshooting/enabling-debug-logging>`. Elk proces dat getoond wordt zou de status ``RUNNING`` moeten hebben. Hangende of gecrashde processen kunnen herstart worden met:: Backend Standaard worden alleen fouten gelogd. Je kunt DEBUG-logging inschakelen waardoor de "backend" aanzienlijk meer achtergrondinformatie logt. DSMR-reader bestaat technisch uit deze processen en ze worden beheerd door Supervisor: Datalogger Elk heeft eigen logbestand(en): Draait de interface van DSMR-reader Lokale datalogger voor uitlezen telegrammen (indien gebruikt). Meest belangrijke process, verantwoordelijk voor alle achtergrondverwerking. Of herstart ze allemaal tegelijkertijd:: De logbestanden kunnen blijven hangen wegens rotatie. Probeer te tailen op een wildcard-patroon om alles logs van een proces te zien. Bijvoorbeeld:: Hulp bij problemen: Logbestanden Webinterface Je kunt de status van alle processen bekijken door het volgende uit te voeren:: ``/var/log/supervisor/dsmr_backend.log`` ``/var/log/supervisor/dsmr_datalogger.log`` ``/var/log/supervisor/dsmr_webinterface.log`` ``dsmr_backend`` ``dsmr_datalogger`` ``dsmr_webinterface`` 