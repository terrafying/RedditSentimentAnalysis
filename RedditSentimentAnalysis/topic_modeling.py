import numpy as np
import scipy.sparse as ss
import matplotlib.pyplot as plt
import pandas as pd

# Citation: "Anchored CorEx: Hierarchical Topic Modeling with Minimal Domain Knowledge"
# https://github.com/gregversteeg/corex_topic
from corextopic import corextopic as ct
import _pickle as cPickle
from corextopic import vis_topic as vt

from sklearn.feature_extraction.text import CountVectorizer

from gather_data import ForumDataSource

import glob, os, pickle

data_source = ForumDataSource()



class TopicModel(object):
    def __init__(self):
        self.vectorizer = CountVectorizer(stop_words='english', max_features=20000, binary=True)
        filenames = glob.glob('data/reddit/*_comments_*.json.gz')
        filename = filenames[0]
        input_data: pd.DataFrame = data_source.load_from_file(filename) #HACK: speedup
        # Each "Document" is a text comment
        self.doc_word = self.vectorizer.fit_transform(input_data.text)
        self.doc_word = ss.csr_matrix(self.doc_word)

        sub_name = os.path.basename(filename).split('_')[0]

        print(self.doc_word.shape)  # n_docs x m_words

        # Get words that label the columns
        # Encode/decode to get rid of annoying unicode characters that break the topic_model obj when saving/loading
        words = [x for x in list(np.asarray(self.vectorizer.get_feature_names()))]

        topic_model_filename = f'data/models/{sub_name}_topic_model.pkl'
        if os.path.exists(topic_model_filename):
            topic_model = cPickle.load(open(topic_model_filename, 'rb'))
        else:
            # Train the CorEx topic model, with some forum-specific anchor words
            topic_model = ct.Corex(n_hidden=25,
                                   anchors=[['xmr', 'monero'],
                                            ['btc', 'bitcoin', 'satoshi', 'nakamoto'],
                                            ['stellar', 'xlm'],
                                            ['ltc', 'litecoin'],
                                            ['xrp', 'ripple'],
                                            ['eth', 'ethereum', 'vitalik'],
                                            ['binance', 'coinbase', 'exchange'],
                                            ['electrum', 'wallet']],
                                   anchor_strength=4)

            # Define the number of latent (hidden) topics to use.
            topic_model.fit(self.doc_word, words=words)  # ,
            cPickle.dump(topic_model, open(topic_model_filename, 'wb'))
            # topic_model.save(topic_model_filename, ensure_compatibility=False)
        self.topic_model = topic_model
        # Print all topics from the model
        topics = topic_model.get_topics()
        for n, topic in enumerate(topics):
            topic_words, _ = zip(*topic)
            print('{}: '.format(n) + ','.join(topic_words))

    def predict(self, df: pd.DataFrame, sub_name='Stellar'):
        test_vector = self.vectorizer.transform(list(df.text))
        test_prediction = self.topic_model.predict(ss.csr_matrix(test_vector))
        topics = self.topic_model.get_topics()

        text = list(df.text)
        print(topics)
        t = []
        for index, row in enumerate(test_prediction):
            # sentence = text[index]
            prediction_index = [i for i, val in enumerate(row) if val]
            t.append(prediction_index)
            if prediction_index:
                print(prediction_index)
                if prediction_index[0] >= 0:
                    topic = topics[prediction_index[0]]
        return t



def test():
    test_sentences = [
        'Bitcoin is the future thanks for sharing the'.encode('utf-8', 'ignore').decode('utf-8'),
        'litecoin is a a decent coin, i guess'.encode('utf-8', 'ignore').decode('utf-8')
    ]

    tm = TopicModel()

    # df = pd.DataFrame()
    # df['text'] = test_sentences
    for p in tm.predict(pd.DataFrame(test_sentences)):
        print(p)

if __name__ == '__main__':
    test()