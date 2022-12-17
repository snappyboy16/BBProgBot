from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import RegexpTokenizer
import pymorphy2
import pandas as pd
import pickle

with open(r"C:\Users\aleks\PycharmProjects\BBProgBot\pkl\model5.pkl", "rb") as f:
    model = pickle.load(f)
tokenizer = RegexpTokenizer(r'\w+')  # объявление токенизатора
morph = pymorphy2.MorphAnalyzer()  # объявление лемматизатора
tfidfconverter = TfidfVectorizer()

data = pd.read_csv('pkl/train_data.csv')
X_train = tfidfconverter.fit_transform(data["utterance"]).toarray()

request = 'Как я могу зарегестрироваться на сайте?'
res = model.predict(tfidfconverter.transform(
    [' '.join([morph.parse(word)[0][2] for word in tokenizer.tokenize(f'{request}')])]).toarray())
print(res)