'''
Python 2.7.3

happy_state.py

Uses the twitter 1% stream to compute the happiest state in the US.
"entities": "hashtags"

"place":"country", "fullname", "name", "coordinates"

"lang": "en"

"text":

'''

import sys
import json
from collections import defaultdict

STATE_CODES = {}
with open("STATE_CODES.txt") as fobj:
    for line in fobj:
        STATE_CODES[str(line).strip('\n')] = None

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
    tweet_text = tweet["text"]
    words = tweet_text.split()
    tweet_score = 0
    word_count = 0
    for word in words:
        if scores.has_key(word):
            word_count += 1
            tweet_score += scores[word]

    return tweet_score / word_count

def parse_candidates(tweet_file, filters=None):
    '''
    (str) -> list

    Parameters
    ----------
    tweet_file: str
        The path to the json tweet stream file.

    Returns
    -------
    candidate_tweets: list
        A list of candidate ("location","text") tuples.
    '''
    refined_tweets = []
    with open(tweet_file) as fobj:
        for line in fobj:
            tweet_obj = json.loads(line)
            candidate = tweet_filter(tweet_obj,filters)
            if candidate is not None:
                refined_tweets.append( candidate )
    
    return refined_tweets

def tweet_filter(tweet_obj, filters):
    '''
    '''
    for f in filters:
        f_pass = f(tweet_obj)
        if not f_pass:
            return None

    return tweet_obj

def text_filter(tweet_obj):
    '''
    Returns
    -------
    passes filter:  return the text field
    failes filter:  return None
    '''
    if tweet_obj.has_key("text"):
        return True
    else:
        return False

def location_filter(tweet_obj):
    '''
    Returns
    -------
    passes filter:  return the location field
    failes filter:  return None
    '''
    if tweet_obj.has_key("user") \
        and tweet_obj["user"].has_key("location") \
        and len(tweet_obj["user"]["location"]) > 0:
            return True

    return False

def hashtag_filter(tweet_obj):
    '''
    Returns
    -------
    passes filter:  return the location field
    failes filter:  return None
    '''
    if tweet_obj.has_key("entities") \
        and tweet_obj["entities"].has_key("hashtags") \
        and len(tweet_obj["entities"]["hashtags"]) > 0:
            return True
    return False

def get_state(tweet_location):
    '''
    (str) -> str

    Parameters
    ----------
    location: string
        String containing the tweet's location.

    Returns
    -------
    state_code: str or None
        str: Valid two-letter US state code (e.g. CA, NY, TX etc).
        None: If no valid code parsible.
    '''
    location_cap = tweet_location.upper()
    words = location_cap.split()
    for word in words:
        minimal = word.strip(' .,!@#$%^&*()\'\"?><:;][}{|\\')
        if STATE_CODES.has_key(minimal):
            return minimal

    return None

def hashtag_count(pairs_list):
    '''
    '''
    num = 0
    for each in pairs_list:
        num += each[1]
    return num

def prep_JSON(state_hashtags):
    '''
    '''
    total_count = 0
    json_dict = {}
    json_dict["country"] = "US"
    json_dict["states"] = {}
    for state in state_hashtags:
        print state
        json_dict["states"][state] = {}
        json_dict["states"][state]["hashtags"] = \
        sorted(state_hashtags[state].items(), key=lambda x:x[1], reverse=True)
        count = hashtag_count(json_dict["states"][state]["hashtags"])
        json_dict["states"][state]["count"] = count

        total_count += count
    json_dict["hashtag-total"] = total_count

    return json_dict

def get_bin_key(tweet_score):
    '''
    -5 to -3, 0
    -3 to -1, 1
    -1 to +1, 2
    +1 to +3, 3
    +3 to +5, 4
    '''
    if tweet_score < -3:
        return "-5 to -3"
    elif tweet_score < -1:
        return "-3 to -1"
    elif tweet_score <= 1:
        return "-1 to +1"
    elif tweet_score <= 3:
        return "+1 to +3"
    elif tweet_score <= 5:
        return "+3 to +5"
    else:
        print "bin scoring error\n";

    

def main():
    sent_file = sys.argv[1]
    scores = load_scores(sent_file)

    tweet_file = sys.argv[2]
    candidates = parse_candidates(tweet_file,
                                      [location_filter,hashtag_filter])

    state_hashtags = defaultdict( lambda: defaultdict(int))
    for tweet in candidates:
        state = get_state(tweet["user"]["location"])
        if state is not None:
            
            for hashtag in tweet["entities"]["hashtags"]:
                state_hashtags[state][hashtag["text"]] += 1

    json_dict = prep_JSON(state_hashtags)

    outname = "hashtags_" + tweet_file[3:]
    with open(outname, "w") as fobj:
        fobj.write(json.dumps(json_dict))

if __name__ == '__main__':
    assert len(sys.argv) == 3
    print "\tSentiment File: {0}".format(sys.argv[1])
    print "\tTweet Stream File: {0}\n".format(sys.argv[2])
    main()

"""



def state_sentiment(tweet_file, scores):
    '''
    (str, dict) -> list

    Parameters
    ----------
    tweet_file: str
        The path to the json tweet stream file.
    scores: dict
        Dictionary relating words (str) to values (int).

    Returns
    -------
    state_scores: dict
        Dictionary relating two-letter state codes to tweet sentiment scores.

    '''
    state_scores = {}
    candidate_tweets = parse_candidates(tweet_file)
    for location,text in candidate_tweets:
        state_code = has_state(location)
        if state_code is not None:
            text_score = score_tweet(text, scores)
            state_scores = update_scores(state_code, text_score, state_scores)
                
    return state_scores

def happiest_state(state_scores):
    '''
    ( dict ) -> str, float
    '''
    happiest_mean = None
    happiest_code = None
    for each in state_scores:
        value = state_scores[each]
        cur_mean = float(value[0]) / value[1]
        if cur_mean > happiest_mean:
            happiest_mean = cur_mean
            happiest_code = each

    return (happiest_code, happiest_mean)
            


STATE_CODES = {}
with open("STATE_CODES.txt") as fobj:
    for line in fobj:
        STATE_CODES[str(line).strip('\n')] = None
"""


