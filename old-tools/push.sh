#!/bin/bash
#cd /home/martin/Documents/Programming/blog
#git add --all .
#git commit -m "$(date +'%-m.%-e.%Y')"

cd /home/martin/Documents/Programming/blog

#bundle exec jekyll build
aws s3 sync ./_site/ s3://eve.gd
#aws cloudfront create-invalidation --distribution-id E1ARNKVOIBYNHJ --paths "/*"
aws cloudfront create-invalidation --distribution-id E1ARNKVOIBYNHJ --paths "/"
aws cloudfront create-invalidation --distribution-id E1ARNKVOIBYNHJ --paths "/index.html"
aws cloudfront create-invalidation --distribution-id E1ARNKVOIBYNHJ --paths "/2022/*"

#git push origin master

