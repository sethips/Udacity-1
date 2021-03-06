## Udacity CS101 Web Crawler
import urllib2
    
##
#   Utilities
##    
def split_string(source,splitlist):    
    default_sep = splitlist[0]
    for sep in splitlist[1:]:
        source = source.replace(sep, default_sep)
    return [i.strip() for i in source.split(default_sep) if i != '']

##
# Hash Stuff
##    

def hash_string(keyword,buckets):
    sum = 0
    for c in keyword:
        sum += ord(c)
    return sum % buckets  
    
def make_hashtable(nbuckets):
    hashtable = []
    for n in range(nbuckets):
        hashtable.append([])
    return hashtable

def hashtable_get_bucket(htable,keyword):
    return htable[hash_string(keyword, len(htable))]
    
def hashtable_add_entry(htable, key, value):
    bucket = hashtable_get_bucket(htable, key)
    bucket.append([key, value])

def bucket_find(bucket, key):
    for entry in bucket:
        if entry[0] == key:
            return entry
        else:
            return None
    
def hashtable_lookup(htable, key):
    bucket = hashtable_get_bucket(htable, key)
    entry = bucket_find(bucket, key)
    if entry[0] == key:
        return entry[1]
    return None

def hashtable_update(htable, key, value):
    bucket = hashtable_get_bucket(htable, key)
    entry = bucket_find(bucket, key)
    if entry:
        entry[1] = value
    else:
        bucket.append([key, value])




##
#   Index Stuff
##    
def lookup(index,keyword):
    if keyword in index:
        return index[keyword]
    else:
        return None
            
def record_user_click(index,keyword,url):
    urls = lookup(index, keyword)
    if urls:
        for entry in urls:
            if entry[0] == url:
                entry[1] += 1

def add_to_index(index, keyword, url):
    if keyword in index:
        index[keyword] = (url)
    else:
        index[keyword] = url

def add_page_to_index(index,url,content):
    contentList = content.split()
    
    for keyword in contentList:
        add_to_index(index, keyword, url)

##
#   Crawl Stuff
##
def get_next_target(page):
    start_link = page.find('<a href=')
    if start_link == -1:
        return None, 0
    
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote+1:end_quote]
    return url, end_quote
        
def get_all_links(page):
    links = []
    while get_next_target(page)[0] != None:
        url, endpos = get_next_target(page)
        if url:
            links.append(url)
            page = page[endpos:]
        else:
            break
    return links

def get_page(url):
    try:
        import urllib
        return urllib.urlopen(url).read()
    except:
        return ""
    
def crawl(seed):
    tocrawl = set([seed])
    crawled = set()
    index = {}
    graph = {}
    
    while tocrawl:
        next_crawl = tocrawl.pop()
        if next_crawl not in crawled:
            page = get_page(next_crawl)
            add_page_to_index(index,next_crawl,page)
            outlinks = get_all_links(page)
            graph[next_crawl] = outlinks
            tocrawl.update(outlinks)
            crawled.add(next_crawl)


    return index, graph

##
# input: dictionary graph of urls and their outlinks
# output: dictionary {url:rank, ...}
# 
# rank(0,url) = 1/npages
# rank(t,url) = (1-d)/npages + 
# where d is the damping constant of 0.8
## 
def compute_ranks(graph):
    d = 0.8 # damping factor
    numloops = 10
    
    ranks = {}
    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages
    
    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d) / npages
            
            #Insert Code Here
            for node in graph:
                if page in graph[node]:
                    newrank += d * ranks[node] / len(graph[node])
            
            newranks[page] = newrank
        ranks = newranks
    return ranks
    
    
def lookup_best(index, ranks, keyword):
    pages = lookup(index, keyword)
    if not pages:
        return None
    best_page = pages[0]
    for candidate in pages:
        if ranks[candidate] > ranks[best_page]:
            best_page = candidate
    return best_page

##
# TESTING
##

## test seed crawl
# seed = 'http://www.udacity.com/cs101x/index.html'
# print crawl(seed)

## execution timer
import time

def time_execution(code):
    start = time.clock()
    result = eval(code)
    run_time = time.clock() - start
    print result, run_time
    
def spin_loop(n):
    i = 0
    while i < n:
        i = i + 1
    return i

## make big indexes
def make_string(p):
    s = ""
    for e in p:
        s = s + e
    return s

def make_big_index(size):
    index = []
    letters = ['a', 'a', 'a', 'a', 'a', 'a', 'a', 'a']
    while len(index) < size:
        word = make_string(letters)
        add_to_index(index, word, 'fake')
        for i in range(len(letters) - 1, 0, -1):
            if letters[i] < 'z':
                letters[i] = chr(ord(letters[i]) +1)
                break
            else:
                letters[i] = 'a'
    return index
    
## test hash function
def test_hash_function(func, keys, size):
    results = [0] * size 
    keys_used = []
    for w in keys:
        if w not in keys_used:
            hv = func(w, size)
            results[hv] += 1
            keys_used.append(w)
    return results

# index10000 = make_big_index(10000)
# time_execution('lookup(index10000, "udacity")')

# words = get_page('http://zachholman.com/').split()
# counts = test_hash_function(hash_string, words, 12)
# print counts

## test new crawl function with graph returned
# index, graph = crawl('http://www.udacity.com/cs101x/urank/index.html')
# print graph

## test compute_ranks()
index, graph = crawl('http://www.udacity.com/cs101x/urank/index.html')
ranks = compute_ranks(graph)
print ranks

