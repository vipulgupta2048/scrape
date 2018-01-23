# Natural Language Processing

## News Classifier
----------------------------------
The news classifier is implemented using **Doc2Vec** & **SVM**. **Doc2Vec** for creating word embeddings and **SVM** for classifying.
#### Requirements and Setup
Install the requirements  
``pip install -r requirements.txt``

Run `setup.py` to  setup the working directory  
``python setup.py``

#### Training the model
Train the model by executing `train.py`  
``python train.py``

 #### Using the Module/API
 - To use the classifier ``import`` ``newsClassifier.py`` into your script.
 - Use ``newsClassifier.categorize(document)`` to categorize a news article.
 - Here, ``document`` is a string object containing the news article.
 - ``newsClassifier.categorize()`` returns a string object containing the predicted category of ``document``.

## News Summarization
--------------------------------------
_//TODO_

## Information Extraction
----------------------------------------------
_//TODO_
