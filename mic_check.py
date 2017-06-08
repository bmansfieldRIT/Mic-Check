# mic_check.py
# usage: python mic_check.py artist_name num_words_to_show

import sys
import requests
import click # used to show a progress bar for requests
from collections import Counter
from bs4 import BeautifulSoup



# removes characters from a set of lyrics before parsing
# Input: BeautifulSoup <p> object array
# Output: String Array
def formatLyricData(unfmtLyrics, fmtLyrics):

	for lyric in unfmtLyrics:

		# convert BeautifulSoup object to a string
		l = lyric.get_text()

		# deal with characters that the charmap can't handle
		l = l.replace(u"\u2019", "").replace(u"\u201c", "").replace(u"\u201d", "").replace(u"\u2018", "")
		l = l.replace("\n", " ").replace("\r", " ").replace("\t", " ")
		l = l.replace("!", "").replace(",", "").replace(")", "").replace("(", "").replace(";", "").replace("*", "").replace("?", "").replace(".", "").replace("\"", "").replace("+", "")

		fmtLyrics.append(l)

	return fmtLyrics


# creates a dictionary to replace common shortenings and misspellings with a proper word
def createMisspellingsDict():
    return dict([("'bout","about"), ("'cause","because"), ("'em","them")])


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
	replacewordsDict = createMisspellingsDict()

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
						if lyric in replacewordsDict:
							if replacewordsDict[lyric] not in lyricDict:
								lyricDict[replacewordsDict[lyric]] = 1
							else:
								lyricDict[replacewordsDict[lyric]] += 1
						else:
							if lyric not in lyricDict:
								lyricDict[lyric] = 1
							else:
								lyricDict[lyric] += 1

def removeDuplicateEntries(lyricDict):
	lyricsMarkedForDeletion = [] # lyrics cannot be deleted in the for loop, so we delete them afterwards
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



def printLyricStatistics(lyricDict, numSongs):
	totalNumWords = sum(lyricDict.values())
	uniqueWords = len(lyricDict)

	print "Total Number of Words Used: " + str(totalNumWords)
	print "Number of Unique Words Used: " + str(uniqueWords)
	print "Average Words Per Song: " + str(totalNumWords / numSongs)
	print "Average Unique Words Per Song: " + str(uniqueWords / numSongs)



def main():

	#
	# retrieve artist lyric data
	#
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

	lyricDict = {}
	songPages = []

	trackLinkList = trackList.findAll("a")
	with click.progressbar(trackLinkList) as bar:
		for song in bar:
			songPage = requests.get(song.get('href')).content
			songPageSoup = BeautifulSoup(songPage, "html.parser")

			lyricsContainer = songPageSoup.find("p", {"id" : "songLyricsDiv"})
			songPages.append(lyricsContainer)

	#
	# Parse lyric data
	#
	print "Parsing lyrics..."
	fmtSongs = []
	formatLyricData(songPages, fmtSongs)

	#
	# Add songs to lyric dictionary
	#
	for song in fmtSongs:
		addSongToLyricDict(song, lyricDict, artistName)

	print "Organizing Lyric Dictionary..."
	removeDuplicateEntries(lyricDict)

	#
	# Output lyric data
	#
	done = False
	while not done:
		prompt = """\nChoose an option:
		1: Print Full Lyric Dictionary (Most Used First)
		2: Print Full Lyric Dictionary (Least Used First)
		3: Print n lyrics (Most Used)
		4: Print n Lyrics (Least Used)
		5: Search For Word
		6: Print Statistics
		7: Write Lyrics to File
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
		elif loopInput == "6":
			printLyricStatistics(lyricDict, len(songPages))
		elif loopInput == "7":
			filename = raw_input("Name of File: ")
			outputFile = open(filename + ".txt", "w")
			print "Writing Lyrics to File..."
			for key, value in sorted(lyricDict.iteritems()):
				outputFile.write(key.encode('utf-8') + ": " + str(value) + "\n")
		elif loopInput == "99":
			exit(1)
		else:
			print "Incorrect Input"

main()
