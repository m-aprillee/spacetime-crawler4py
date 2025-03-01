import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
import pickle

visited = set()

def updateText(content, url):
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()
    #append text to text file
    f = open("text.txt", "a")
    f.write(";;;;;\n")
    f.write(url)
    f.write('\n')
    f.write(text)
    f.close()
    
def saveVisited():
    f = open('visited.pkl', 'wb')
    pickle.dump(visited, f)
    f.close()
    
def loadVisited():
    v = set()
    try:
        f = open('visited.pkl', 'rb')
        v = pickle.load(f)
        f.close()
    except:
        f = open('visited.pkl', 'wb')
        f.close()
    return v


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

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return list({link for link in links if is_valid(link)})

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    next_links = list()

    if resp.status != 200 or url in visited or resp.url in visited or resp.raw_response == None:
        return next_links

    soup = BeautifulSoup(resp.raw_response.content, 'lxml')
    for link in soup.find_all('a'):
        if link.has_attr("href"):
            url_defrag = urldefrag(link.get('href'))[0] 
            next_links.append(url_defrag)

    updateText(resp.raw_response.content, resp.url)

    if len(visited) == 0:
        visited.update(loadVisited())
    visited.add(url)
    visited.add(resp.url)
    saveVisited()
    print(len(visited))

    return next_links

def is_low_information(url):
    # Return true if classified as low information url
    if re.search(r"\?action=login$", url):                # No need to crawl login pages
        return True
    if re.search(r".zip$", url) or re.search(r".ps$", url) or re.search(r".ps.gz$", url):        # Just takes to download
        return True
    if re.search(r"\?ical=\d+$", url):                     # Calendar stuff
        return True
    if re.search(r"\/img_\d+$", url):                     # Just one image
        return True
    if re.search(r"\?share=facebook$", url) or re.search(r"\?share=twitter$", url):              # SNS share
        return True
    return False

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    # Valid domains for the assignment:
    # *.ics.uci.edu/*           => \.ics.uci.edu\/{0,1}
    # *.cs.uci.edu/*            => \.cs.uci.edu\/{0,1}
    # *.informatics.uci.edu/*   => \.informatics.uci.edu\/{0,1}
    # *.stat.uci.edu/*          => \.stat.uci.edu\/{0,1}
    # today.uci.edu/department/information_computer_sciences/*
    #                           => ^today.uci.edu\/department\/information_computer_sciences\/{0,1}

    if not url:
        return False
    domains = set(['.ics.uci.edu/', '.cs.uci.edu/', '.informatics.uci.edu/', '.stat.uci.edu/', 'today.uci.edu/department/information_computer_sciences/'])

    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        if is_low_information(url):
            return False
        
        if re.match(r".*\.ics.uci.edu/\.*", url):
            pass
        elif re.match(r".*\.cs.uci.edu/\.*", url):
            pass
        elif re.match(r".*\.informatics.uci.edu/\.*", url):
            pass
        elif re.match(r".*\.stat.uci.edu/\.*", url):
            pass
        elif re.match(r"^today.uci.edu\/department\/information_computer_sciences\/.*", url):
            pass
        else:
            return False
        
        if re.match(r".*\/pdf.*", parsed.path.lower()):
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|ppsx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|odc)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
