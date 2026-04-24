ANALYSEUR DE TRAFIC RÉSEAU SIMULÉ 
Université de Parakou 
Date : 20 Avril 2026 
Réalisé par : 
HOUEGNIHOUE Edegnon Casimir 
DJASSOU Marcel 
Cahier de charge 
1. Contexte et justification 
Au Bénin, l’utilisation d’Internet devient de plus en plus importante dans la vie 
quotidienne, notamment pour les inscriptions universitaires, les transferts d’argent 
mobile et le streaming de contenus en ligne. 
Cependant, il est fréquent d’observer des lenteurs du réseau, des transferts bloqués ou 
encore des services qui mettent du temps à répondre. Ces problèmes sont souvent dus à des 
congestions dans le réseau ou à une mauvaise répartition du trafic de données. 
Ce projet vise donc à concevoir un simulateur de trafic réseau afin de mieux comprendre ces 
phénomènes et d’identifier les points de blocage dans un système de communication. 
2. Objectif du projet 
L’objectif principal est de développer un programme de simulation capable de reproduire 
le fonctionnement d’un réseau informatique et d’analyser la circulation des données afin 
de : 
Comprendre le comportement des paquets dans un réseau 
Identifier les goulots d’étranglement 
Mesurer les performances du réseau 
Détecter les congestions et pertes de données 
3. Description générale du système 
Le réseau est modélisé sous forme de graphe composé de nœuds et de liens. 
Les nœuds représentent les machines (ordinateurs, routeurs, serveurs) 
Les liens représentent les connexions entre les machines 
Les paquets représentent les données envoyées dans le réseau 
Chaque lien possède une capacité maximale et chaque nœud dispose d’une file d’attente 
pour gérer les paquets reçus. Lorsque le trafic devient trop important, des ralentissements 
apparaissent et certains paquets peuvent être perdus. 
4. Fonctionnement du système 
Le simulateur fonctionne de la manière suivante : 
Création d’un réseau de nœuds interconnectés 
Envoi de paquets de données entre les nœuds 
Transmission des paquets via les liens 
Gestion des files d’attente en cas de surcharge 
Détection des congestions et analyse des performances 
5. Fonctionnalités principales 
Création d’un réseau de nœuds interconnectés 
Simulation de l’envoi et de la réception de paquets 
Gestion des files d’attente (FIFO) 
Visualisation du trafic réseau 
Détection des congestions 
6. Détection des problèmes 
Le système doit automatiquement signaler : 
Câble saturé : utilisation supérieure à 90% 
Machine débordée : file d’attente supérieure à 80% 
Perte élevée de données : plus de 5% de paquets perdus 
7. Contraintes techniques 
Langage utilisé : Python 
Programmation orientée objet obligatoire 
Respect de la modularité et de l’encapsulation 
Simulation logicielle (pas de réseau réel). 
8. Résultats attendus 
À la fin de la simulation, le programme doit afficher : 
Le nombre de paquets envoyés et reçus 
Le taux de perte de données 
Les nœuds ou liens responsables des ralentissements 
Le temps moyen de transmission des paquets. 
9. Critères de réussite 
Le projet sera considéré réussi si : 
La simulation fonctionne correctement 
Les principes de la POO sont respectés 
Les congestions sont correctement détectées
Les résultats sont clairs et exploitable 
