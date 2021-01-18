import sys

import jsonlines

from elasticsearch import Elasticsearch

def main(argv):

    es = Elasticsearch()

    es.indices.delete(index=f"{argv[0]}"[0:-3], ignore=[400, 404])

    game_id = 0

    with jsonlines.open(f'{argv[0]}') as reader:
        
        for doc in reader:
            
            res = es.index(index=f"{argv[0]}"[0:-3], id =game_id , body=doc)
            print("db_index: ", f"{argv[0]}"[0:-3])
            print("id:", game_id)
            print("action:", res['result'])
            res = es.get(index=f"{argv[0]}"[0:-3], id=game_id)
            print("name:", res['_source']['name'])
            print()
            game_id += 1

if __name__ == "__main__":
   main(sys.argv[1:])