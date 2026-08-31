#!/bin/bash
source /home/martinev/rubyvenv/bloglive/2.1/bin/activate
bundle install
bundle exec jekyll build -d /home/martinev/public_html/

