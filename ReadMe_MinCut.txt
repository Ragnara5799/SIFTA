How to Run:
Vorraussetzungen:  Phyton 2.7
VorAufruf: Die Pfade in Graph/minCut.sh anpassen.   
Aufruf: sh minCut.sh 
Wichtig: Aufruf muss aus dem Ordner erfolgen in dem die mappings.xml und graph.xml des Sifta-Graphen liegen. Defaultmäßig in dem selben Ordner in dem auch die Skriptdatei liegt: SIFTA/Graph
Ergebnis: Ergebnisse werden in dem Ordner gespeichert der in minCut.sh angegeben wird.
Ungefähre Laufzeit: Bei Ziel von 0,6 ca. 3-4 Stunden 


Dokumentation: 

Ziel: Suche die kleinstmögliche Menge von Apps, die man entfernen muss um alle Leaks von privaten Daten zu verhindern. (Alle Flüsse im SIFTA-Graph trennen)

Methode:  MinCut Algorithmus, genauer angepasster Ford Fulkerson Algorithmus.

Pseudocode:
Gegeben: Graph G mit Quelle q und Senke s, Menge aller Kanten K,
Menge aller Knoten N
Set A = (); // A ist die Menge aller Entfernten Apps
while(es existiert ein Pfad p von q nach s)
    Bestimme ein p;
    Bestimme pk // pk ist die Kante mit dem kleinsten Gewicht
                // Gewicht einer Kante = |k \ A |
    Füge alle Apps aus pk zu A hinzu und lösche pk.
End
Return A  // min cut von G

Ergebnis: Um alle Leaks zu entfernen muss ein großteil aller Apps entfernt werden. Außerdem ist das Ergebniss nicht immer eindeutig.
           Das liegt an den Abhängigkeiten zwischen den Kanten. 
           Beispiel: Wir haben 3 Pfade 1,2 und 3. 
           Auf 1 hat die Kante mit niedrigestem Gewicht die Apps A und B. 
           Auf 2 gibt es 2 Kanten mit dem kleinsten Gewicht: Erste Kante mit Apps A,B und die 2. Kante mit den Apps A,C
           Auf 3 hat die Kante mit niedrigstem Gewicht die Apps A,B,D.
           Um alle Pfade zu unterbrechen reicht es die Apps A,B,D zu entfernen. Wenn der algorithmus aber zuerst Pfad 2 findet und sich entscheidet A und C zu entfernen,
           hat man plötzlich das Ergebniss dass A,B,C,D entfernt werden müssen.
           Dieses Problem tritt auch beim SIFTA Graphen aus.

Neues Ziel: Suche die kleinstmögliche Menge von Apps, die man entfernen muss um möglichst viele Leaks von privaten Daten zu verhindern.

Methode: partieller MinCut.

Pseudocode für partiellen MinCut: 
PartialMinCut(graph, allFlows, goal):
//graph: Der Graph dessen Flüsse unterbrochen werden sollen.
//allFlows: Alle Flüsse im Graphen graph
//goal: die mindestMenge(in %) von Flüssen die unterbrochen werden soll
    appsToRemove = {}
    cuttingApps = Berechne eine Liste aller Apps die bei ihrer Entfernung mindestens einen Fluss unterbrechen.
    while cuttingApps != {} && goal nicht erreicht{
        nextApp = Wähle die App aus cuttingApps, die bei ihrere Entfernung die meisten Flüsse unterbricht
        appsToRemove.add(nextApp)
        entferne alle Flüsse aus allFlows die bei der Entfernung von nextApp unterbrochen werden.
        cuttingApps = Berechne die Liste aller Apps die bei ihrer Entfernung mindestens einen Fluss unterbrechen mit den übrigen Flüssen aus allFlows
    }
    return appsToRemove;

Einschränkung: Der Algorithmus stoppt nicht nur wenn das Ziel erreicht wurde, sondern auch wenn es keine Apps mehr gibt die, wenn man sie entfernt mindestens einen Fluss trennen.

Ergebnis: Um einen Großteil der Leaks zu verhindern müssen nur wenige Apps entfernt werden.

