---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2010/12/20/mendeley-android-client-first-preview-and-oauth-problem
categories:
- Technology
- Android
- Academia
comments:
- author: Mr. Gunn
  author_email: william.gunn@mendeley.com
  author_url: ''
  content: Hi Martin! Glad to see you're taking a crack at this. You might want to
    check the mendeley mailing list on google groups for more help on this, but I've
    passed your message along as well
  date: 2010-12-20 22:10:33 +0100
  date_gmt: 2010-12-20 22:10:33 +0100
  id: 5986
- author: Jason Hoyt
  author_email: jason.hoyt@mendeley.com
  author_url: http://mendeley.com/about-us/
  content: "Callbacks are supported with the \"jsonp=YourFunctionName\" argument at
    the end of any method.\r\n\r\nCheers!"
  date: 2010-12-20 23:27:16 +0100
  date_gmt: 2010-12-20 23:27:16 +0100
  id: 5989
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  content: "Thanks to you both; appreciate the feedback and will check the Google
    Groups. In the meantime, if the API team get a chance to look and respond while
    I'm away, I'll continue work when back after Xmas.\r\n\r\nCheers! (and happy holidays!)"
  date: 2010-12-21 06:52:33 +0100
  date_gmt: 2010-12-21 06:52:33 +0100
  id: 5991
- author: Ian Mulvany
  author_email: ian.mulvany@mendeley.com
  author_url: http://www.mendeley.com/profiles/ian-mulvany/
  content: "There are plenty of people in the Mendeley office with andriod phones
    that would love to see this! \r\n\r\nBTW, I love Gravity's Rainbow, and am rather
    a fan of Beckett too, so it's really nice to see someone who is bridging the divide
    between the literary and digital."
  date: 2010-12-22 17:07:06 +0100
  date_gmt: 2010-12-22 17:07:06 +0100
  id: 6001
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  content: Thanks Ian - looking forward to working on this in the new year - any news
    from the API team?
  date: 2010-12-22 17:37:07 +0100
  date_gmt: 2010-12-22 17:37:07 +0100
  id: 6002
- author: Clemens
  author_email: clemens.lombriser@gmail.com
  author_url: ''
  content: "I also just started a small Android using the signpost library to log
    into Mendely. Currently it just reads out my collections and displays them into
    a ListActivity. The code is available here:\r\nhttps://code.google.com/p/droidbiblio"
  date: 2011-01-02 21:02:50 +0100
  date_gmt: 2011-01-02 21:02:50 +0100
  id: 6050
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  content: "Hi Clemens,\r\n\r\nMany thanks for this; sounds good -- I'll give Signpost
    a shot and report back!"
  date: 2011-01-02 21:09:36 +0100
  date_gmt: 2011-01-02 21:09:36 +0100
  id: 6051
date: 2010-12-20 22:00:47 +0100
date_gmt: 2010-12-20 22:00:47 +0100
doi: https://doi.org/10.59348/q61ec-bg742
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Android
- Mendeley
- mendroid
title: Mendeley Android client; first preview and OAuth problem
wordpress_id: 490
wordpress_url: http://www.martineve.com/?p=490
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mlgp3g62t"
---

<p>In the last day before I head off for a bit of a Christmas break, I decided to take up a recent proposition to start work on an Android client for Mendeley. So far, in a couple of hours, I've got as far as implementing the OAuth provider, so you can start the application, log in to Mendeley and it will ask you to authorize the application to access your Mendeley account.</p>
<p><a href="http://www.martineve.com/2010/12/20/mendeley-android-client-first-preview-and-oauth-problem/mendroid-first-problem/" rel="attachment wp-att-491"><img src="http://www.martineve.com/wp-content/uploads/2010/12/mendroid-first-problem.png" alt="Mendroid screenshot" title="Mendroid" width="327" height="484" class="alignnone size-full wp-image-491" /></a></p>
<p>Well, that's the theory... there's a problem, though. Currently the OAuth system will <strong>not</strong> work with the Android browser. I took the same URL and request token, accessing the auth URL in one instance with a desktop client and one instance with an android phone (tried on device -- HTC Wildfire -- and emulator). The desktop PC can get an access code, the Android device cannot.</p>
<p><object width="480" height="385"><param name="movie" value="http://www.youtube-nocookie.com/v/KJshIJOdf5Y?fs=1&amp;hl=en_GB&amp;color1=0x5d1719&amp;color2=0xcd311b"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube-nocookie.com/v/KJshIJOdf5Y?fs=1&amp;hl=en_GB&amp;color1=0x5d1719&amp;color2=0xcd311b" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="480" height="385"></embed></object></p>
<p>Apologies for the quality of that YouTube video, but it does demonstrate the point. As an additional debug procedure, I also ran the working desktop URL to the phone via Chrome to Phone. Same result.</p>
<p>Is Mendeley's API doing something strange based on user agent? Also: does Mendeley's API support a callback URL? (this is kinda crucial for an Android app!)</p>
<p>To try and get some feedback, here's the code it's running for login at present. This code is GPL v3 licensed and I have removed my own keys.</p>

