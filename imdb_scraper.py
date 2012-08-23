#!/bin/python
import os,re,urllib,urllib2
from BeautifulSoup import BeautifulSoup as Soup

def getFilmPage(item):
	#http://www.imdb.com/find?q=lol&s=all
	#<p><b>Popular Titles</b> (Displaying 1 Result)<table><tr> <td valign="top"><a href="/title/tt1592873/" onClick="(new Image()).src='/rg/find-tiny-photo-1/title_popular/images/b.gif?link=/title/tt1592873/';"><img src="http://ia.media-imdb.com/images/M/MV5BMTA0MjI5ODA3MjReQTJeQWpwZ15BbWU3MDI1NTE3Njc@._V1._SY30_SX23_.jpg" width="23" height="32" border="0"></a>&nbsp;</td><td align="right" valign="top"><img src="/images/b.gif" width="1" height="6"><br>1.</td><td valign="top"><img src="/images/b.gif" width="1" height="6"><br><a href="/title/tt1592873/" onclick="(new Image()).src='/rg/find-title-1/title_popular/images/b.gif?link=/title/tt1592873/';">LOL</a> (2012)                         <p class="find-aka">aka  "LOL USA" - France <em>(imdb display title)</em></p>   
	#http://www.imdb.com/title/tt1592873/
	try:
		page = urllib2.urlopen("http://www.imdb.com/find?q="+str(urllib2.quote(item))+"&s=all")
		soup = Soup(page)
		result = soup.find("a", {"href":re.compile('^/title/')})
		page = urllib2.urlopen("http://www.imdb.com"+str(result['href']))
		soup = Soup(page)
		return soup
	except urllib2.HTTPError:
		print "IMDB scrape error"

def getGenres(imdbpage):
	#<a onclick="(new Image()).src='/rg/title-overview/genre/images/b.gif?link=%2Fgenre%2FAction';"     href="/genre/Action"    >Action</a>
	#<a onclick="(new Image()).src='/rg/title-overview/genre/images/b.gif?link=%2Fgenre%2FAdventure';"     href="/genre/Adventure"    >Adventure</a>&nbsp;&nbsp;-&nbsp;&nbsp;
	genrelinks = imdbpage.findAll("a", {"href":re.compile('^/genre/')})
	genres = []
	for g in genrelinks:
		if g.string.strip() not in genres:
			genres.append(g.string.strip())
	return genres

def getFullTitle(imdbpage):  #The Expendables 2 (2012) 7.7
	#<h1 class="header" itemprop="name">
	# The Expendables 2
	# 
	# 
	# <span class="nobr">(<a href="/year/2012/">2012</a>)</span>
	# 
	# 
	# 
	# </h1>
	#<span itemprop="ratingValue">7.7</span>
	info = imdbpage.find("h1", {"itemprop":"name"})
	title = str(info)
	title = title[title.find('>')+1:title.find('<span')-1].strip()
	year = info.find("a")
	rating = imdbpage.find("span", {"itemprop":"ratingValue"}).string
	return title + " ("+year.contents[0]+") "+ rating

def makeLinkTo(item, path):
	if not os.path.lexists(path):
		os.symlink(item, path)

def makeGenreFolderFrom(path, genrepath='./FilmsByGenre'):
	#mkdir genrepath+Genres
	if not os.path.exists(genrepath):
		os.makedirs(genrepath)
	for item in os.listdir(path):
		print item
		itempath = os.path.join(path, item)
		if os.path.isdir(itempath):   #The item is a film folder, get details
			page = getFilmPage(item)
			genres = getGenres(page)
			fulltitle = getFullTitle(page)
			for genre in genres:
				if not os.path.exists(os.path.join(genrepath, genre)):
					os.makedirs(os.path.join(genrepath, genre))
				makeLinkTo(itempath,os.path.join(genrepath, genre)+"/"+fulltitle)

if __name__ == '__main__':
	makeGenreFolderFrom('/Users/hurl/Dropbox/Own/Code/IMDBScraper/test')
	# film = getFilmPage("The Expendables 2")
	# genres = getGenres(film)
	# title = getFullTitle(film)