---
title: "How to securely create an encrypted digital 'in case of death' document"
layout: post
image:
  feature: header_time.png
doi: "https://doi.org/10.59348/qjt3f-eg160"
archive: "https://wayback.archive-it.org/22123/20241101171236/https://eve.gd/2025/02/16/how-to-securely-create-an-encrypted-digital-in-case-of-death-document"
---
Very few people like thinking about the fact they will die. But it can prove a substantial administrative headache to loved ones if they don't know about all of your finances, your passwords, your emails etc. At the same time, you shouldn't be writing down passwords in any document that could be stolen or seen; it's bad cybersecurity practice. So what can you do?

First, I should say, this blog post is NOT about what to put in the document that you encrypt. There are [lots of other](https://rossnaylor.com/build-a-death-folder/) good sites for that. This is a guide to the technical side of it.

First, what do you need?:

* Some kind of shared [Dropbox](https://www.dropbox.com/home) (or similar) folder
* [gpg: the GNU Privacy Guard](https://www.gnupg.org/) -- an interface to using PGP
* Your document in some widely accessible format, like MS Word

So, the first step is to encrypt your document. You do this as follows (from the command line -- [you may be able to do this using a GUI](https://www.gnupg.org/software/frontends.html)):

	gpg -c ./your-file.doc

At this point, gpg will ask you for a password. Enter a hard-to-guess secure phrase and make sure you remember it.

Then, place the file in the shared Dropbox folder.

You then need to give that password to a trusted individual (or several individuals) with the instruction to pass it on to whoever you nominate if they ever ask for it. I believe the IDEAL would be to lodge this with a lawyer, but very trusted friends will also do.

Then: how does the designated person get access? Well, first they obtain the password from your friends/lawyer.

First, you need to make sure, using their Android phone (sorry, I don't know about iPhone) that they have access to your shared Dropbox folder. You should also install the "[OpenKeyChain](https://play.google.com/store/apps/details?id=org.sufficientlysecure.keychain&hl=en)” app on their device.

Create a document with this info:

> Get the password from Trusted Person: email@gmail.com, +44 1234 56789
 
> Install and then go to the app “OpenKeyChain” on your phone (this works for Android, unsure about iPhones).
 
> Press the menu bar at the side.
 
> Press “Encrypt/Decrypt”.
 
> Under “Decrypt/Verify” press Select input file.
 
> Navigate on the left hand menu there (press the three horizontal lines at the top left) to “Dropbox”.
 
> Go the “FOLDER NAME HERE" and then “SUB-FOLDER HERE” folder.

> Select the file “Accounts.doc.gpg”.

> Enter the password when prompted.

> Open in Google Docs.

> All other files in that directory ending in .gpg can also be decrypted following the same principle.

You can also have a backup plan:

> Send the above file (Go to Dropbox, go to “FOLDER, go to SUB-FOLDER” and share the file “Accounts.doc.gpg” by email: email@gmail.com) to Friend. Ask him to decrypt with “gpg  Accounts.doc.gpg".

,,, and hurrah! You've now got a secure system for transmitting information after you die. Also: don't forget to delete the original file that contains the sensitive data.