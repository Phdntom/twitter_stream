import sys
import json

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
    (dict, list) -> list

    Parameters
    ----------
    scores: dict
        Dictionary relating words (str) to values (int).
    tweet_text: list
        A list containing the text (str) of a tweet.

    Returns
    -------
    tweet_scores: list
        A list of scores (int) corresponding to each tweet in tweet_text.
    '''
    words = tweet.split()
    tweet_score = 0
    for word in words:
        if scores.has_key(word):
            tweet_score += scores[word]

    return tweet_score

def tweet_filter(scores, tweets_text, strength_cutoff = 0):
    '''
    (list, list, int) -> list of 2-tuples
    '''
    index = 0
    for each in scores:
        if abs(each) >= strength_cutoff:
            print each, tweets_text[index]
        index += 1

def main():

    sent_file = sys.argv[1]
    scores = load_scores(sent_file)

    tweet_file = sys.argv[2]
    tweets_text = parse_file(tweet_file,"text")

    tweet_scores = []
    for tweet in tweets_text:
        tweet_scores.append(score_tweet(scores,tweet))

    tweet_filter(tweet_scores, tweets_text, 3)
   
if __name__ == '__main__':
    assert len(sys.argv) == 3
    print "\tSentiment File: {0}".format(sys.argv[1])
    print "\tTweet Stream File: {0}\n".format(sys.argv[2])
    main()

