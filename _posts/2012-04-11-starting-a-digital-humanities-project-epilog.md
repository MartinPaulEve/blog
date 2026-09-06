---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2012/04/11/starting-a-digital-humanities-project-epilog
categories:
- Digital Humanities
- Programming
comments:
- author: Erik
  author_email: erik@erik.com
  author_url: ''
  content: "Sounds interesting, Martin. I'll be interested to follow your progress.\r\n\r\nOne
    thing I learned from working on the Pynchon Wiki and my own subsequent projects,
    though, is that you've got to make the barrier to contributions as small as possible.
    Even a whiff of \"Huh?\" and I suspect that many potential contributors get turned
    off from creating an account or even browsing the site.\r\n\r\nThat said: \"objects\".
    I get that this is at the core of your concept, but I'm a guy invited to conferences
    to talk about annotation wikis and even *I* get a whiff of \"Huh?\". What's your
    average contributor gonna think?\r\n\r\nIf you mean books, movies, and plays,
    just say so. Keep \"objects\" off the intro page. Let the user just dive in, like
    in Wikipedia. Show why they should bother visiting the site (good content) and
    why they should contribute (ditto). Regular contributors or advanced users can
    be introduced to the object concept or find it themselves after they join. They
    can then explore what the \"object\" concept can do for all that content.\r\n\r\nI
    personally believe you shouldn't spend too much time worrying about structure
    / organization of the content a priori. The content needs to come first. Spending
    a ton of energy on complex organizational structures (layers, how I break down
    an object -- by page, chapter, individual shot --, how they connect, etc.) before
    there's any content to fill them is the mistake made by a hundred digital humanities
    projects that no one ever visits or contributes to.\r\n\r\nStart by adding a ton
    of your own annotations. Once there's enough content, then you and users can worry
    about how to link it all in ways and structures THAT ARE ACTUALLY USEFUL TO USERS.
    Clearly you're onto some interesting concepts here but be careful about putting
    the cart before the horse.\r\n\r\nJust my two cents-- Looks like you're off to
    a great start.\r\n\r\nE"
  date: 2012-04-11 11:01:57 +0200
  date_gmt: 2012-04-11 11:01:57 +0200
  id: 6681
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  content: Great points, Erik! I'm going to digest this a heap more and think through
    how best to re-work it. I agree about own annotations being the kickstart, but
    I have to build the infrastructure first ;) Thanks again!
  date: 2012-04-11 11:03:49 +0200
  date_gmt: 2012-04-11 11:03:49 +0200
  id: 6682
- author: Erik
  author_email: erik@erik.com
  author_url: ''
  content: "Thanks-- keep working hard and I can't wait to see the results.\r\n\r\nI'll
    add annotations on anything other than Foucault :)\r\n\r\nE"
  date: 2012-04-11 11:24:22 +0200
  date_gmt: 2012-04-11 11:24:22 +0200
  id: 6683
date: 2012-04-11 10:00:40 +0200
last_modified_at: 2026-09-06
date_gmt: 2012-04-11 10:00:40 +0200
doi: https://doi.org/10.59348/pg8jt-da988
roguescholar: https://rogue-scholar.org/records/fappe-1xc23
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mihn2ge2h
layout: post
published: true
status: publish
tags:
- Technology
- Digital Humanities
title: 'Starting a Digital Humanities Project: epiLog'
wordpress_id: 2029
wordpress_url: https://www.martineve.com/?p=2029
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mihn2ge2h"
kcworks: https://works.hcommons.org/records/cvmkx-8ph71
references:
- title: epiLog/epiLog at master · MartinPaulEve/epiLog
  type: SoftwareSourceCode
  url: https://github.com/MartinPaulEve/epiLog/tree/master/epiLog
  isPartOf:
    name: GitHub
    type: WebSite
- title: Flickr
  type: WebSite
  url: http://flickr.com/
- title: OpenID2 eol message
  type: WebPage
  url: https://me.yahoo.com/
---

<p>As part of a transparent development process, I wanted to announce that I'm starting, thanks to some funding and support from a colleague at Sussex, a Digital Humanities project that focuses upon object annotation and cross-medium comparison. The project is called epiLog and will be available during development <a href="https://github.com/MartinPaulEve/epiLog/tree/master/epiLog">on my github</a>.</p>
<h3>The Concept</h3>
<p>I constantly make annotations on books, films, photographs and many other objects. My typical process is to break down the object into manageable chunks and then write about these subsets. The way I write various enormously. If it's public facing, my annotations will be narrative in style. If private, more like notes designed to jog my memory. What I thought would be really interesting, though, would be to provide people a platform for easily sharing, layering and comparing annotations. This comparison should happen, as I see it, not just on a single object (eg. we both used the same terms to describe a chapter of a book), but to cross-correlate between objects of different types. For instance, it is often said that Pynchon's <i>Gravity's Rainbow</i> is filmic in mode (cf. Brian McHale). Under epiLog, I hope it will be possible, when enough annotations are in the system, to find objects that, say, map onto one another, regardless of type (say, a David Lynch film and a Pynchon novel). In this way, we would be able to narrow the field to more likely matches for comparative studies, or at least for preliminary research purposes.</p>
<h3>Day 1</h3>
<p>I spent the first six hours of the project getting a Django environment up and running (I love python!) and integrating a <a href="http://twitter.github.com/bootstrap/">Twitter Bootstrap</a> environment and OpenID login, the latter taking the majority of the time. I have a homepage, a user profile (associated with an OpenID account) and avatar support ready to go.</p>
<p>I've never used Bootstrap before, but I have to say that it was a pleasurable experience. Although it tends towards homogenized styles, it really removes the hassle from styling. I can simply write well-formed HTML to a grid and have it displayed.</p>
<p>Component-wise: for those looking to integrate an OpenID login into Django, go no further than <a href="https://launchpad.net/django-openid-auth">django_openid_auth</a>. Bear in mind that most providers fail if you run your development server on 127.0.0.1, so be sure to rebind with something like: python ./manage.py runserver 192.168.0.2:8000 . If you want swanky login buttons, have a look at my modal dialog and Javascript snippet:</p>

