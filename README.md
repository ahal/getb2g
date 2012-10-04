[Getb2g](https://github.com/ahal/getb2g) 
is a python package intended to make downloading the latest B2G nightly simple. It was designed 
with automated testing in mind, but can be used for anything that requires a B2G nightly build.

# Usage

Simply specify the username, password, a list of keywords and date (optional) to get the latest nightly build.

From command line:

    getb2g --user <username> --key <keyword1> --key <keyword2> --output-file <path_to_save_zip> --date <YYYY-MM-DD>

From script:

    import getb2g
    print getb2g.find_url(user, passwd, keys, date=None)                        # prints the url
    print getb2g.save_as(user, passwd, keys, savepath, date=None, silent=False) # prints full path to downloaded zip

For example to get otoro eu builds from the 19th of September, run:

    getb2g --user <username> --key otoro --key eu --date 2012-09-19 -o b2g.zip
