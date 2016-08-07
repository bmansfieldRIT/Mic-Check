# mic_check.py

import requests
from bs4 import BeautifulSoup

def printLyrics(lyricsObj):

	lyrics = lyricsObj.get_text().replace(u"\u2019", "").replace(u"\u201c", "").replace(u"\u201d", "").replace(u"\u2018", "")
	print lyrics
		
def main():
	page = requests.get("https://www.songlyrics.com/kendrick-lamar-lyrics/").content
	artistPage = BeautifulSoup(page, "html.parser")
	trackList = artistPage.find("table", {"class" : "tracklist"})

	for song in trackList.findAll("a"):
		songPage = requests.get(song.get('href')).content
		songPageSoup = BeautifulSoup(songPage, "html.parser")
		lyricsContainer = songPageSoup.find("p", {"id" : "songLyricsDiv"})
		img_tags = lyricsContainer.img.extract()
		printLyrics(lyricsContainer)
		
main()

