#!/bin/sh

set -e

cd "$(dirname "$0")"/..

FACEBOOK_USERNAME="RHWEBsites"

function run {
    # Grep the log error
    echo ---
    echo "Running $@"

    result=`$@`
    echo "$result"
    if echo "$result" | grep -q "log_count/ERROR"; then
        printf "\n\e[31;1mFAILED\e[0m = $@, please see the log above for details\n"
        exit 1
    fi
}

run "scrapy crawl facebook_photo -a target_username=$FACEBOOK_USERNAME"
run "scrapy crawl facebook_event -a target_username=$FACEBOOK_USERNAME"

printf '\n\e[32mEverything is fine!\e[0m\n'
