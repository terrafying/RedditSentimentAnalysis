import numpy as np
import scipy.sparse as ss
import matplotlib.pyplot as plt

from corextopic import corextopic as ct
from corextopic import vis_topic as vt # jupyter notebooks will complain matplotlib is being loaded twice

# from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer

# Transform 20 newsgroup data into a sparse matrix
from gather_data import ForumDataSource

if __name__ == '__main__':
    vectorizer = CountVectorizer(stop_words='english', max_features=20000, binary=True)
    data_source = ForumDataSource()
    sub = 'Cryptocurrency'
    input_data = data_source.load_from_file(f'data/reddit/{sub}_comments_1598932800_1596254400.json.gz')
    doc_word = vectorizer.fit_transform(input_data.text)
    doc_word = ss.csr_matrix(doc_word)


    print(doc_word.shape) # n_docs x m_words

    # Get words that label the columns (needed to extract readable topics and make anchoring easier)
    words = list(np.asarray(vectorizer.get_feature_names()))

    # Train the CorEx topic model
    topic_model = ct.Corex(n_hidden=50, anchors=[['xmr','monero'], ['btc', 'bitcoin', 'satoshi', 'nakamoto'], ['ltc', 'litecoin'], ['xrp', 'ripple'], ['tezos'], 'exchange'])  # Define the number of latent (hidden) topics to use.
    topic_model.fit(doc_word, words=words)

    # Print all topics from the CorEx topic model
    topics = topic_model.get_topics()
    for n,topic in enumerate(topics):
        topic_words,_ = zip(*topic)
        print('{}: '.format(n) + ','.join(topic_words))

    topic_model.save(f'{sub}_topic_model.pkl')

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
    # p = topic_model.predict(vectorizer.fit_transform(['this is a new sentence about bitcoin'.split()]))
    # print(p)
    # Train a second layer to the topic model
    # tm_layer2 = ct.Corex(n_hidden=10)
    # tm_layer2.fit(topic_model.labels)
    #
    # # Train a third layer to the topic model
    # tm_layer3 = ct.Corex(n_hidden=1)
    # tm_layer3.fit(tm_layer2.labels)
    #
    # # If you have graphviz installed, then you can output visualizations of the hierarchial topic model to
    # #   your current working directory.
    # # One can also create custom visualizations of the hierarchy
    # #   by properly making use of the labels attribute of each layer.
    #
    # vt.vis_hierarchy([topic_model, tm_layer2, tm_layer3], column_label=words, max_edges=200, prefix='topic-model-example')