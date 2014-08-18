import easygui as eg
import scLikesDownloader

### Begin operations
PATH = ''
sc = scLikesDownloader.downloader('http://www.soundcloud.com/waltermorrison', PATH)


favorites = sc.trackList()
x = 0
while(x < len(favorites)):
    print 'Saving file ' + str(x) + ' of ' + str(len(favorites)-1)
    result = sc.saveFile(favorites[x])
    if result:
        x += 1
    else:
        print 'Retrying #' + str(x) + ' | '
        
        break

print 'Save Completed'
print 'Displaying error reports.... if none are displayed this was a complete success!'

if (len(sc.reports) > 0):
    for report in sc.reports:
        print report
