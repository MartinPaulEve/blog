#!/bin/bash
. /usr/share/virtualenvwrapper/virtualenvwrapper.sh
. /usr/local/bin/virtualenvwrapper.sh
cd /home/martin/Documents/Programming/blog
cd music
workon musicBrainzPull
python /home/martin/Documents/Programming/musicBrainzPull/listMusic.py ./ids.txt ./template ./index.md
cd ..
cd books
python /home/martin/Documents/Programming/bookPull/listBooks.py ids.txt template index.md eprints.bbk.ac.uk
cd ..
workon SeleniumDeploy
python /home/martin/Documents/Programming/SeleniumDeploy/makedeposit.py
/usr/bin/python3 /home/martin/Documents/Programming/eprintsCV/eprintsCV_eprints3.py eprints.bbk.ac.uk Eve=3AMartin_Paul=3A=3A "book_ned,book_ed,article_ref_nev,book_section,article_rev,article_nef_nev,conference_item" > /home/martin/Documents/Programming/blog/_includes/publications.html
cd CaSSius-CV
./gencv.sh
cd ..
cp /home/martin/Documents/Programming/blog/CaSSius-CV/sections/* /home/martin/Documents/Programming/blog/_includes/
git add --all .
git commit -m "$(date +'%-m.%-e.%Y')"
cd /home/martin/Documents/Programming/blog
./getcal.sh
#git push origin master

cd /home/martin/Documents/Programming/blog

bundle exec jekyll build
aws s3 sync ./_site/ s3://eve.gd

#aws cloudfront create-invalidation --distribution-id E1ARNKVOIBYNHJ --paths "/*"
#aws cloudfront create-invalidation --distribution-id E1ARNKVOIBYNHJ --paths "/"
#aws cloudfront create-invalidation --distribution-id E1ARNKVOIBYNHJ --paths "/index.html"
#aws cloudfront create-invalidation --distribution-id E1ARNKVOIBYNHJ --paths "/2022/*"
/home/martin/Documents/Programming/blog/invalidate_cache.sh
