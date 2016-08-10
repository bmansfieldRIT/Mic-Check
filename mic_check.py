# mic_check.py
# usage: python mic_check.py artist_name num_words_to_show
# flags: -most (show most used words), -least (show least words used)

import sys
import requests
from bs4 import BeautifulSoup

def formatLyrics(lyricsObj):

	# deals with characters that charmap can't handle
	lyrics = lyricsObj.get_text().replace(u"\u2019", "").replace(u"\u201c", "").replace(u"\u201d", "").replace(u"\u2018", "").replace("\n", " ").replace("\r", " ")
	# lyrics.replace("!", "").replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace(".", "").replace("\'", "").replace("\"", "").replace(",", "")
	return lyrics

def createLyricDict():
	return {}

def addSongToLyricDict(lyrics, lyricDict, artistName):
	acceptLyrics = True # indicate whether to count these lyrics as the given singer's
	collectingTagInfo = False
	checkTagAgainstArtist = False
	tagInfo = "" # construct a string determining the singer of a block of lyrics ex. [verse 1: A Singer]
	for lyric in lyrics.split(" "):

		if checkTagAgainstArtist:
			if artistName in tagInfo or ":" not in tagInfo:
				acceptLyrics = True
				tagInfo = ""
			else:
				acceptLyrics = False
			checkTagAgainstArtist = False


		lyric = lyric.lower()
		if len(lyric) > 0 and lyric[0] == "[":
			tagInfo += lyric
			if lyric[-1] != "]":
				collectingTagInfo = True

		else:
			if collectingTagInfo:
				if len(lyric) > 0 and lyric[-1] == "]":
					tagInfo += " " + lyric
					collectingTagInfo = False
					checkTagAgainstArtist = True
					print tagInfo
				else:
					tagInfo += " " + lyric
			else:
				if acceptLyrics:
					if lyric not in lyricDict:
						lyricDict[lyric] = 1
					else:
						lyricDict[lyric] = lyricDict[lyric] + 1

def main():

	artist_name = ""
	num_words_to_show = ""
	num_lyrics_order = ""

	if (len(sys.argv) <  3):
		print "usage: python mic_check.py 'artist_name' num_words_to_show"
		exit(1)
	else:
		artist_name = sys.argv[1]
		num_words_to_show = sys.argv[2]

	fmt_artist_name = artist_name.replace(" ", "-")
	formattedRequestURL = "https://www.songlyrics.com/" + fmt_artist_name + "-lyrics/"

	page = requests.get(formattedRequestURL).content
	artistPage = BeautifulSoup(page, "html.parser")

	print "Retreiving " + artistPage.title.get_text().title() + "..."
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

	print "Parsing lyrics..."
	for songPage in songPages:
		addSongToLyricDict(songPage, lyricDict, artist_name)


	# for word in sorted(lyricDict, key=lyricDict.get, reverse=True):
  	#	print word, lyricDict[word]
	# print lyricDict

main()
