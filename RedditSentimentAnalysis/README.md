# CMSC495_Proj


## Cloning
This project uses Git LFS to track large files, so make sure to initialize & checkout files that way if you need sample data.

- Install git lfs
  - OSX: `brew install git-lfs`
- Pull
  - `git lfs install`
  - `git lfs pull`

## Environment
- Python 3.8
- Setup Virtual Environment
    - `python3 -m venv .env`
    - `source .env/bin/activate`
- Install dependencies
    - `pip install -r requirements.txt`

## API Credentials - credentials.json

A JSON document called 'credentials.json' should be saved in the root directory with the rest of the code,
formatted as follows:
```json
{
  "client_id": "<client ID from reddit>",
  "api_key": "<secret api key from reddit>",
  "username": "<associated reddit username>",
  "password": "<associated reddit password>"
}
```
## Files 
* sentiment_analyzer.py - Uses a BERT (language representation) model to process the scraped data in batches.  Main method produces some plots of sentiment over time for the Reddit posts. 

* sentiment_intensity.py - The "legacy" version of the above.

* download-models.sh - A downloader script, currently for the BERT model only (to safeguard against technical difficulties with git LFS)

* gather_data.py - As the name suggests, it gathers data from the forum, providing a ForumDataSource object with methods to store and retrieve the data (as a pandas DataFrame), with a little preprocessing

* gui_prototype.py - The actual GUI.

### References

- "FinBERT: Financial Sentiment Analysis with Pre-trained Language Models": https://arxiv.org/pdf/1908.10063.pdf