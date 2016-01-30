# scraping
import requests
from bs4 import BeautifulSoup

# storing
import pickle

# change dir and name of pickle object if desired
outfile = 'data/oscars-data.pkl'

def get_movie_page(url):
    '''
    Gets movie page as soup object for the provided url.
    Args:
        url (str): url of movie page
    Returns:
        movie_page (soup object): html of movie page
    '''
    movie_page = BeautifulSoup(requests.get(url).text, 'lxml')
    return movie_page

def get_data_on_page(row):
    """Get oscars data from each page and return as dict.
    Args:
    row -- row in soup object
    """
    return {
        'year': row.select('.sdb-field-year')[0].text,
        'category': row.select('.sdb-field-category')[0].text,
        'won': row.select('.sdb-field-result')[0].text.lower() == 'yes',
        'film': row.select('.sdb-field-filmName')[0].text,
        'person': row.select('.sdb-field-actorDirectorName')[0].text}

def get_data(pgs):
    """Get oscars data from all pages and return as list of dicts.
    Args:
    pgs (list) -- list of page numbers (for urls)
    """
    alldata = []
    for pg in pgs:
        url = 'http://data.newsday.com/long-island/data/entertainment/movies/' + \
            'oscar-winners-history/?currentRecord=' + str(pg)
        soup = get_movie_page(url)
        rows = soup.select('.sdb-even,.sdb-odd')
        alldata.extend([get_data_on_page(row) for row in rows])
        print 'processed: ', str(pg)
    return alldata

def main():
    pgs = xrange(1, 2563, 50) # 2563 items with 50 per page
    oscardata = get_data(pgs)
    with open(outfile, 'w') as picklefile:
		pickle.dump(oscardata, picklefile)

if __name__ == '__main__':
    main()
