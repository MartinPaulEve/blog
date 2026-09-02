---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2013/05/12/getting-free_cite-running-on-your-own-server
categories:
- Publishing Technology
- Programming
comments: []
date: 2013-05-12 10:48:39 +0200
date_gmt: 2013-05-12 09:48:39 +0200
doi: https://doi.org/10.59348/j9t2j-x0n12
roguescholar: https://rogue-scholar.org/records/c11kg-5rs62
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mgr4mbs2s
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Rails
title: Getting free_cite running on your own server
wordpress_id: 2680
wordpress_url: https://www.martineve.com/?p=2680
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mgr4mbs2s"
kcworks: https://works.hcommons.org/records/kpx76-68671
---

<p>I decided that the best way to spend this Sunday morning was to try to get <a href="https://github.com/shoe/free_cite">free_cite</a>, a citation parsing system, running on my server. Turns out this is easier said than done; the README provides no information on which versions of different software you need and also gives no advice on setting up the ruby environment.</p>
<p>In any case, here's the best way to do it. Turns out that you run into a massive headache if you try to use default Debian/Ubuntu package managers to configure Ruby (really? this shouldn't be hard to get right... but hey).</p>
<p>If you think you don't need the below detailed instructions, here's the info you do need:</p>
<p>Ruby version: 1.8.7-p371<br />
Rails version: 2.1</p>
<p>In any case, on Ubuntu 12.10, run:</p>

{% highlight bash %}
sudo apt-get install curl
curl -L get.rvm.io | bash -s stable --auto
rvm requirements
sudo apt-get install build-essential openssl libreadline6 libreadline6-dev \
curl git-core zlib1g zlib1g-dev libssl-dev libyaml-dev libsqlite3-dev sqlite3 \
libxml2-dev libxslt-dev autoconf libc6-dev ncurses-dev automake libtool bison  \
subversion pkg-config

rvm install 1.8.7-p371
rvm --default use 1.8.7-p371
gem install -v=2.1 rails

sudo apt-get install libpq-dev postgresql-client-9.1 postgresql-9.1
gem install pg

wget http://superb-west.dl.sourceforge.net/sourceforge/crfpp/CRF++-0.47.tar.gz
tar xvzf CRF++-0.47.tar.gz
cd CRF++-0.47
./configure && make && sudo make install
cd CRF++-0.47/ruby
ruby extconf.rb
make
sudo make install
{% endhighlight %}

<p>You then need to configure your postgresql database. As this is covered elsewhere, I'll leave it. Suffice to say that the instructions on the free_cite page for setting up the permissions are correct.</p>
<p>Next, do:</p>

{% highlight bash %}
git clone https://github.com/shoe/free_cite.git
cd free_cite/config
cp database.yml.example database.yml
{% endhighlight %}

<p>and then fill in the database details in database.yml.</p>
<p>Next:</p>

{% highlight bash %}
gem install crfpp
gem install rake --version 0.8.7
{% endhighlight %}

<p>You then need to edit lib/crfparser.rb to change the case of CRFPP to crfpp on the 4th "require" line.</p>
<p>Finally:</p>

{% highlight bash %}
rake _0.8.7_ crfparser:train_model
rake _0.8.7_ db:migrate
{% endhighlight %}