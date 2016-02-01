# movie-predictor
Use regression to predict potential success of low-budget films based on film characteristics. What factors drive success and how are these factors different for success as defined by revenues vs. success as defined by recognition (Oscar nominations?). 

For more information, see my [blog post](http://dianalam.github.io/2016/01/30/movie-success.html).

## in this repo
* `movie-scraper.py` scrapes data for all movies (16,100+) on boxofficemojo.com
* `oscar-scraper.py` scrapes Oscars data from Newsday 
* `movie-predictor-analysis.ipynb` iPython notebook with regression analysis 
* `data/` contains data (pkl files and CPI csv) used in iPython notebook analysis; also the default subdir where pkl files will be saved if scraping scripts are run
* `presentation/` contains pdf presentation of findings & recommendations

## installation
### clone this repo  
```bash
$ git clone https://github.com/dianalam/movie-predictor.git
```

### dependencies
Scripts were written in Python 2.7. You'll need the following modules: 
```bash
matplotlib >= 1.5.1  
numpy >= 1.10.1  
pandas >= 0.17.1  
python-dateutil >= 2.4.2
scipy >= 0.16.0
seaborn >= 0.6.0
sklearn >= 0.17
statsmodels >= 0.6.1
```

To install modules, run:  
```bash
$ pip install <module>
```

### running
Scrape boxofficemojo. Note that script comes with the option to get a text alert via Twilio once script is done running. To use, you'll need to pass your Twilio Account SID, Auth Token, and phone number (with +1 at the beginning) as environment variables.
```bash
$ TWILIO_SID = <my-account-sid> TWILIO_TOKEN = <my-auth-token> PHONE_NUM = <my-phone-number> python movie-scraper.py
```


Scrape Newsday
```bash
$ python oscar-scraper.py
```


View/run regression analysis (cells already executed in file)
```bash
ipython notebook movie-predictor-analysis.ipynb
```

## data sources
Thanks to: 
* [Box Office Mojo](http://boxofficemojo.com)
* [Newsday](http://data.newsday.com/long-island/data/entertainment/movies/oscar-winners-history/)
