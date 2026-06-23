#!/bin/bash
cd /home/martin/Documents/Programming/blog

bundle exec jekyll build --incremental

git add --all .
git commit -m "$(date +'%-m.%-e.%Y')"

git push

ssh evegd@reclaim -i ~/.ssh/id_ed25519_waldorf.pub /home/evegd/build_site.sh

cd -

#aws s3 sync ./_site/ s3://eve.gd
#rsync -a ./_site/ torionos:/var/www/html/
#aws cloudfront create-invalidation --distribution-id E1ARNKVOIBYNHJ --paths "/"
#aws cloudfront create-invalidation --distribution-id E1ARNKVOIBYNHJ --paths "/index.html"
#aws cloudfront create-invalidation --distribution-id E1ARNKVOIBYNHJ --paths "/2022/*"
#/home/martin/Documents/Programming/blog/invalidate_cache.sh
#git push origin master

