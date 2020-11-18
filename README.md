# CMSC495_Proj


## Cloning
This project uses Git LFS to track large files, so make sure to initialize & checkout files that way if you need sample data.

- Install git lfs
  - OSX: `brew install git-lfs`
- Pull
  - `git lfs install`
  - `git lfs checkout`

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

{
  "client_id": <client ID from reddit>,
  "api_key": <secret api key from reddit>,
  "username": <associated reddit username>,
  "password": <associated reddit password>
}

### References

- "FinBERT: Financial Sentiment Analysis with Pre-trained Language Models": https://arxiv.org/pdf/1908.10063.pdf