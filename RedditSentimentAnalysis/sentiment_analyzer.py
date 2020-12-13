import gzip
from typing import List

import numpy as np
import pandas as pd
from pytorch_pretrained_bert.modeling import *
from torch.utils.data import TensorDataset, SequentialSampler, DataLoader
from transformers import BertTokenizer

from gather_data import ForumDataSource

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def softmax(x):
    """Utility function: Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x, axis=1)[:, None])
    return e_x / np.sum(e_x, axis=1)[:, None]


class SentimentAnalyzer(object):
    """
    Sentiment Analyzer class.
    Sets up torch, checks if GPU is available.
    Loads BERT model
    """
    def __init__(self):
        # If there's a GPU available...
        if torch.cuda.is_available():

            # Tell PyTorch to use the GPU.
            self.device = torch.device("cuda")

            print('There are %d GPU(s) available.' % torch.cuda.device_count())

            print('We will use the GPU:', torch.cuda.get_device_name(0))

        # If not...
        else:
            print('No GPU available, using the CPU instead.')
            self.device = torch.device("cpu")

        # Load the BERT tokenizer.
        print('Loading BERT tokenizer...')
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

        self.model = BertForSequenceClassification.from_pretrained('data/models/bert/', num_labels=3, cache_dir=None)

        # Put model in evaluation mode
        self.model.eval()


    def ids(self, text: List[str]):
        # Tokenize all of the sentences and map the tokens to their word IDs.
        input_ids = []
        attention_masks = []

        # For every sentence...
        for sent in text:
            # tokenizes the sentence, encodes the sentence using standard NLTK special tokens to enable processing
            # returns pytorch readable tensors
            encoded_dict = self.tokenizer.encode_plus(
                sent,  # Sentence to encode.
                add_special_tokens=True,  # Add '[CLS]' and '[SEP]'
                max_length=64,  # Pad & truncate all sentences.
                pad_to_max_length=True,
                return_attention_mask=True,  # Construct attn. masks.
                return_tensors='pt',  # Return pytorch tensors.
            )

            # Add the encoded sentence to the list
            input_ids.append(encoded_dict['input_ids'])

            # Add the attention mask, differentiates padding from non-padding in the sentence.
            attention_masks.append(encoded_dict['attention_mask'])
        return input_ids, attention_masks

    def predict(self, df: pd.DataFrame):
        """
        :param df: DataFrame containing 'text' column with posts
        :return: DataFrame containing 'sentiment' (float) and 'prediction' (integer) columns
        """
        # Report the number of sentences.
        print('Number of sentences: {:,}\n'.format(df.shape[0]))

        input_ids, attention_masks = self.ids(df.text.values)

        # Convert the lists into tensors.
        input_ids = torch.cat(input_ids, dim=0)
        attention_masks = torch.cat(attention_masks, dim=0)

        logger.info(f'input ids: {input_ids}')
        # Set the batch size.
        batch_size = 32

        # Create the DataLoader.
        prediction_data = TensorDataset(input_ids, attention_masks)
        prediction_sampler = SequentialSampler(prediction_data)
        prediction_dataloader = DataLoader(prediction_data, sampler=prediction_sampler, batch_size=batch_size)

        # Prediction on test set

        print('Predicting sentiment for {:,} posts...'.format(len(input_ids)))

        # Predict
        result = pd.DataFrame(columns=['logit','prediction','sentiment_score'])
        for batch in prediction_dataloader:
            # Add batch to GPU
            batch = tuple(t.to(self.device) for t in batch)

            # Unpack the inputs from our dataloader
            b_input_ids, b_input_mask = batch

            all_segment_ids = torch.tensor([0]*64, dtype=torch.long)

            # Telling the model not to compute or store gradients, saving memory and
            # speeding up prediction

            with torch.no_grad():
                # Forward pass, calculate logit predictions
                logits = self.model(b_input_ids, all_segment_ids, b_input_mask)
                # Normalize prediction data
                logits = softmax(np.array(logits))
                # Sentiment score = positive - negative
                sentiment_score = logits[:, 0] - logits[:, 1]
                # Choose largest index for prediction (0=positive, 1=negative, 2=neutral)
                prediction = np.squeeze(np.argmax(logits, axis=1))

                # Write result to dataframe
                batch_result = {'logit': list(logits),
                                'prediction': prediction,
                                'sentiment_score': sentiment_score}

                result = pd.concat([result, pd.DataFrame(batch_result)], ignore_index=True)

        # Turn prediction number to a word
        scores = ['positive','negative','neutral']
        result['prediction'] = result['prediction'].apply(lambda p: scores[p])
        # # Re-populate result with original text
        result['text'] = df.text.values

        # Set index as date
        result.index = pd.to_datetime(df.date)

        return result

import os


class Report(object):
    """
    Report object to contain Reddit data, plus convenience functions
    """
    def __init__(self, data: pd.DataFrame, name='report', info=dict()):
        self._name = name
        self._data = data
        self._info = info
        pass

    def save(self, directory='data/reports'):
        report_folder = os.path.join(directory, self._name)
        if not os.path.exists(report_folder):
            os.mkdir(report_folder)
        with open(os.path.join(report_folder, 'data.csv'), 'w') as f:
            f.write(self._data.to_csv())
        with open(os.path.join(report_folder, 'info.json')) as f:
            json.dump(self._info, f)

    def __str__(self):
        s = f"""
        Name: {self._name}
        Number of lines: {len(self._data)}
        """

    @property
    def data(self):
        return self._data


def load_report(filename='my_report.csv', directory='data/reports') -> Report:
    with open(os.path.join(directory, filename), 'r') as f:
        report = Report(pd.read_csv(f), filename.split('.')[0])
    return report

import glob

if __name__ == '__main__':
    """
    This example shows using data from SentimentAnalyzer to produce a graph.
    """

    # Prepare data from json file, then submit to sentiment analyzer.
    data_source = ForumDataSource()
    # Just pick the first set of comments
    filenames = glob.glob('data/reddit/*_comments_*.json.gz')
    filename = filenames[0]
    sub_name = os.path.basename(filename).split('_')[0]

    print(f'Loading data from {filename}')
    input_data: pd.DataFrame = data_source.load_from_file(filenames[0])

    sentiment_analyzer = SentimentAnalyzer()

    # Just use a subset of the records ( faster )
    r = sentiment_analyzer.predict(input_data[:400])

    # Set pandas display options (more space for data)
    pd.set_option("display.max_columns", 500)
    pd.set_option('display.width', 1000)
    print(r[['text','prediction','sentiment_score']])

    # Plot hourly mean of sentiment scores
    report = load_report()
    df = report.data
    df.index = pd.to_datetime(df.date)
    df.resample("H").mean().plot(title=f'Hourly mean sentiment for {sub_name}')