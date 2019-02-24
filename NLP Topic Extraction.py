import requests
import re
import pandas as pd
import numpy as np
import nltk
import string
from bs4 import BeautifulSoup
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from itertools import chain
from collections import defaultdict
from collections import Counter
from nltk.corpus import stopwords


#Additional stopwords
new_stopwords = ['said']
stopwords = nltk.corpus.stopwords.words('english')
stopwords = stopwords + new_stopwords


def striphtml(x):
    p = re.compile(r'<.*?>') #Remove HTML formatting.
    return p.sub('', x)


def website_tokenizer(website):

    #EXTRACT <p> TAG DATA.
    page = requests.get(website) #Request website information.

    unprocessed_website_text = [] #Fill empty list with website text.
    soup = BeautifulSoup(page.content, 'html.parser')

    for p_tag in soup.find_all('p'):
        if 'style' in p_tag.attrs:
            del p_tag.attrs['style'] #Delete style attribute
        elif 'class' in p_tag.attrs:
            del p_tag.attrs['class'] #Delete class attribute
        else:
            unprocessed_website_text.append(p_tag)

    website_text = [str(i) for i in unprocessed_website_text] #Convert BS Type to string.
    website_text = [striphtml(i) for i in website_text if i[0:4] != '<p><'] #Remove HTML and remove <p><class> tags.

    website_text = [re.sub(r'\[[0-9]+\]', '', i).lower() for i in website_text]  # Remove numeric citations in the form [Number].
    website_text = [re.sub(r'[^\w\s]','', i) for i in website_text] #Remove punctuation.
    website_text = [nltk.word_tokenize(i) for i in website_text] #Tokenize words.

    website_text = list(chain.from_iterable(website_text)) #Uncomment if flattened list is required.
    website_text = [i for i in website_text if len(i) > 1] #Remove elements of length 1.
    filtered_words = [i for i in website_text if i not in stopwords]

    frequency = defaultdict(int)
    for text in filtered_words:
        frequency[text] += 1

    unique_filtered_words = [text for text in filtered_words if frequency[text] > 1]


###############################################################################
###############################################################################
###############################TAG EXTRACTION##################################
###############################################################################
###############################################################################

    #Objective: Try extracting topic tag, else guess topic tag using popular capitalised words.

    if website[8:21] == 'www.bbc.co.uk':
        try:
            topic_tags = soup.find_all('div', attrs={'id': 'topic-tags'}) #Extract topic tag from HTML page.
            tags_list = []
            for div in topic_tags:
                tags_list.append(div.find('a'))
            tags_list = [str(i) for i in tags_list]
            tags_list = [i.split('>')[1] for i in tags_list] #Find first occurance of > as important information is after >.
            tags_list = list(set([i[:-3] for i in tags_list])) #Remove HTML formatting 3 characters after <.

        except IndexError:

            #Objective: Guess tags using popular capitalised words.
            website_text = [str(i) for i in unprocessed_website_text]  # Convert BS Type to string.
            guess_tags = [striphtml(i) for i in website_text if i[0:4] != '<p><']
            guess_tags = [re.sub(r'[^\w\s]', '', i) for i in guess_tags] #Remove punctuation.

            guess_tags = [' '.join(word.strip(string.punctuation).lower() for word in i.split() if not word.islower()) for i in guess_tags]
            guess_tags = [nltk.word_tokenize(i) for i in guess_tags] #Tokenize words.
            guess_tags = list(chain.from_iterable(guess_tags)) #Create flattened list.
            guess_tags = [i for i in guess_tags if i not in stopwords] #Remove stopwords.
            guess_tags = [i for i in guess_tags if len(i) > 3] #Remove words shorter than 3 letters.
            guess_tags = [i for i in guess_tags if not i.isdigit()] #Remove numbers.

            c = Counter(guess_tags)
            guess_tags = c.most_common(5)[:] #Filter values by 3 most frequent.
            tags = [i[0] for i in guess_tags] #Return the 3 most words.
            counts = [i[1] for i in guess_tags] #Return associated frequencies.

            # Define tagging tolerance
            tag_tolerance = 0

            counts_filter = [i for i in counts if (max(counts) / i) >= tag_tolerance] #Filter results that are <3 frequent than the maximal frequency value.

            counts = counts[:len(counts_filter) + 1] #Filter list by index.
            tags_list = tags[:len(counts)] #Filter list by index.
            tags_list = [i.capitalize() for i in tags_list] #Capitalise each word.

    else:

        #Objective: Guess tags using popular capitalised words.
        website_text = [str(i) for i in unprocessed_website_text]  # Convert BS Type to string.
        guess_tags = [striphtml(i) for i in website_text if i[0:4] != '<p><']
        guess_tags = [re.sub(r'[^\w\s]', '', i) for i in guess_tags]  # Remove punctuation.

        guess_tags = [' '.join(word.strip(string.punctuation).lower() for word in i.split() if not word.islower()) for i
                      in guess_tags]
        guess_tags = [nltk.word_tokenize(i) for i in guess_tags]  # Tokenize words.
        guess_tags = list(chain.from_iterable(guess_tags))  # Create flattened list.
        guess_tags = [i for i in guess_tags if i not in stopwords]  # Remove stopwords.
        guess_tags = [i for i in guess_tags if len(i) > 3]  # Remove words shorter than 3 letters.
        guess_tags = [i for i in guess_tags if not i.isdigit()]  # Remove numbers.

        c = Counter(guess_tags)
        guess_tags = c.most_common(5)[:]  # Filter values by 3 most frequent.
        tags = [i[0] for i in guess_tags]  # Return the 3 most words.
        counts = [i[1] for i in guess_tags]  # Return associated frequencies.

        counts_filter = [i for i in counts if (max(counts) / i) >= tag_tolerance]  # Filter results that are <3 frequent than the maximal frequency value.

        counts = counts[:len(counts_filter) + 1]  # Filter list by index.
        tags_list = tags[:len(counts)]  # Filter list by index.
        tags_list = [i.capitalize() for i in tags_list]  # Capitalise each word.

    return unique_filtered_words, tags_list


print(website_tokenizer('https://www.bbc.co.uk/news/uk-england-norfolk-47348108')[0])
print(website_tokenizer('https://www.bbc.co.uk/news/uk-england-norfolk-47348108')[1])


def spacy_tokenizer():
    return

def polygot_tokenizer():
    return

#Next Steps
#Add general function
#Add spacy function
#import polygot function
#sort this