#!/bin/bash
echo "Broadcasting live gateway to search and AI indexers..."
curl -s "https://www.google.com/ping?sitemap=https://fluffy-spiders-find.loca.lt/llms.txt" > /dev/null &
curl -s "https://www.bing.com/ping?sitemap=https://fluffy-spiders-find.loca.lt/llms.txt" > /dev/null &
echo "Index ping dispatches completed."
