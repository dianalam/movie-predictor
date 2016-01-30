# scraping
import requests
from bs4 import BeautifulSoup

# parsing
import re
import dateutil.parser
from word2number import w2n
import string
from pprint import pprint

# storing
import pickle
import os

# text alerts
from twilio.rest import TwilioRestClient

# customize output dir and file names below if desired
outfile_urls = "testdata/all-movie-urls.pkl"
outfile_moviedata = "testdata/all-movie-data.pkl"
outfile_failedurls = "testdata/failed-urls.pkl"

def get_movie_page(url):
	"""
	Gets movie page as soup object for the provided url.
	Args:
		url (str): url of movie page
	Returns:
		movie_page (soup object): html of movie page
	"""
	movie_page = BeautifulSoup(requests.get(url).text, "lxml")
	return movie_page

def get_movie_value(soup, field_name, is_people=False):
	"""Search soup object by keyword and return next
	sibling or object as text.
	Args:
	soup -- beautiful soup object
	field_name (str) -- keyword to search for
	is_people (bool) -- set to true if searching for actor,
	director, producer, or writer; parses findings
	Returns:
	string of found text
	"""
	obj = soup.find(text=re.compile(field_name))
	if not obj:
		return None
	next_sibling = obj.findNextSibling()
	next_obj = obj.findNext()

	# for lists of people (actors, dir, prod, etc.), returns html result for
	# parsing in people_to_list(); else, returns text from object
	if next_sibling:
		if is_people:
			return next_sibling
		else:
			return next_sibling.get_text()
	elif next_obj:
		if is_people:
			return next_obj
		else:
			return next_obj.get_text()
	else:
		return None

### functions below for cleaning search results
def clean_title(titlestring):
	"""Cleans up retrieved movie title."""
	try:
		title = str(titlestring.split("(")[0]).strip()
		return title
	except:
		return None

def to_date(datestring):
	"""Converts date string to datetime object."""
	try:
		date = dateutil.parser.parse(datestring.strip())
		return date
	except:
		return None

def money_to_int(moneystring):
	"""Converts dollar figure string into int."""
	try:
		moneystring = moneystring.replace("$", "").replace(",", "")
		return int(moneystring)
	except:
		return None

def budget_to_int(budgetstring):
	"""Converts budget string figure (in format $X million/billion/thousand)
	into int.
	"""
	try:
		budget_val_list = budgetstring.replace("$", "").split(" ")
		vals_dict = {"thousand": 1000,
					 "million": 1000000,
					 "billion": 1000000000}
		budget = float(budget_val_list[0]) * vals_dict[budget_val_list[1]]
		return int(budget)
	except:
		return None

def people_to_list(peopleobj):
	if peopleobj is None:
		return ""
	else:
		try:
			people_list = [str(person.strip("*")) for person in peopleobj.stripped_strings if "(" not in person]
			return people_list
		except:
			return ""

def noms_from_oscars(oscarsstring):
	"""Converts descriptive oscars text to number of nominations as int."""
	try:
		nominations_str = (str(oscarsstring.split(",")[0]).strip().lower()).split(" ")
		nominations = w2n.word_to_num(nominations_str[2])
		return nominations
	except:
		return 0

def wins_from_oscars(oscarsstring):
	"""Converts descriptive oscars text to number of wins as int."""
	try:
		wins_str = (str(oscarsstring.split(",")[1]).replace(".", "").strip().lower()).split(" ")
		wins = w2n.word_to_num(wins_str[1])
		return wins
	except:
		return 0

def theaters_to_int(theaterstring):
	"""Converts string of number of theaters into int."""
	try:
		theaters = theaterstring.strip().replace(",", "").split(" ")[0]
		return int(theaters)
	except:
		return None

def runtime_to_minutes(runtimestring):
	"""Converts runtime string into minutes."""
	try:
		runtime = runtimestring.split()
		minutes = int(runtime[0])*60 + int(runtime[2])
		return minutes
	except:
		return None

def get_movie_data(soup):
	"""Parses soup object of the movie page and returns dictionary of movie
	features (title, rating, genre, distributor, production budget,
	domestic total gross, domestic total adjusted gross (2015$), international
	total gross, oscar nominations, oscar wins, release date, closing date,
	runtime, director(s), writers, actors, producers.)
	"""
	raw_title = soup.find("title").text
	title = clean_title(raw_title)

	raw_rating = get_movie_value(soup, "MPAA Rating")
	rating = str(raw_rating)

	raw_genre = get_movie_value(soup, "Genre:")
	genre = str(raw_genre)

	raw_distributor = get_movie_value(soup, "Distributor")
	distributor = str(raw_distributor)

	raw_theaters = get_movie_value(soup, "Widest")
	theaters = theaters_to_int(raw_theaters)

	raw_budget = get_movie_value(soup, "Production")
	budget = budget_to_int(raw_budget)

	raw_domestic_total_gross = get_movie_value(soup,"Domestic:")
	domestic_total_gross = money_to_int(raw_domestic_total_gross)

	raw_domestic_total_adj_gross = get_movie_value(soup,"Domestic Total Adj")
	domestic_total_adj_gross = money_to_int(raw_domestic_total_adj_gross)

	raw_intl_total_gross = get_movie_value(soup, "Worldwide")
	intl_total_gross = money_to_int(raw_intl_total_gross)

	raw_oscars = get_movie_value(soup, "Academy Awards")
	oscar_noms = noms_from_oscars(raw_oscars)
	oscar_wins = wins_from_oscars(raw_oscars)

	raw_release_date = get_movie_value(soup,"Release Date")
	release_date = to_date(raw_release_date)

	raw_closing_date = get_movie_value(soup, "Close")
	closing_date = to_date(raw_closing_date)

	raw_runtime = get_movie_value(soup,"Runtime")
	runtime = runtime_to_minutes(raw_runtime)

	raw_director = get_movie_value(soup, "Director", is_people=True)
	director = people_to_list(raw_director)

	raw_writers = get_movie_value(soup, "Writer", is_people=True)
	writers = people_to_list(raw_writers)

	raw_actors = get_movie_value(soup, "Actor", is_people=True)
	actors = people_to_list(raw_actors)

	raw_producers = get_movie_value(soup, "Producer", is_people=True)
	producers = people_to_list(raw_producers)

	headers = ["1-title", "rating", "genre", "distributor", "theaters", "budget",
				"dom_total_gross", "domestic_total_adj_gross", "intl_total_gross",
				"oscar_noms", "oscar_wins", "2-release_date", "3-closing_date",
				"runtime_mins", "director", "writers", "actors", "producers"]

	movie_dict = dict(zip(headers, [title,
									rating,
									genre,
									distributor,
									theaters,
									budget,
									domestic_total_gross,
									domestic_total_adj_gross,
									intl_total_gross,
									oscar_noms,
									oscar_wins,
									release_date,
									closing_date,
									runtime,
									director, writers, actors, producers]))

	return movie_dict


