# scrapy_facebooker

`scrapy_facebooker` is a collection of scrapy spiders which can scrape
posts, images, and so on from public Faceook Pages.

This spider is intended to archive public Facebook pages, use it at your
own risk!

This spider doesn't need a Facebook account to run.

## How to prepare

Before using this spider you need to install some of its dependencies,
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

## License

Is available at `LICENSE.txt` in the root of this project.
