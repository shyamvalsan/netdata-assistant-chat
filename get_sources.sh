# Cron this script to run daily

cd sources
git clone git@github.com:netdata/learn.git
git clone git@github.com:netdata/blog.git

cd ../data/
cp -rf ../sources/learn/docs/* ./docs/
cp -rf ../sources/blog/blog/* ./blog/