{% highlight html %}
<!-- modal dialogs -->
<div class="modal fade" id="loginModal">
<div class="modal-header">
<a class="close" data-dismiss="modal">×</a>
<h3>Login to epiLog</h3>
</div>
<div class="modal-body">
<form action="" method="post">

<p>
epiLog uses OpenID for its authentication.
</p>
<p>
Username: <br/><input type="text" name="openid_username" id="openid_username" />
</p>
<p>Select your OpenID provider:</p>
<div class="btn-group" data-toggle="buttons-radio">
<a class="btn openurlbutton" data-toggle="button" id="aol"><img src="{{MEDIA_URL}}openid/aol.ico" alt="AOL" /></a>
<a class="btn openurlbutton" data-toggle="button" id="blogger"><img src="{{MEDIA_URL}}openid/blogger.ico" alt="Blogger" /></a>
<a class="btn openurlbutton" data-toggle="button" id="claimid"><img src="{{MEDIA_URL}}openid/claimid.ico" alt="Claim ID" /></a>
<a class="btn openurlbutton" data-toggle="button" id="flickr"><img src="{{MEDIA_URL}}openid/flickr.ico" alt="Flickr" /></a>
<a class="btn openurlbutton" data-toggle="button" id="google"><img src="{{MEDIA_URL}}openid/google.ico" alt="Google" /></a>
<a class="btn openurlbutton" data-toggle="button" id="livejournal"><img src="{{MEDIA_URL}}openid/lj.ico" alt="LiveJournal" /></a>
<a class="btn openurlbutton" data-toggle="button" id="myopenid"><img src="{{MEDIA_URL}}openid/myopenid.ico" alt="myOpenID" /></a>
<a class="btn openurlbutton" data-toggle="button" id="technorati"><img src="{{MEDIA_URL}}openid/technorati.ico" alt="Technorati" /></a>
<a class="btn openurlbutton" data-toggle="button" id="verisign"><img src="{{MEDIA_URL}}openid/verisign.ico" alt="Verisign" /></a>
<a class="btn openurlbutton" data-toggle="button" id="vidoop"><img src="{{MEDIA_URL}}openid/vidoop2.ico" alt="Vidoop" /></a>
<a class="btn openurlbutton" data-toggle="button" id="yahoo"><img src="{{MEDIA_URL}}openid/yahoo.ico" alt="Yahoo" /></a>
</div>


<a class="accordion-toggle" data-toggle="collapse" href="#collapseOne">
Advanced...
</a>

<div id="collapseOne" class="collapse">
<div class="accordion-inner">
<p>Enter an OpenID URL:</p>
{{ form.openid_identifier }}
</div>
</div>

</p>
</form>
</div>
<div class="modal-footer">
<a data-dismiss="modal" class="btn">Close</a> <a href="#" class="btn btn-primary" id="doLogin"><i class="icon-user icon-white"></i> Login</a>
</div>
</div>


<!-- Placed at the end of the document so the pages load faster -->
<script
src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>

<script type="text/javascript">

var provider = '';

$(document).ready(function() {

$(".openurlbutton").click(function(){
provider = $(this).attr('id');
setProvider(provider);
});

$("#openid_identifier").keyup(function(){
setProvider(provider);
});

$("#doLogin").click(function(){
$('form').submit();
});

});

  // a brief piece of script that will populate the openID identifier when the user clicks on a provider
  // it will also deal with the page aesthetics of clicking a provider
  function setProvider(provider)
  {
    providerBox = $('#id_openid_identifier');
    userName = $('#openid_username').val();

    var selected = 0;

    switch (provider)
    {
    case "aol":
providerBox.val("http://openid.aol.com/" + userName);
break;
    case "blogger":
providerBox.val("http://" + userName + ".blogspot.com");
break;
case "claimid":
providerBox.val("http://claimid.com/" + userName);
break;
case "flickr":
providerBox.val("http://flickr.com/" + userName);
break;
case "google":
providerBox.val("https://www.google.com/accounts/o8/id");
break;
case "livejournal":
providerBox.val("http://" + userName + ".livejournal.com");
break;
    case "myopenid":
providerBox.val("http://" + userName + ".myopenid.com");
break;
case "technorati":
providerBox.val("http://technorati.com/people/technorati/" + userName);
break;
case "verisign":
providerBox.val("http://" + userName + ".pip.verisignlabs.com");
break;
case "vidoop":
providerBox.val("http://" + userName + ".myvidoop.com");
break;
case "yahoo":
providerBox.val("https://me.yahoo.com/");
break;
    }

  }
  
</script>
{% endhighlight %}

<h3>Input</h3>
<p>I am extremely open to feedback, ideas/directions from interested parties. At present, I'm just going with the "build something cool" ethos, but if others have inside info on what I should change, API support, existing packages that I should know about, then I'd love to hear.</p>