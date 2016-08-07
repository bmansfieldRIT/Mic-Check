# mic_check.py

import requests
from bs4 import BeautifulSoup

def formatLyrics(lyricsObj):

	# deals with characters that charmap can't handle
	lyrics = lyricsObj.get_text().replace(u"\u2019", "").replace(u"\u201c", "").replace(u"\u201d", "").replace(u"\u2018", "").replace("\n", " ").replace("\r", " ")
	return lyrics
	
def createLyricDict():
	return {}
	
def addSongToLyricDict(lyrics, lyricDict):
	for lyric in lyrics.split(" "):
		lyric = lyric.lower()
		if lyric not in lyricDict:
			lyricDict[lyric] = 1
		else:
			lyricDict[lyric] = lyricDict[lyric] + 1
		
def main():

	# example artist 
	page = requests.get("https://www.songlyrics.com/kendrick-lamar-lyrics/").content
	artistPage = BeautifulSoup(page, "html.parser")
	trackList = artistPage.find("table", {"class" : "tracklist"})
	
	lyricDict = createLyricDict()

	for song in trackList.findAll("a"):
		songPage = requests.get(song.get('href')).content
		songPageSoup = BeautifulSoup(songPage, "html.parser")
		
		lyricsContainer = songPageSoup.find("p", {"id" : "songLyricsDiv"})
			#img_tags = lyricsContainer.img.extract()
		lyrics = formatLyrics(lyricsContainer)
		
		addSongToLyricDict(lyrics, lyricDict)
	
	print lyricDict
		
main()

