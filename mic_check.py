# mic_check.py
# usage: python mic_check.py artist_name num_words_to_show

import sys
import requests
from bs4 import BeautifulSoup

# removes characters from a set of lyrics before parsing
def formatLyrics(lyricsObj):

	# deals with characters that charmap can't handle
	lyrics = lyricsObj.get_text().replace(u"\u2019", "").replace(u"\u201c", "").replace(u"\u201d", "").replace(u"\u2018", "").replace("\n", " ").replace("\r", " ")
	# lyrics.replace("!", "").replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace(".", "").replace("\'", "").replace("\"", "").replace(",", "")
	return lyrics

# returns an empty dictionary
def createLyricDict():
	return {}

# note: lyrics sometimes contain tags such as [verse 1: Brian Eno]
# 		to indicate who the lyrics belong to. In this case, the function will
# 		only add blocks of lyrics after a tag contains the given artists name.
#		Otherwise, the songs will have tags such as [verse 2], or no tags at all.
#		By default, this function will assume all lyrics in a song belong to
#		the given artist.
def addSongToLyricDict(lyrics, lyricDict, artistName):

	acceptLyrics = True # indicate whether to count these lyrics as the given singer's
	collectingTagInfo = False
	checkTagAgainstArtist = False

	tagInfo = "" # construct a string representing the tag of a lyric block

	for lyric in lyrics.split(" "):

		# check if the next block of lyrics belongs to the given artist
		if checkTagAgainstArtist:
			if artistName in tagInfo or ":" not in tagInfo: # if the tag does not contain a colon, assume it is the given artists
				acceptLyrics = True
				tagInfo = "" # reset the tag string
			else:
				acceptLyrics = False
			checkTagAgainstArtist = False

		lyric = lyric.lower()

		# test if we are at the beginning of a tag
		if len(lyric) > 0 and lyric[0] == "[":
			tagInfo += lyric
			if lyric[-1] != "]": # test if we are at the end of a tag
				collectingTagInfo = True # set flag to begin collecting tag information
		else:
			if collectingTagInfo:
				# test if we are at the end of a tag
				if len(lyric) > 0 and lyric[-1] == "]":
					collectingTagInfo = False
					checkTagAgainstArtist = True
				tagInfo += " " + lyric
			else:
				if acceptLyrics:
					if lyric not in lyricDict:
						lyricDict[lyric] = 1
					else:
						lyricDict[lyric] = lyricDict[lyric] + 1

def main():

	artistName = ""

	if (len(sys.argv) < 2):
		print "usage: python mic_check.py 'artist_name'"
		exit(1)
	else:
		artist_name = sys.argv[1]

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
