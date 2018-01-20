# Natural Language Processing

## News Classifier
The news classifier is implemented using **Doc2Vec** & **SVM**. **Doc2Vec** for creating word embeddings and **SVM** for classifying.
#### Requirements and Setup
**[This will be automated soon]** \
Install the following python libraries\
``pip install gensim`` \
``pip install nltk`` \
``pip install sklearn``

Then run the python shell and execute the following \
``import nltk`` \
``nltk.download('wordnet')`` \
``nltk.download('stopwords')``

#### Training the model
**NOTE:** This step is not required. Pre-trained models are in './models'\
If you would like to train a model download the [BBC dataset.](http://mlg.ucd.ie/files/datasets/bbc-fulltext.zip)
- Download the data
  1. ``cd`` into this folder.
  2. ``mkdir data``
  3. ``cd data``
  4. ``wget http://mlg.ucd.ie/files/datasets/bbc-fulltext.zip``
  5. ``sudo apt-get install unzip``
  6. ``unzip bbc-fulltext.zip``
 - Run ``train.py`` or edit it as necessary.

 #### Using the Module/API
 - To use the classifier ``import`` ``newsClassifier.py`` into your script.
 - Use ``newsClassifier.categorize(document)`` to categorize a news article.
 - Here, ``document`` is a string object containing the news article.
 - ``newsClassifier.categorize()`` returns a string object containing the predicted category of ``document``.

## News Summarization
_//TODO_

## Information Extraction
_//TODO_
