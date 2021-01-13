# Game Crawler

Write a crawler to extract game attributes (Max 300 games) and store them in Elasticsearch.


## Specifications

* The data should be extracted from the following link (two layers):

[Top grossing games](https://play.google.com/store/apps/collection/cluster?clp=0g4YChYKEHRvcGdyb3NzaW5nX0dBTUUQBxgD:S:ANO1ljLhYwQ&gsr=ChvSDhgKFgoQdG9wZ3Jvc3NpbmdfR0FNRRAHGAM%3D:S:ANO1ljIKta8)

The following attributes are of intrest:
1. Game name
2. Game genere
3. Number of downloads
4. Score value and number
5. Description

* Use Kibana for data visualization and relate the number of downloads to game score.

* Visualize the words frequency in game description using Kibana
