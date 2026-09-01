---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/01/08/automated-cpanel-backups-with-scp
categories:
- Programming
comments:
- author: Vanessa
  author_email: admin@v-nessa.net
  author_url: http://v-nessa.net
  content: Very nice! I don't think I've updated my original script since 2006!
  date: 2011-01-14 15:00:08 +0100
  date_gmt: 2011-01-14 15:00:08 +0100
  id: 6115
- author: Jon
  author_email: ferrari_41@hotmail.com
  author_url: ''
  content: 'Hi Thank you for the script. I tried to run it by it came up with error
    message: please check the host hostname.com and username and password) I can confirm
    that host, user name and password were all correct. I could run it from the control
    panel. Are you able to help? Regards Jon'
  date: 2011-07-25 14:20:00 +0200
  date_gmt: 2011-07-25 14:20:00 +0200
  id: 6509
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: https://www.martineve.com
  content: 'So, just to confirm, you have changed the username, password and host
    in the script? What version of CPanel are you using? The $skin variable must be
    set to correctly refer to this. '
  date: 2011-07-25 14:28:00 +0200
  date_gmt: 2011-07-25 14:28:00 +0200
  id: 6510
date: 2011-01-08 08:41:32 +0100
date_gmt: 2011-01-08 08:41:32 +0100
doi: https://doi.org/10.59348/d16y8-w8w12
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Backup
title: Automated CPanel Backups with SCP
wordpress_id: 531
wordpress_url: http://www.martineve.com/?p=531
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mkxvjyi2p"
---

<p>Originally from <a href="http://www.v-nessa.net/2007/01/03/cpanel-automated-backup-script">V-Nessa's site</a>, I thought I would share the PHP script that I have now modified to include Secure Copy (SCP) support.</p>

{% highlight php %}
<?php



// PHP script to allow periodic cPanel backups automatically.

// Permissions on this file should be 600 

// Place outside your public_html 

// Crontab:  30 3 * * * /usr/local/bin/php /home/username/cpanel_backup.php



// ********* Configuration *********



// Info required for cPanel access

$cpuser = "username"; // Username used to login to CPanel

$cppass = "password"; // Password used to login to CPanel

$domain = "domain.com"; // Domain name where CPanel is run

$skin = "x3"; // Set to cPanel skin you use (script won't work if it doesn't match)



// Info required for SCP host

$ftpuser = "scpuser"; // Username for SCP account

$ftppass = "scppass"; // Password for SCP account

$ftphost = "scp.host.com"; // Full hostname or IP address for SCP host

$port = "22";

$ftpmode = "scp"; // FTP mode ("ftp" for active, "passiveftp" for passive, "scp" for scp)
$rdir = "/home/yourusername/Backup/";
 // make sure this folder exists on the destination host


// Notification information

$notifyemail = "you@youremail.com"; // Email address to send results



// Secure or non-secure mode

$secure = 0; // Set to 1 for SSL (requires SSL support), otherwise will use standard HTTP



// Set to 1 to have web page result appear in your cron log

$debug = 1;



// *********** Don't Touch!! *********



if ($secure) {

   $url = "ssl://".$domain;

   $port = 2083;

} else {

   $url = $domain;

   $port = 2082;

}



$socket = fsockopen($url,$port);

if (!$socket) { echo "Failed to open socket connection... Bailing out!\n"; exit; }



// Encode authentication string

$authstr = $cpuser.":".$cppass;

$pass = base64_encode($authstr);



$params = "dest=$ftpmode&rdir=$rdir&email=$notifyemail&server=$ftphost&port=$port&user=$ftpuser&pass=$ftppass&submit=Generate Backup";



// Make POST to cPanel

fputs($socket,"POST /frontend/".$skin."/backup/dofullbackup.html?".$params." HTTP/1.0\r\n");

fputs($socket,"Host: $domain\r\n");

fputs($socket,"Authorization: Basic $pass\r\n");

fputs($socket,"Connection: Close\r\n");

fputs($socket,"\r\n");



// Grab response even if we don't do anything with it.

while (!feof($socket)) {

  $response = fgets($socket,4096);

  if ($debug) echo $response;

}



fclose($socket);



?>
{% endhighlight %}

<p>If you need help with usage, it's exactly the same as in V_Nessa's original post, so read there, but now supports copying to a remote host over SSH.</p>