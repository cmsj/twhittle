This is a daemon that deletes your oldest tweets, but there are two huge limitations:
 * You can't get API keys for this stuff from Twitter anymore, so unless you already have one, move on.
 * The Twitter API only lets you get your most recent 3200 tweets, so use some other method to nuke yourself down to <= 3200 tweets, then this daemon can keep you below 3200 (the exact number to keep is configurable in the config file)

You probably don't want any of this, but I do, so yay.

This is how I run it:
 * Take `sample_config.json` and put the relevant values in, put it somewhere as `config.json`
 * Configure Docker to run twhittle (it's on Docker hub [here](https://hub.docker.com/r/cmsj/twhittle/)) and add a volume where your `config.json` lives as `/config`
 * Tell Docker to set the environment variable `TWHITTLE_CONFIG` to `/config/config.json`
