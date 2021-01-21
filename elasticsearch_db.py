import sys
import jsonlines
from elasticsearch import Elasticsearch, helpers
import nltk
import string

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
                        "words": {
                            "type": "text",
                        },
                    }
                }
            }
        )

        doc_words = {}
        for doc in reader:

            for key in ['score', 'score_num', 'downloads']:
                doc[key] = float(doc[key]
                                 .replace(',', '')
                                 .replace('+', '')
                                 .replace('M', '000000')
                                 .replace('Varies with device', '0'))

            # create list of words
            doc_words[doc['name']] = tokenize(doc['description'])

            try:
                # put document into elastic search
                es.index(index=index_name, doc_type=doctype, body=doc)

            except Exception as e:
                print('error: ' + str(e) + ' in' + str(index))

            index = index + 1

        doc_tfs = compute_tfs(doc_words)

        index_name = f"{argv[0]}"[0:-3] + "_words"
        doctype = 'games_words_record'
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
                        "word": {
                            "type": "string"
                        },
                        "count": {
                            "type": "float"
                        },
                    }
                }
            }
        )

        doc = {}
        for word in doc_tfs:

            if doc_tfs[word] < 2:
                continue

            doc['word'] = word
            doc['count'] = doc_tfs[word]

            try:
                # put document into elastic search
                es.index(index=index_name, doc_type=doctype, body=doc)

            except Exception as e:
                print('error: ' + str(e) + ' in' + str(index))

            index = index + 1


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """

    # Initialize the list of words, punctuation and stopwords
    keywords = []
    punctuations_list = string.punctuation
    stopwords_list = nltk.corpus.stopwords.words("english")

    # Make a naive tokenized copy of the `document`
    naive_list = nltk.word_tokenize(document)

    for item in naive_list:

        # Ignore punctuations or stopwords
        if (item in punctuations_list) or (item in stopwords_list) or (len(item) < 4):
            continue

        # Add document by coverting all words to lowercase
        keywords.append(item.lower())

    return keywords


def compute_tfs(descriptions):
    """
    Given a dictionary of `games` that maps names of games to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the games should be in the
    resulting dictionary.
    """

    # Initialize a dictionary that maps words to their IDF values.
    tf_dict = {}

    # Loop over game descriptions
    for game_name in descriptions:

        # Loop over words in each document
        for word in descriptions[game_name]:

            # continue if the word was already processed in
            # previous documents
            if word in tf_dict:
                continue

            # Count number of documents that contain the word
            word_count = 0
            for game_name in descriptions:
                if word in descriptions[game_name]:
                    word_count += 1

            # add tf_score to tf_dict
            tf_dict[word] = word_count

    return tf_dict


if __name__ == "__main__":
    main(sys.argv[1:])
