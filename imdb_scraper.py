#!/bin/python
import os,re,urllib,urllib2
import HTMLParser
from BeautifulSoup import BeautifulSoup as Soup

def getFilmPage(item):
	#http://www.imdb.com/find?q=lol&s=all
	#<p><b>Popular Titles</b> (Displaying 1 Result)<table><tr> <td valign="top"><a href="/title/tt1592873/" onClick="(new Image()).src='/rg/find-tiny-photo-1/title_popular/images/b.gif?link=/title/tt1592873/';"><img src="http://ia.media-imdb.com/images/M/MV5BMTA0MjI5ODA3MjReQTJeQWpwZ15BbWU3MDI1NTE3Njc@._V1._SY30_SX23_.jpg" width="23" height="32" border="0"></a>&nbsp;</td><td align="right" valign="top"><img src="/images/b.gif" width="1" height="6"><br>1.</td><td valign="top"><img src="/images/b.gif" width="1" height="6"><br><a href="/title/tt1592873/" onclick="(new Image()).src='/rg/find-title-1/title_popular/images/b.gif?link=/title/tt1592873/';">LOL</a> (2012)                         <p class="find-aka">aka  "LOL USA" - France <em>(imdb display title)</em></p>   
	#http://www.imdb.com/title/tt1592873/
	try:
		film = item.replace(' III',' 3')
		film = film.replace(' II',' 2')
		film = film.replace(' I',' 1')
		film = film.replace(' IV',' 4')
		film = film.replace(' VI',' 5')
		film = urllib2.quote(film)
		page = urllib2.urlopen("http://www.imdb.com/find?q="+str(film)+"&s=all")
		soup = Soup(page)
		if soup.find("h1", {"itemprop":"name"}) != None:
			return soup
		result = soup.find("a", {"href":re.compile('^/title/')})
		try:
			page = urllib2.urlopen("http://www.imdb.com"+str(result['href']))
			soup = Soup(page)
			return soup
		except Exception, e:
			return None
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
	if title != 'None':
		title = title[title.find('>')+1:title.find('<span')-1].strip()
		title = urllib2.unquote(title)
		try:
			year = info.find("a")
			year = year.contents[0]
		except AttributeError:
			year = title[title.rfind('('):]
		try:
			rating = imdbpage.find("span", {"itemprop":"ratingValue"}).string
		except AttributeError:
			rating = ""
	else:
		title = str(imdbpage)
		fo = open('r.html','w')
		fo.write(title)
		title = title[title.find('itemprop="name">')+20:]
		title = title[:title.find('<')-1].strip()
		year = str(imdbpage)
		year = year[year.find('<a href="/year/')+17:year.find('<a href="/year/')+21]
		rating = str(imdbpage)
		rating = rating[rating.find('ratingValue">')+13:]
		rating = rating[:rating.find('<')-1]
	print HTMLParser.HTMLParser().unescape(title + " ("+year+") "+ rating)
	return HTMLParser.HTMLParser().unescape(title + " ("+year+") "+ rating)

def makeLinkTo(item, path):
	if not os.path.lexists(path):
		try:
			os.symlink(item, path)
		except Exception, e:
			print "SYMLINK ERROR - "+ item + "=" + path

def makeGenreFolderFrom(path, genrepath='./FilmsByGenre'):
	#mkdir genrepath+Genres
	if not os.path.exists(genrepath):
		os.makedirs(genrepath)
	for item in os.listdir(path):
		itempath = os.path.join(path, item)
		if os.path.isdir(itempath):   #The item is a film folder, get details
			page = getFilmPage(item)
			if page == None:
				print str(item) + " not found on IMDB."
				continue
			genres = getGenres(page)
			fulltitle = getFullTitle(page)
			for genre in genres:
				if not os.path.exists(os.path.join(genrepath, genre)):
					os.makedirs(os.path.join(genrepath, genre))
				makeLinkTo(itempath,os.path.join(os.path.join(genrepath, genre),fulltitle))

if __name__ == '__main__':
	makeGenreFolderFrom('/Volumes/Series/')
	# film = getFilmPage("The Expendables 2")
	# genres = getGenres(film)
	# title = getFullTitle(film)