---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2009/02/01/ftp-url-fastsnap-parsing-in-net
categories:
- Programming
comments: []
date: 2009-02-01 06:04:10 +0100
date_gmt: 2009-02-01 06:04:10 +0100
doi: https://doi.org/10.59348/11rxw-mwh37
roguescholar: https://rogue-scholar.org/records/e2y39-djh96
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mmkriyl2n
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- .NET
- C#
- FastSnap
- FTP
title: FTP URL FastSnap Parsing in .NET
wordpress_id: 236
wordpress_url: http://pro.grammatic.org/post-ftp-url-fastsnap-parsing-in-net-66.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mmkriyl2n"
kcworks: https://works.hcommons.org/records/dzda7-cqn18
references:
- http://thedailywtf.com # The Daily WTF programming horror site
- http://thedailywtf.com/Articles/The-Backup-Snippet.aspx # The Daily WTF: The Backup Snippet article
---

<p>Sometimes, the built in functions of a framework are good enough for your purpose and there is no point in reinventing the wheel. Fine examples of this are to be found at <a href="http://thedailywtf.com">The Daily WTF</a>, one of my personal faves being <a href="http://thedailywtf.com/Articles/The-Backup-Snippet.aspx">The Backup Snippet</a>.</p>
<p>However, sometimes the .NET Framework does a poor job of parsing FTP FastSnap URLs. For instance, ftp://ausername:apassword@IP:port/path. This is especially evident when the IP is given in non-dotted decimal representation.</p>
<p>The following function attempts to parse a FastSnap using the inbuilt Framework. If that fails, it tries a custom procedure that is sometimes able to catch some of the failed entries. It's by no means perfect, but it can give some additional flexibility.</p>

{% highlight csharp %}
using System;
using System.Collections.Generic;
using System.Text;
using System.Text.RegularExpressions;

// SNIP: namespace and class declarations

        /// <summary>
        /// Parses an FTP URL into its components
        /// </summary>
        /// <param name="fastSnap">The input ftp:// URL</param>
        /// <returns>A Dictionary containing host, port, username, password and path</returns>
        public static Dictionary<string, string> GetFastSnap(string fastSnap)
        {
            // remove whitespace
            fastSnap = fastSnap.Trim();

            // check for ftp:// at start
            if (!fastSnap.StartsWith("ftp://"))
                fastSnap = string.Format("ftp://{0}", fastSnap);

            // check for non-existent login information
            if (Regex.IsMatch(fastSnap, "^ftp://[^:@]*:[0-9]{1,5}$|^ftp://[^:@]*:[0-9]{1,5}/.*$"))
                fastSnap = fastSnap.Replace("ftp://", string.Format("ftp://anonymous:anonymous@{0}", fastSnap));

            // remove surplus double slash
            if (fastSnap.EndsWith("//"))
                fastSnap = fastSnap.TrimEnd('/');

            // check for a trailing slash
            if (!fastSnap.EndsWith("/"))
                fastSnap += "/";

            // try and parse using the in-built Framework function
            try
            {
                Uri ftpUri = new Uri(fastSnap);

                // construct the return object
                Dictionary<string, string> ftpInfoParsed = new Dictionary<string, string>();

                if (ftpUri.UserInfo != string.Empty)
                {
                    ftpInfoParsed.Add("username", ftpUri.UserInfo.Split(':')[0]);
                    ftpInfoParsed.Add("password", ftpUri.UserInfo.Split(':')[1]);
                }
                else
                {
                    ftpInfoParsed.Add("username", "anonymous");
                    ftpInfoParsed.Add("password", "anonymous");
                }

                ftpInfoParsed.Add("host", ftpUri.Host);
                ftpInfoParsed.Add("port", ftpUri.Port.ToString());
                ftpInfoParsed.Add("path", ftpUri.PathAndQuery);

                return ftpInfoParsed;
            }
            catch (Exception)
            {
            }

            // ascertain various positions within the string
            int firstColon = fastSnap.IndexOf(':', 6);
            int atSymbol = fastSnap.IndexOf('@', firstColon);
            int secondColon = fastSnap.IndexOf(':', atSymbol);

            // non-existent port information
            if (secondColon == -1)
            {
                secondColon = firstColon + 1;
            }

            int forwardSlash = fastSnap.IndexOf('/', secondColon);

            // construct the return object
            Dictionary<string, string> ftpInfo = new Dictionary<string, string>();

            // add the fields
            ftpInfo.Add("username", fastSnap.Substring(6, firstColon - 6));
            ftpInfo.Add("password", fastSnap.Substring(firstColon + 1, atSymbol - firstColon - 1));
            
            // if no port was specified, we use different offsets
            if (secondColon == firstColon + 1)
            {
                ftpInfo.Add("host", fastSnap.Substring(atSymbol + 1, forwardSlash - atSymbol - 1));
                ftpInfo.Add("port", "21");
            }
            else
            {
                ftpInfo.Add("host", fastSnap.Substring(atSymbol + 1, secondColon - atSymbol - 1));
                ftpInfo.Add("port", fastSnap.Substring(secondColon + 1, forwardSlash - secondColon - 1));
            }
            
            if (forwardSlash < fastSnap.Length - 1)
            {
                ftpInfo.Add("path", fastSnap.Substring(forwardSlash + 1, fastSnap.Length - forwardSlash - 1));
            }
            else
            {
                ftpInfo.Add("path", "/");
            }

            return ftpInfo;

        }
{% endhighlight %}