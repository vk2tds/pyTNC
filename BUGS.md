BUGS


* Timezone is stored when the specific information is saved. If you cange to or from UTC, dates and times will be in whatever 
format they were in until refreshed
* If TAB completion is NOT working, GNU Readline may not be working. It may not be needed, depending on the system
* cannot work out an escape command in readline in CONV mode. Hacked by doing Alt-C which sends ç
* Redline - https://pypi.org/project/gnureadline/



Future 
* Libedit readline
    if 'libedit' in readline.__doc__:
        print("Found libedit readline")
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        print("Found gnu readline")
        readline.parse_and_bind("tab: complete")

