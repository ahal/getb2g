[Getb2g](https://github.com/ahal/getb2g) 
is a python package intended to make downloading the latest B2G nightly simple. It was designed 
with automated testing in mind, but can be used for anything that requires a B2G nightly build.

# Usage

Simply specify the username, password and device to get the latest nightly build. Device is one of: 
emulator-arm, emulator-x86, nexus-s, otoro, sgs2.

From command line:

    getb2g --user <username> --device <device> --output-file <path_to_save_zip>

From script:

    import getb2g
    print getb2g.find_url(user, passwd, device)         # prints the url
    print getb2g.save_as(user, passwd, device, outfile) # prints full path to downloaded zip
