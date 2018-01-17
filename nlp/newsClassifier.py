from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer, sent_tokenize
from nltk.stem import WordNetLemmatizer

from sklearn.externals import joblib

from gensim.models import Doc2Vec

news_categories = {
    1 : 'business',
    2 : 'entertainment',
    3 : 'politics',
    4 : 'sport',
    5 : 'tech'
}

doc2vec_model = Doc2Vec.load('./models/doc2vec.model')
svm = joblib.load('./models/svm.model')

def tokenize(document):
    """
    Takes a string as input and returns a string with all stopwords removed,
    words lemmatized and every word converted to lower case.
    """
    #Create set of stopwords
    stop_words = set(stopwords.words('english'))
    #Initialize Tokenizer
    tokenizer = RegexpTokenizer('[\'a-zA-Z]+')
    # Initialize lemmatizer
    wordnet_lemmatizer = WordNetLemmatizer()
    words = []
    for sent in sent_tokenize(document):
        for t in tokenizer.tokenize(sent):
            if t.lower() not in stop_words:
                words.append(wordnet_lemmatizer.lemmatize(t.lower()))
    return ' '.join(words).strip()

def categorize(document):
    """
    Categorizes a document into the following categories
    [business, entertainment, politics, sport, tech].
    Takes a string object as input and returns a string object.
    """
    doc = tokenize(document)
    vector = doc2vec_model.infer_vector(doc.split(' '))
    result = svm.predict(vector.reshape(1, -1))[0]
    return news_categories[result]
