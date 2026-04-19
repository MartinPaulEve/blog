#!/bin/bash
aws cloudfront create-invalidation --distribution-id E1ARNKVOIBYNHJ --paths "/*"
aws cloudfront create-invalidation --distribution-id E32ULTEKXPGSCO --paths "/*"
aws cloudfront create-invalidation --distribution-id E30FCI7CTTE26B --paths "/*"

