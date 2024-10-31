from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import pandas as pd
import random
import nltk
from nltk import word_tokenize, pos_tag

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

df = pd.read_csv("./data/recurring_themes.csv")

df['Theme'] = df['Theme'].str.lower()

words_to_replace = ['nice', 'good', 'bad', 'better']

for word in words_to_replace:
    df['Theme'] = df['Theme'].str.replace(word, '')

def pastel_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    return "hsl(210, 100%%, %d%%)" % random.randint(60, 80)

for sentiment in ["Positive", "Neutral", "Negative"]:
    text = " ".join(df[df["Sentiment"] == sentiment]["Theme"].tolist())

    nouns = []
    for word, pos in pos_tag(word_tokenize(text)):
        if pos.startswith('NN'): 
            nouns.append(word)
    filtered_text = " ".join(nouns)

    wordcloud = WordCloud(width=800, height=400, background_color="white", color_func=pastel_color_func).generate(filtered_text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(f"./data/{sentiment.lower()}.png")  
    plt.close()

overall_sentiment = df[df["Sentiment"] == "Overall sentiment"]["Theme"].values[0]
print(f"Overall sentiment: {overall_sentiment}")