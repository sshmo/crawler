import sys
import jsonlines
from elasticsearch import Elasticsearch, helpers

def main(argv):

    es = Elasticsearch()

    with jsonlines.open(f'{argv[0]}') as reader:

        index_name = f"{argv[0]}"[0:-3]
        doctype = 'games_record'
        index = 0
        es.indices.delete(index=index_name, ignore=[400, 404])
        es.indices.create(index=index_name, ignore=400)
        es.indices.put_mapping(
            index=index_name,
            doc_type=doctype,
            ignore=400,
            body={
                doctype: {
                    "properties": {
                        "name": {
                            "type": "string"
                            },
                        "genre": {
                            "type": "string",
                        },
                        "score": {
                            "type": "float"
                        },
                        "score_num": {
                            "type": "float",
                        },
                        "downloads": {
                            "type": "float",
                        },
                        "description": {
                            "type": "text",
                        },
                    }
                }
            }
        )
        for doc in reader:
            
            for key in ['score', 'score_num', 'downloads']:
                doc[key] =float(doc[key]\
                    .replace(',', '')\
                    .replace('+', '')\
                    .replace('M', '000000')\
                    .replace('Varies with device', '0'))
            
            try:
                # put document into elastic search
                es.index(index=index_name, doc_type=doctype, body=doc)

            except Exception as e:
                print('error: ' + str(e) + ' in' + str(index))
            
            index = index + 1

if __name__ == "__main__":
   main(sys.argv[1:])