{% highlight java %}
/*
    mendroid: An Android Mendeley client
    Copyright 2010 Martin Paul Eve

    This file is part of Mendroid.

    Mendroid is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    Mendroid is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with Mendroid.  If not, see <http://www.gnu.org/licenses/>.

*/
package com.martineve.mendroid;

import java.io.IOException;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.Map;

import net.oauth.OAuth;
import net.oauth.OAuthAccessor;
import net.oauth.OAuthConsumer;
import net.oauth.OAuthException;
import net.oauth.OAuthMessage;
import net.oauth.OAuthServiceProvider;
import net.oauth.client.OAuthClient;
import net.oauth.client.httpclient4.HttpClient4;
import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.text.Html;
import android.text.method.LinkMovementMethod;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.TextView;

public class MendeleyDroidLogin extends Activity implements OnClickListener {
	
	OAuthAccessor client;
	String access_token;
	String request_token;
	
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        
        Button login_button = (Button) findViewById(R.id.login_button);
        login_button.setOnClickListener(this);
        
        // setup the link in the credits box ;)
        TextView credits = (TextView) findViewById(R.id.login_page_credits);
        credits.setText(Html.fromHtml("Copyright <a href=\"http://www.martineve.com\">Martin Paul Eve</a>, 2011"));
        credits.setMovementMethod(LinkMovementMethod.getInstance());
    }
    
    protected void onResume() {
    	// extract the OAUTH access token if it exists
	    Uri uri = this.getIntent().getData();
	    if(uri != null) {
	    	ProgressDialog dialog = ProgressDialog.show(this, "", 
	                "Logging in to Mendeley, please wait...", true);
	      access_token = uri.getQueryParameter("oauth_token");
	      access_token = convertToAccessToken(client.requestToken);
	      // setDefaultAccessToken(access_token, this); // keep this in the database
	      dialog.cancel();
	    }
	    
	    super.onResume();
	}  
	    
    public String convertToAccessToken(String request_token) {
	    ArrayList<Map.Entry<String, String>> params = new ArrayList<Map.Entry<String, String>>();
	    OAuthClient oclient = new OAuthClient(new HttpClient4());
	    OAuthAccessor accessor = client;
	    params.add(new OAuth.Parameter("oauth_token", request_token));
	    try {
	    OAuthMessage omessage = oclient.invoke(accessor, "POST", accessor.consumer.serviceProvider.accessTokenURL, params);
	    return omessage.getParameter("oauth_token");
	    } catch (Exception ioe) {
	    	return "";
	    }
    }
    
    public void onClick(View v) {
    	// get the request token
    	ProgressDialog dialog = ProgressDialog.show(this, "", 
               "Communicating with Mendeley, please wait...", true);
    	client = defaultClient();
    	
    	dialog.cancel();
    	
    	Intent i = new Intent(Intent.ACTION_VIEW);
    	i.setData(Uri.parse(client.consumer.serviceProvider.userAuthorizationURL +
    	                                  "?oauth_token=" + client.requestToken +
    	                                  "&oauth_callback=" + client.consumer.callbackURL));
    	startActivity(i);
    	                             
    }
    
    OAuthServiceProvider defaultProvider() {
	    return new OAuthServiceProvider("http://www.mendeley.com/oauth/request_token/", "http://www.mendeley.com/oauth/authorize/", "http://www.mendeley.com/oauth/access_token/");
	}

	OAuthAccessor defaultClient() {
	    String callbackUrl = "martineve-mendroid:///";
	    OAuthServiceProvider provider =  defaultProvider();
	    
	    String consumerKey = "CONSUMER_KEY_HERE";
    	String consumerSecret = "CONSUMER_SECRET_HERE";
	    OAuthConsumer consumer = new OAuthConsumer(callbackUrl, consumerKey,
	                                    consumerSecret, provider);
	    OAuthAccessor accessor = new OAuthAccessor(consumer);
	    
    	OAuthClient oaclient = new OAuthClient(new HttpClient4());
    	
    	try {
			oaclient.getRequestToken(accessor);
			request_token = accessor.requestToken;
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (OAuthException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (URISyntaxException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	    
	    return accessor;
	}

}

{% endhighlight %}

<p>For now, I'm off on holiday, but if anyone had any thoughts, I'd love to hear them. Merry Christmas all!</p>