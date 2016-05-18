How to Run:

Vorraussetzungen:  Phyton 2.7, Graph nx, taynoud-Python-louvain
Für Graph Networkx siehe: http://networkx.github.io/download.html
Für taynoud-Python-louvain siehe SIFTA/taynoud-Python-louvain.zip oder https://bitbucket.org/taynaud/python-louvain
VorAufruf: Die Pfade in Graph/cluster.sh anpassen.   
Aufruf: sh cluster.sh 
Wichtig: Aufruf muss aus dem Ordner erfolgen in dem die mappings.xml und graph.xml des Sifta-Graphen liegen. Defaultmäßig in dem selben Ordner in dem auch die Skriptdatei liegt: SIFTA/Graph
Ergebnis: Ergebnisse werden in dem Ordner gespeichert der in cluster.sh angegeben wird.
Ungefähre Laufzeit: Bei SuppLimit 1000 und EdgeLimit 28.0 ca 3-4 Stunden.



Dokumentation:
Ziel: Wir suchen Gruppen von Apps die ein ähnliches Kommunikationsverhalten haben.

Methode: 2 geteilt: 
1.Teil: Mit frequentSetMining berechnen wir für alle AppPairs auf wie vielen Kanten die 2 Apps für jedes Paar zusammen vorkommen.
Mit diesen Informationen wird dann ein Graph erstellt. Die Knoten des Graphen sind die Apps. Zwischen 2 Apps besteht eine Kante wenn die beiden Apps auf einer Kante im Sifta-Graph liegen.
Das Gewicht der Kante ist die Anzahl der Kanten auf denen die zwei Apps zusammen liegen.
2.Teil: Auf diesem Graphen wird dann Clustering ausgeführt um Cluster von Ähnlichen Apps zu finden. Da der Graph aber zu groß für die meisten Cluster-Algorithmen wird,
wird das Clustering durch schrittweises Entfernen der Kanten mit dem kleinsten Gewicht durchgeführt. Die dadurch entstehenden Subgraphen ergeben dann die Cluster.
Auf den einen übrigen größeren Cluster wird dann noch ein extra Clusteralgorithmus ausgeführt. Das Ganze funktioniert auch, aber beim versuch den Clusteralgorithmus auf jeden Subgraphen 
auszuführen wird ein Fehler ausgegeben den ich bisher nicht entfernen konnte.

Ergebniss: Cluster von Apps die ähnliches Kommunikationsverhalten aufweisen.
