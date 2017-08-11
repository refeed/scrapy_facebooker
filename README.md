# scrapy_facebooker

[![Build Status](https://travis-ci.org/refeed/scrapy_facebooker.svg?branch=master)](https://travis-ci.org/refeed/scrapy_facebooker)

`scrapy_facebooker` is a collection of scrapy spiders which can scrape
posts, images, and so on from public Faceook Pages.

These spiders are intended to archive public Facebook pages, use it at your
own risk!

There are spiders which can operate normally without a Facebook account,
but there are also spiders which just can operate with a Facebook
Graph API access token.

## How to prepare

Before using these spiders you need to install all of its dependencies,
you can easily install it in one command:
```
pip install -r requirements.txt
```

This project is intended to run in Python 3.

## How to run

To run a spider, first you need to choose what spider you want to use,
you can look at spiders available at this project in
`/scrapy_facebooker/spiders/`.

For example, I want to use `facebook_post` spider and run it to scrape a public
page in Facebook with username `RHWEBsites`, and print the output to a file
named `output.json`:
```
$ scrapy crawl facebook_post -a target_username=RHWEBsites -o output.json
```

This is a name list of the spiders available in this repository:
- `facebook_event_graph`
- `facebook_post_graph`
- `facebook_photo_graph`
- `facebook_video_graph`
- `facebook_event`
- `facebook_post`
- `facebook_photo`

## License

Is available at `LICENSE.txt` in the root of this project.
