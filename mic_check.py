# mic_check.py
# usage: python mic_check.py artist_name num_words_to_show

import sys
import requests
import click # used to show a progress bar for requests
from collections import Counter
from bs4 import BeautifulSoup

# removes characters from a set of lyrics before parsing
def formatLyrics(lyricsObj):

	# deals with characters that charmap can't handle
	lyrics = lyricsObj.get_text().replace(u"\u2019", "").replace(u"\u201c", "").replace(u"\u201d", "").replace(u"\u2018", "").replace("\n", " ").replace("\r", " ")
	lyrics = lyrics.replace("!", "").replace(",", "")
	return lyrics

# returns an empty dictionary
def createLyricDict():
	return {}

# note: lyrics sometimes contain tags such as [verse 1: Brian Eno]
# 	to indicate who the lyrics belong to. In this case, the function will
# 	only add blocks of lyrics after a tag contains the given artists name.
#	Otherwise, the songs will have tags such as [verse 2], or no tags at all.
#	By default, this function will assume all lyrics in a song belong to
#	the given artist.
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
		if len(lyric) > 0:
			if lyric[0] == "[":
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
							lyricDict[lyric] += 1

def removeDuplicateEntries(lyricDict):
	lyricsMarkedForDeletion = [] # lyrics cannot be deleted in the for loop marking them as duplicates, so we delete them afterwards
	for lyric in lyricDict:
		if (lyric[-1] == "s" and lyric[:len(lyric) - 1] in lyricDict):
			lyricDict[lyric[:len(lyric) - 1]] += lyricDict[lyric]
			lyricsMarkedForDeletion.append(lyric)
	for markedLyric in lyricsMarkedForDeletion:
		del lyricDict[markedLyric]

def printLyricDict(lyricDict, leastCommonBool, numWords):
	counterDict = Counter(lyricDict)
	if not leastCommonBool:
		for k, v in counterDict.most_common(numWords):
			print '%s: %i' % (k, v)
	else:
		for k, v in counterDict.most_common(len(counterDict))[:-(numWords+1):-1]:
			print '%s: %i' % (k, v)

def main():

	artistName = ""

	if (len(sys.argv) < 2):
		print "usage: python mic_check.py 'artist_name'"
		exit(1)
	else:
		artistName = sys.argv[1]

	fmtArtistName = artistName.replace(" ", "-")
	formattedRequestURL = "https://www.songlyrics.com/" + fmtArtistName + "-lyrics/"

	page = requests.get(formattedRequestURL).content
	artistPage = BeautifulSoup(page, "html.parser")

	print "Retreiving " + artistPage.title.get_text().title() + "..."
	print "** Not the artist you were looking for? Check spelling and generally remove all punctuation **"
	trackList = artistPage.find("table", {"class" : "tracklist"})

	lyricDict = createLyricDict()
	songPages = []

	trackLinkList = trackList.findAll("a")
	with click.progressbar(trackLinkList) as bar:
		for song in bar:
			songPage = requests.get(song.get('href')).content
			songPageSoup = BeautifulSoup(songPage, "html.parser")

			lyricsContainer = songPageSoup.find("p", {"id" : "songLyricsDiv"})
			# img_tags = lyricsContainer.img.extract()
			lyrics = formatLyrics(lyricsContainer)
			songPages.append(lyrics)

	print "Parsing lyrics..."
	for songPage in songPages:
		addSongToLyricDict(songPage, lyricDict, artistName)

	print "Organizing Lyric Dictionary..."
	removeDuplicateEntries(lyricDict)

	done = False
	while not done:
		prompt = """\nChoose an option:
		1: Print Full Lyric Dictionary (Most Used First)
		2: Print Full Lyric Dictionary (Least Used First)
		3: Print n lyrics (Most Used)
		4: Print n Lyrics (Least Used)
		5: Search For Word
		99: Exit \n"""

		loopInput = raw_input(prompt)

		if loopInput == "1":
			printLyricDict(lyricDict, True, len(lyricDict))
		elif loopInput == "2":
			printLyricDict(lyricDict, False, len(lyricDict))
		elif loopInput == "3":
			numLyricsInput = int(raw_input("Number of Lyrics to Print: "))
			printLyricDict(lyricDict, False, numLyricsInput)
		elif loopInput == "4":
			numLyricsInput = int(raw_input("Number of Lyrics to Print: "))
			printLyricDict(lyricDict, True, numLyricsInput)
		elif loopInput == "5":
			searchTermInput = raw_input("Word to Search For: ")
			if searchTermInput not in lyricDict:
				print "Number of Times Word Used: %i" % 0
			else:
				print "Number of Times Word Used: %i" % lyricDict[searchTermInput]
		elif loopInput == "99":
			exit(1)
		else:
			print "Incorrect Input"

main()
