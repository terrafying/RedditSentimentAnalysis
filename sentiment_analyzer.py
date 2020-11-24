import gzip
from typing import List

import numpy as np
import pandas as pd
from pytorch_pretrained_bert.modeling import *
from torch.utils.data import TensorDataset, SequentialSampler, DataLoader
from transformers import BertTokenizer

from .gather_data import ForumDataSource

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
        # Tokenize all of the sentences and map the tokens to thier word IDs.
        input_ids = []
        attention_masks = []

        # For every sentence...
        for sent in text:
            # `encode_plus` will:
            #   (1) Tokenize the sentence.
            #   (2) Prepend the `[CLS]` token to the start.
            #   (3) Append the `[SEP]` token to the end.
            #   (4) Map tokens to their IDs.
            #   (5) Pad or truncate the sentence to `max_length`
            #   (6) Create attention masks for [PAD] tokens.
            encoded_dict = self.tokenizer.encode_plus(
                sent,  # Sentence to encode.
                add_special_tokens=True,  # Add '[CLS]' and '[SEP]'
                max_length=64,  # Pad & truncate all sentences.
                pad_to_max_length=True,
                return_attention_mask=True,  # Construct attn. masks.
                return_tensors='pt',  # Return pytorch tensors.
            )

            # Add the encoded sentence to the list.
            input_ids.append(encoded_dict['input_ids'])

            # And its attention mask (simply differentiates padding from non-padding).
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

        # date_df: pd.DataFrame = df[['date']].join(result)
        result.index = pd.to_datetime(df.date)

        return result

import os

def save_report(report: pd.DataFrame, filename='my_report.csv', directory='data/reports'):
    with open(os.path.join(directory, filename),'w') as f:
        f.write(report.to_csv())

def load_report(filename='my_report.csv', directory='data/reports'):
    with open(os.path.join(directory, filename), 'r') as f:
        report = pd.read_csv(f)
    return report

class Report(object):
    """
    TODO: Report object to contain whatever goes into a report
    """
    def __init__(self):
        pass

if __name__ == '__main__':
    """
    Example Usage: 
    Prepare data from gz file, then submit to sentiment analyzer.
    
    Save the report afterward."""


    data_source = ForumDataSource()
    input_data = data_source.load_from_file('data/reddit/Monero_comments_1598932800_1596254400.json.gz')

    sentiment_analyzer = SentimentAnalyzer()

    # Just use 32 records for now ( faster )
    r = sentiment_analyzer.predict(input_data[:32])

    # Set pandas display options (more space for data)
    pd.set_option("display.max_columns", 500)
    pd.set_option('display.width', 1000)
    print(r[['text','prediction','sentiment_score']])

    # ir.plot(y='sentiment_score')

    df = load_report()
    df.index = pd.to_datetime(df.date)
    df.resample("H").mean().plot(title='Hourly mean')