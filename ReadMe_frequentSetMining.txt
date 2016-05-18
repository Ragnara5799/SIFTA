How To Run:
Vorraussetzung: Python 2.7
VorAufruf: Die Pfade in Graph/frequentSetMining.sh anpassen.
Aufruf: sh frequentSetMining.sh
Wichtig: Aufruf muss aus dem Ordner erfolgen in dem die mappings.xml und graph.xml des Sifta-Graphen liegen. Defaultmäßig in dem selben Ordner in dem auch die Skriptdatei liegt: SIFTA/Graph
Ergebnis: Ergebnisse werden in dem Ordner gespeichert der in frequentSetMining.sh angegeben wird.
Benennung der Dateien: removedAppCombosEdgeBasedX_Y : X steht für die das Supportlimit. Y steht für die Schrittzahl des Algorithmus und die Länge der AppCombos.
Laufzeit: Starkt abhängig von der Wahl des Supportlimits: Bei SuppLimit: 50000 und SUPPLIMITDIFEDGE = 150: bis Schritt 5: Dauer ca. zweieinhalb Tage


Dokumentation:

Ziel: Gruppen von Apps finden die kooperieren.

Methode: Frequent Set Mining.

Pseudocode:
Eingabe SuppLimit und SuppLimitDifEdge
Berechne firstSupportSet() // für jede App: Berechne die Anzahl der Flüsse auf denen diese App vorhanden ist.
Set interestingApps = Alle Apps in firstSupportSet() deren Wert größer als SupportLimit ist.
Set AppCombos =  Alle Kombinationen von Apps aus interestingApps.
while(AppCombos != {}){
	set suppSet = Für jede AppCombo: Berechne die Anzahl der Flüsse auf denen die AppCombo vorkommt (bei Option: "sameFlowDifferentEdges" müssen die einzelnen Apps auf verschiedenen
        Kanten liegen)
        entferne alle AppCombos deren Wert kleiner als das SuppLimit ist. (Bei Option "sameFlowDifferentEdges": kleiner als SuppLimitDifEdge)
        Speichere Zwischenschritt.
        AppCombos: Berechne alle Kombinationen aus AppCombos und interestingApps 
}

Ergebnis:  Wir haben zwei Optionen: "sameFlowDifferentEdges" und "sameFlow"
           Die Ergebnisse aus "sameFlow" sind nicht aufschlussreich da man nicht weiß ob die Apps aus den AppCombos auf den selben Kanten liegen oder nicht.
           Die Ergebnisse aus "sameFlowDifferentEdges" geben Kombinationen von Apps zurück die kooperieren um Leaks zu erzeugen.      
