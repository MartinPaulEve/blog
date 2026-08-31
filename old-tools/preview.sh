#!/bin/bash
/usr/bin/python /home/martin/Documents/Programming/eprintsCV/eprintsCV.py eprints.lincoln.ac.uk 3354 "book,article,book_section,conference_item" > /home/martin/Documents/Programming/blog/_includes/publications.html
bundle exec jekyll build

