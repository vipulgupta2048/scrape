import glob  # Used for iterating through files
import multiprocessing as mp  # Just used for getting the no. of CPU cores

# NLTK | http://www.nltk.org/api/nltk.html#subpackages
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer, sent_tokenize
from nltk.stem import WordNetLemmatizer

# Gensim | https://radimrehurek.com/gensim/models/doc2vec.html
from gensim.models.doc2vec import TaggedDocument
from gensim.models import Doc2Vec

# sklearn | scikit-learn.org/
from sklearn.externals import joblib  # Used for saving the sklearn model
from sklearn.model_selection import train_test_split  # For splitting the data
from sklearn import svm  # SVM model http://scikit-learn.org/stable/modules/svm


news_dir = './data/bbc/'
news_categories = {
    'business': 1,
    'entertainment': 2,
    'politics': 3,
    'sport': 4,
    'tech': 5
}

newsX = []
newsY = []

# Create a set of stopwords
# i.e. words that do not impart much too the meaning of a text
stop_words = set(stopwords.words('english'))
# Initialize Tokenizer
# Used for extracting words from a string of text
tokenizer = RegexpTokenizer('[\'a-zA-Z]+')
# Initialize lemmatizer
# Refer to: https://en.wikipedia.org/wiki/Lemmatisation#Description
wordnet_lemmatizer = WordNetLemmatizer()


def clean(document):
    """Clean a document.

    Takes a string as input and returns a string with all stopwords removed,
    words lemmatized and every word converted to lower case.
    """
    words = []
    for sent in sent_tokenize(document):
        for t in tokenizer.tokenize(sent):
            if t.lower() not in stop_words:
                words.append(wordnet_lemmatizer.lemmatize(t.lower()))
    return ' '.join(words).strip()


# Iterating through the different categories of text in sample data
for category, category_id in news_categories.items():
    print('Category: ' + category + ' ' + str(category_id))
    # Iterating through each news article in a category
    for file_name in glob.glob(news_dir + category + '/*.txt'):
        with open(file_name, 'r', encoding='ISO-8859-1') as news_file:
            news_data = news_file.read()

        newsX.append(clean(news_data))
        newsY.append(category_id)

print('Corpus Size: ' + str(len(newsX)))

# For Tagged Documents refer:
# https://radimrehurek.com/gensim/models/doc2vec.html#gensim.models.doc2vec.TaggedDocument
print('Creating Tagged Documents')
tagged_documents = []
for i, document in enumerate(newsX):
    tagged_documents.append(TaggedDocument(document.split(' '), [i]))


print('Training Doc2Vec')
# Refer: https://radimrehurek.com/gensim/models/doc2vec.html
doc2vec_model = Doc2Vec(documents=tagged_documents, size=50, window=3,
                        min_count=2, iter=30, workers=mp.cpu_count())

print('Creating vectors')
# Using the doc2vec model to convert each news article into a vector
news_vectors = []
for document in newsX:
    news_vectors.append(doc2vec_model.infer_vector(document.split(' ')))

# Splitting the data into training and testing data [Ratio 3:1]
X_train, X_test, Y_train, Y_test = train_test_split(news_vectors, newsY,
                                                    test_size=0.25)

print('Training a SVM')
# Training an SVM with default hyperparameters
# Refer: http://scikit-learn.org/stable/modules/svm
model = svm.SVC()
model.fit(X_train, Y_train)

print('Accuracy: ', svm.score(X_test, Y_test))
print('Saving models...')
joblib.dump(model, './models/svm.model')
doc2vec_model.save('./models/doc2vec.model')
print('Saved to "./models"')
