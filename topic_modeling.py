import numpy as np
import scipy.sparse as ss
import matplotlib.pyplot as plt

# Citation: "Anchored CorEx: Hierarchical Topic Modeling with Minimal Domain Knowledge"
# https://github.com/gregversteeg/corex_topic
from corextopic import corextopic as ct
from corextopic import vis_topic as vt

from sklearn.feature_extraction.text import CountVectorizer

from gather_data import ForumDataSource

import glob, os, pickle

if __name__ == '__main__':
    vectorizer = CountVectorizer(stop_words='english', max_features=20000, binary=True)
    data_source = ForumDataSource()

    filenames = glob.glob('data/reddit/*_comments_*.json.gz')
    filename = filenames[0]

    sub_name = os.path.basename(filename).split('_')[0]

    input_data = data_source.load_from_file(filename)
    # Each "Document" is a text comment
    doc_word = vectorizer.fit_transform(input_data.text)
    doc_word = ss.csr_matrix(doc_word)


    print(doc_word.shape) # n_docs x m_words

    # Get words that label the columns
    words = list(np.asarray(vectorizer.get_feature_names()))


    topic_model_filename = f'data/models/{sub_name}_topic_model.pkl'
    if os.path.exists(topic_model_filename):
        topic_model = pickle.load(open(topic_model_filename))
    else:
        # Train the CorEx topic model, with some forum-specific anchor words
        topic_model = ct.Corex(n_hidden=50, anchors=[['xmr', 'monero'],
                                                     ['btc', 'bitcoin', 'satoshi'],
                                                     ['stellar', 'xlm'],
                                                     ['ltc', 'litecoin'],
                                                     ['xrp', 'ripple'],
                                                     ['tezos'],
                                                     ['eth', 'ethereum', 'vitalik'],
                                                     ['binance', 'coinbase']])

        # Define the number of latent (hidden) topics to use.
        topic_model.fit(doc_word, words=words)
        topic_model.save(topic_model_filename)


    # Print all topics from the model
    topics = topic_model.get_topics()
    for n, topic in enumerate(topics):
        topic_words, _ = zip(*topic)
        print('{}: '.format(n) + ','.join(topic_words))


    test_sentences = [
        'i am going to sell my btc, thanks for sharing',
        'litecoin is a a decent coin, i guess'
    ]

    test_vector = vectorizer.transform(test_sentences)
    test_prediction = topic_model.predict(ss.csr_matrix(test_vector))

    for index, row in enumerate(test_prediction):
        sentence = test_sentences[index]
        prediction_index = [i for i, val in enumerate(row) if val]
        if prediction_index:
            print(prediction_index)
            if prediction_index[0] >= 0:
                topic = topics[prediction_index[0]]

                print('prediction for ' + sentence)
                print(topic)