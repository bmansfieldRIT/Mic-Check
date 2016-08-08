# mic_check.py
# usage: python mic_check.py artist_name num_words_to_show
# flags: -most (show most used words), -least (show least words used), -

import sys
import requests
from bs4 import BeautifulSoup

def formatLyrics(lyricsObj):

	# deals with characters that charmap can't handle
	lyrics = lyricsObj.get_text().replace(u"\u2019", "").replace(u"\u201c", "").replace(u"\u201d", "").replace(u"\u2018", "").replace("\n", " ").replace("\r", " ")
	lyrics.replace("!", "").replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace(".", "").replace("\'", "").replace("\"", "").replace(",", "")
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

	artist_name = ""
	num_words_to_show = ""

	if (len(sys.argv) !=  3):
		print "usage: python mic_check.py 'artist_name' 'num_words_to_show'"
		exit(1)
	else:
		artist_name = sys.argv[1]
		num_words_to_show = sys.argv[2]

	print artist_name
	artist_name = artist_name.replace(" ", "-")
	print artist_name
	formattedRequestURL = "https://www.songlyrics.com/" + artist_name + "-lyrics/"

	page = requests.get(formattedRequestURL).content
	artistPage = BeautifulSoup(page, "html.parser")
	trackList = artistPage.find("table", {"class" : "tracklist"})

	lyricDict = createLyricDict()
	songPages = []

	for song in trackList.findAll("a"):
		songPage = requests.get(song.get('href')).content
		songPageSoup = BeautifulSoup(songPage, "html.parser")

		lyricsContainer = songPageSoup.find("p", {"id" : "songLyricsDiv"})
		# img_tags = lyricsContainer.img.extract()
		lyrics = formatLyrics(lyricsContainer)
		songPages.append(lyrics)

	for songPage in songPages:
		addSongToLyricDict(songPage, lyricDict)


	for word in sorted(lyricDict, key=lyricDict.get, reverse=True):
  		print word, lyricDict[word]
	# print lyricDict

main()
