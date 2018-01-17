import glob
import multiprocessing
#NLTK
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer, sent_tokenize
from nltk.stem import WordNetLemmatizer
#Gensim
from gensim.models.doc2vec import LabeledSentence, TaggedDocument
from gensim.models import Doc2Vec
#sklearn
from sklearn.externals import joblib
from sklearn.model_selection import train_test_split
from sklearn import svm


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

#Create set of stopwords
stop_words = set(stopwords.words('english'))
#Initialize Tokenizer
tokenizer = RegexpTokenizer('[\'a-zA-Z]+')
# Initialize lemmatizer
wordnet_lemmatizer = WordNetLemmatizer()

def tokenize(document):
    """
    Takes a string as input and returns a string with all stopwords removed,
    words lemmatized and every word converted to lower case.
    """
    words = []
    for sent in sent_tokenize(document):
        for t in tokenizer.tokenize(sent):
            if t.lower() not in stop_words:
                words.append(wordnet_lemmatizer.lemmatize(t.lower()))
    return ' '.join(words).strip()

for category, category_id in news_categories.items():
    print('Category: ' + category + ' ' + str(category_id))

    for file_name in glob.glob(news_dir + category + '/*.txt'):
        with open(file_name, 'r', encoding='ISO-8859-1') as news_file:
            news_data = news_file.read()

        newsX.append(tokenize(news_data))
        newsY.append(category_id)

print('Corpus Size: ' + str(len(newsX)))

print('Creating Tagged Documents')
tagged_documents = []
for i, document in enumerate(newsX):
    tagged_documents.append(TaggedDocument(document.split(' '), [i]))

print('Training Doc2Vec')
doc2vec_model = Doc2Vec(documents=news_tagged_documents, size=50, window=3,
                        min_count=2, iter=30, workers=multiprocessing.cpu_count())

print('Creating vectors')
news_vectors = []
for document in newsX:
    news_vectors.append(doc2vec_model.infer_vector(document.split(' ')))

X_train, X_test, Y_train, Y_test = train_test_split(news_vectors, newsY, test_size=0.25)
print('Training a SVM')
model = svm.SVC()
model.fit(X_train, Y_train)

print('Accuracy: ', svm.score(X_test, Y_test))
print('Saving models...')
joblib.dump(model, './models/svm.model')
print('Saved to "./models/svm.model"')
