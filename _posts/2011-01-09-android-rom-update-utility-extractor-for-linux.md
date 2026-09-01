---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/01/09/android-rom-update-utility-extractor-for-linux
categories:
- Linux
- Programming
comments:
- author: Tweets that mention Android Rom Update Utility extractor for Linux | Martin
    Paul Eve -- Topsy.com
  author_email: ''
  author_url: http://topsy.com/trackback?url=https%3A%2F%2Fwww.martineve.com%2F2011%2F01%2F09%2Fandroid-rom-update-utility-extractor-for-linux%2F&amp;utm_source=pingback&amp;utm_campaign=L2
  content: '[...] This post was mentioned on Twitter by jean marc, Pau Oliva. Pau
    Oliva said: Android Rom Update Utility (RUU) extractor for Linux - http://x90.es/nj
    [...]'
  date: 2011-02-04 12:41:59 +0100
  date_gmt: 2011-02-04 12:41:59 +0100
  id: 6165
date: 2011-01-09 08:16:21 +0100
date_gmt: 2011-01-09 08:16:21 +0100
doi: https://doi.org/10.59348/wzhqv-xpg98
roguescholar: https://rogue-scholar.org/records/02td5-b5d22
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mkxgfft2i
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Android
- Linux
- ROM
title: Android Rom Update Utility extractor for Linux
wordpress_id: 535
wordpress_url: http://www.martineve.com/?p=535
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mkxgfft2i"
---

<p>As my hobby-geek phase draws to a close and I return well and truly to my PhD, I thought it worth sharing this python script I wrote a while back which will extract the update.zip file from an Android RUU.exe file on Linux. There are other items out there that do the same thing, but this is my effort.</p>
<p>Usage: modify the options, start the script and then run the RUU under Wine.</p>

{% highlight python %}
#!/usr/bin/python

'''
    ROM Extractor Copyright (c) 2010 Martin Paul Eve
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import pyinotify
import io

# USERNAME = REQUIRED
username = "martin"

# Modify these if using a different format; HTC seem to go by this standard
filename = "rom.zip"
monitor_path = "~/.wine/drive_c/users/%s/Temp/" % username


wm = pyinotify.WatchManager()
mask = pyinotify.IN_CREATE | pyinotify.IN_MODIFY | pyinotify.IN_DELETE | pyinotify.IN_MOVED_TO
bd = None

class RExtract(pyinotify.ProcessEvent):
	def process_IN_MOVED_TO(self, event):
		 if event.name.endswith(filename):
	 		 print "Found ROM. Awaiting completion of modification."
	 		 self.f = open(os.path.join(event.path, event.name), "r")
	 		 self.bd = self.f.read()
	def process_IN_CREATE(self, event):
		 if event.name.endswith(filename):
	 		 print "Found ROM. Awaiting completion of modification."
	 		 self.f = open(os.path.join(event.path, event.name), "r")
	def process_IN_MODIFY(self, event):
	 if event.name.endswith(filename):
	 	 if hasattr(self, "bd"):
			 self.bd = self.bd + self.f.read()
		 else:
			 self.bd = self.f.read()
 	def process_IN_DELETE(self, event):
 		 if event.name.endswith(filename):
			 self.f.close()
	 		 self.f = open(os.path.join("/home/%s/" % username, "rom.zip"), "w")
	 		 self.f.write(self.bd)
	 		 self.f.close()
			 print "ROM Copied"
	 		 raise KeyboardInterrupt

notifier = pyinotify.Notifier(wm, RExtract())
print "ROM Extractor Copyright (c) 2010 Martin Paul Eve"
print "This program comes with ABSOLUTELY NO WARRANTY."
print "This is free software, and you are welcome to redistribute it under certain conditions; see the included licence statement"
print ""
print "Monitoring: %(path)s for %(filename)s" % {"path": os.path.expanduser(monitor_path), "filename": filename}
print "Press CTRL+C to exit"

wdd = wm.add_watch(os.path.expanduser(monitor_path), mask, rec=True, auto_add=True)

while True:
	try:
	 notifier.process_events()
	 if notifier.check_events():
		notifier.read_events()
	except KeyboardInterrupt:
	 notifier.stop()
	 break

{% endhighlight %}