def get_movies_on_page(soup):
	"""Given a soup object of an A-Z movie page, return a list of all the movie
	urls on that page. Movie urls point to the individual movie page where we'll
	be able to extract data.
	"""
	movie_urls = []
	body = soup.body.find(id="body") # look only in div id body
	movies_on_page = [tag["href"] for tag in body.find_all("a") if "movies/?id" in tag["href"]]
	movie_urls.extend(movies_on_page)
	return movie_urls

def get_movies_from_letters(letter_list):
	"""Crawl A-Z pages and scrape URLs for all movies listed on those pages.
	Take a list of letters (#, A-Z) and return a list of all movie urls
	(suffixes only).
	"""
	all_movie_urls = []
	url_prefix = "http://www.boxofficemojo.com/movies/alphabetical.htm?letter="
	url_suffix = "&page="
	for letter in letter_list:
		page = 1
		# checks if there are any movies listed on the given page, append movies
		# if yes, moves on to next letter if not
		while True:
			url = url_prefix + letter + url_suffix + str(page)
			page_soup = get_movie_page(url)
			movie_urls = get_movies_on_page(page_soup)
			all_movie_urls.extend(movie_urls)
			page += 1
			if len(movie_urls) == 0:
				break
	return all_movie_urls

def get_num_movies():
	"""Retrieve data for movies starting with a number, since page structure
	is built differently than letters.
	"""
	url = "http://www.boxofficemojo.com/movies/alphabetical.htm?letter=NUM"
	page_soup = get_movie_page(url)
	movie_urls = get_movies_on_page(page_soup)
	return movie_urls

def get_all_movie_data(url_list):
	"""Take a list of individual movie page urls and return a list of
	dictionaries of individual movie data.
	"""
	url_prefix = "http://www.boxofficemojo.com"
	url_suffix = "&adjust_yr=2015"
	all_movie_data = []
	failed_urls = []
	for movie in url_list:
		url = url_prefix + movie + url_suffix
		try:
			soup = get_movie_page(url)
			data_dict = get_movie_data(soup)
			data_dict["url"] = movie.split("=")[1] # add movie url for reference
			all_movie_data.append(data_dict)
		except:
			print "error processing url: " + movie
			failed_urls.append(url)
		print "processed: " + movie
	return all_movie_data, failed_urls

def text_me():
	"""Send a text message when done scraping if env variables TWILIO_SID,
	TWILIO_TOKEN, and PHONE_NUM are set.
	Args:
	number (string) -- your phone number, formatted as +1<number>
	"""
	try:
		account_sid = os.environ["TWILIO_SID"]
		auth_token = os.environ["TWILIO_TOKEN"]
		phone_number = os.environ["PHONE_NUM"]
		client = TwilioRestClient(account_sid, auth_token)
		message = client.messages.create(to=phone_number,
										from_="+13476258954",
										body="done scraping movies!")
		print "Sending text message!"
	except:
		print "No twilio credentials configured."

def main():
	# get list of all movies, pickle, and return
	print "Processing movie urls..."
	letter_list = list(string.ascii_uppercase)
	all_movies_list = get_movies_from_letters(letter_list)
	num_movies = get_num_movies()
	all_movies_list.extend(num_movies)
	with open(outfile_urls, "w") as picklefile:
	    pickle.dump(all_movies_list, picklefile)
	with open(outfile_urls, "r") as picklefile:
	    loaded_movie_list = pickle.load(picklefile)
	print "Done processing movie urls."
	print "Movie urls saved to: ", outfile_urls

	# get movie data from list of movie urls and pickle
	print "Getting movie data..."
	all_movies_dict, failed_urls = get_all_movie_data(loaded_movie_list)
	with open(outfile_moviedata, "w") as picklefile:
		pickle.dump(all_movies_dict, picklefile)
	with open(outfile_failedurls, "w") as picklefile:
		pickle.dump(failed_urls, picklefile)

	# get text notification when done
	text_me()
	print "Done getting movie data!"
	print "Movie data saved to: ", outfile_moviedata
	print "Failed urls list saved to: ", outfile_failedurls

if __name__ == "__main__":
    main()
