import sys
import json

def scores_dict(score_file):
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

def parse_tweets_on(field, tweet_file):
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
    tweets_field = []
    with open(tweet_file) as fobj:
        for line in fobj:
            tweet_obj = json.loads(line)
            if field in tweet_obj:
                tweets_field.append( tweet_obj[field].encode('utf-8') )

    return tweets_field

def freq_histogram(tweets_text):
    '''
    (list) -> dict

    Parameters
    ----------
    tweets_text: list
        List containing the text field of a tweet.

    Returns
    -------
    histogram: dict
        Dictionary relating terms to their frequencies in tweets_text.
    '''
    histogram = {}
    super_count = 0
    for text in tweets_text:
        words = text.split()
        for word in words:
            if histogram.has_key(word):
                histogram[word] += 1
            else:
                histogram[word] = 1
            super_count += 1

    for each in histogram:
        histogram[each] = histogram[each] / float(super_count)

    return histogram
    

def main():


    sent_file = sys.argv[1]
    scores = scores_dict(sent_file)

    tweet_file = sys.argv[2]
    tweets_text = parse_tweets_on("text",tweet_file)

    tweet_freq_histogram = freq_histogram(tweets_text)

    for each in tweet_freq_histogram:
        print each, tweet_freq_histogram[each]

   
if __name__ == '__main__':
    assert len(sys.argv) == 3
    print "\tSentiment File: {0}".format(sys.argv[1])
    print "\tTweet Stream File: {0}\n".format(sys.argv[2])
    main()

