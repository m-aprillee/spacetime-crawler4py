import re
from urllib.parse import urlparse

STOPWORDS = ['a','about','above','after','again','against','all','am','an','and','any','are','aren', 't','as','at','be','because','been','before','being', 'below','between','both','but','by','can','cannot','could','couldn','did','didn','do','does','doesn','doing','don','down','during','each','few','for','from','further','had','hadn','has','hasn','have','haven','having','he','ll','her','here','hers','herself','him','himself','his','how','i','ve','if','in','into','is','isn','it','its','itself','let','me','more','most','musn','my','myself','no','nor','not','of','off','on','once','only','or','other','ought','our','ours','ourselves','out', 'over', 'own', 'same', 'shan', 'she', 'should', 'shouldn', 'so', 'some', 'such', 'than', 'that', 'the', 'their', 'them', 'themselves', 'then', 'there', 'these', 'they', 're', 've', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn', 'we', 're', 've', 'were', 'weren', 'what', 'what','when', 'where', 'which', 'while', 'who', 'whom', 'why',  'with', 'won', 'would', 'wouldn', 'you', 'your', 'yours', 'yourself', 'yourselves']

def processText():
    f = open("text.txt", "r")
    wordCounts = dict()
    currFileWordCount = 0
    currPage = ''
    readPage = False
    pageMostWords = ''
    mostWordCount = 0
    icsSubdomains = dict()
    
    numPages = 0
    
    for line in f:
        line = line.strip()
        if line != '':
            if readPage == True:
                currPage = line
                #check for ics.uci.edu subdomains
                o = urlparse(currPage)
                if 'ics.uci.edu' in o.netloc:
                    if o.netloc not in icsSubdomains:
                        icsSubdomains[o.netloc] = 1
                    else:
                        icsSubdomains[o.netloc] += 1

                readPage = False
            else:
                if line == ';;;;;':
                    #check for highest word count
                    if currFileWordCount > mostWordCount:
                        pageMostWords = currPage
                        mostWordCount = currFileWordCount
                    currFileWordCount = 0
                    readPage = True
                    numPages += 1
                else:
                    tokens = tokenize(line)
                    for t in tokens:
                        currFileWordCount += 1
                        if len(t) > 1:
                            if t not in STOPWORDS:
                                if t not in wordCounts:
                                    wordCounts[t] = 1
                                else:
                                    wordCounts[t] += 1
    f.close()
    
    print('REPORT')
    print('Number of unique pages:', numPages)
    print('Longest page:', pageMostWords, 'Word Count:', mostWordCount)
    print('50 most common words and their counts:')
    printFrequencies(wordCounts, 50)
    print('Subdomains in ics.uci.edu and number of pages each:')
    printFrequencies(icsSubdomains)
    
    
def printFrequencies(items, numToShow = -1, sort = 'f'):
    freq = list(items.items())
    if sort == 'f':
        freq.sort(key=lambda x: (-x[1], x[0]))
    elif sort == 'a':
        freq.sort(key=lambda x: (x[0], -x[1]))
        
    if numToShow != -1:
        freq = freq[0:50]
    for t, f in freq:
        print(f'{t} = {f}')
    
def tokenize(text):
    # I took this from my assignment 1 - Alisa
    res = []
    for line in text.split('\n'):
        for word in line.split():
            if bool(re.match('^[a-zA-Z0-9]+$', word)): # if the word is alphanumeric
                res.append(word.lower())
            else:
                addTokens = [] # stores the words that we must add
                currWord = []
                for c in word:
                    if not bool(re.match('^[a-zA-Z0-9]$', c)): # if not alphanumeric char, we will reset the currWord = ""
                        if currWord != []: 
                            addTokens.append("".join(currWord)) # we only want to append currWord if it's not ""
                            currWord = []
                    else:
                        currWord.append(c.lower())

                if currWord != []: # if after we finish looping through the whole word and there's a word we haven't added
                    addTokens.append("".join(currWord)) # we add that word that we haven't added yet
                res += addTokens # then we add all these words to the result!
    return res

processText()