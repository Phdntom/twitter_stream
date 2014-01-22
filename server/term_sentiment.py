from __future__ import division
import sys
import json as json
import math as math


def load_scores(score_file):
    '''
    (str) -> dict

    Parameters
    ----------
    score_file : str
        The path to the scores file.

    Returns
    -------
    scores : dict
        Dictionary relating words (str) to values (int).
    '''
    scores = {}
    with open(score_file) as fobj:
        for line in fobj:
            word, value = line.split("\t")
            scores[word] = int(value)

    return scores

def parse_file(tweet_file, field="text"):
    '''
    (str, str) -> list

    Parameters
    ----------
    field: str
        The name of the field you wish to extract.
    tweet_file: str
        The path to the tweet file.

    Returns
    -------
    tweets_field: list
        A list containing the field (str) of each line in tweet_file (str).
    '''
    print "Parsing {0} for the field {1}".format(tweet_file,field)
    tweets_field = []
    with open(tweet_file) as fobj:
        for line in fobj:
            tweet_obj = json.loads(line)
            if tweet_obj.has_key(field):
                tweets_field.append( tweet_obj[field].encode('utf-8') )

    return tweets_field

def score_tweet(scores, tweet):
    '''
    (dict, str) -> float

    Parameters
    ----------
    scores: dict
        Dictionary relating words (str) to values (int).
    tweet: str
        A string of text of the tweet.

    Returns
    -------
    tweet_score:
        A score of the tweet.
    '''
    words = tweet.split()
    tweet_score = 0
    strong_words = 0
    for word in words:
        if scores.has_key(word):
            tweet_score += scores[word]
            strong_words += 1

    return tweet_score, strong_words

def tweet_filter(scores, tweets_text, strength_cutoff = 0):
    '''
    (list, list, int) -> list of 2-tuples
    '''
    index = 0
    for each in scores:
        if abs(each) >= strength_cutoff:
            print each, tweets_text[index]
        index += 1

def term_score(scores, tweet):
    '''
    (dict, str) -> list of tuples

    Parameters
    ----------
    scores: dict
        Dictionary relating words (str) to values (int).
    tweet: str
        A string of text of the tweet.

    Returns
    -------
    term_scores:
        A list of (word,score) pairs for each word in the tweet.
    '''
    tweet_score, count = score_tweet(scores,tweet)

    if count == 0:
        return []

    term_scores = []

    words = tweet.split()
    for word in words:
        if not scores.has_key(word):
            term_scores.append( (word, tweet_score / count ) )

    return term_scores
      
def store_terms(terms, outfile):
    with open(outfile,"w") as out:
        lines = []
        for key in terms:
            value = terms[key]
            score = math.floor(value[0])
            freq = value[1]
            lines.append('\t'.join([key,str(score),str(freq)]) )
        out.write('\n'.join(lines))
        
def reduce_word(word):

    if "@" in word:
        return None
    minimal = ((word.lower()
              ).strip(' !@#$%^&*()<>?:\"{}|,./;\'[]\\')
              )
    return minimal

def main():

    # sent_file dictionary containts word, score pairs
    sent_file = sys.argv[1]
    scores = load_scores(sent_file)

    # tweet_file contains twitter stream data in json
    tweet_file = sys.argv[2]
    tweets_text = parse_file(tweet_file,"text")

    # for each tweet, split up the text into words and search scores
    # from each word score, accumulate a score for the entire tweet
    tweet_scores = []
    for tweet in tweets_text:
        tweet_scores.append(score_tweet(scores,tweet))

    term_scores = []
    for tweet in tweets_text:
        term_scores.extend( term_score(scores,tweet) )
    #print term_scores

    new_terms = {}
    for key_val in term_scores:
        term, score = key_val[0], key_val[1]

        # more text processing analysis here IS_NOUN etc
        word = reduce_word(term)
        if word is not None:
            if new_terms.has_key(word):
                new_terms[word] = (new_terms[word][0] + score, new_terms[word][1] + 1)
            else:
                new_terms[word] = (score, 1)

    ADD_NEW_TERM_CUTOFF = 1
    strong_scores = {}
    for key in new_terms:
        score_num = new_terms[key]
        score = score_num[0]
        num = score_num[1]
        avg = score / num
        if abs(avg) > ADD_NEW_TERM_CUTOFF and num > 1:
            strong_scores[key] = (avg, num)

        #print strong_scores
 
    store_terms(strong_scores, "NEW_AFFIN.txt")
#----------------------------------------

if __name__ == '__main__':
    assert len(sys.argv) == 3
    print "\tSentiment File: {0}".format(sys.argv[1])
    print "\tTweet Stream File: {0}\n".format(sys.argv[2])
    main()

