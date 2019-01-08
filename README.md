# dAbot

CLI tool to automate stuff on DeviantArt.com using [DiFi](https://github.com/danopia/deviantart-difi/wiki) and HTML scraping

## Installation

1. [Install **Python 2**](https://www.python.org/downloads/),
   and make sure it is added to `PATH`.  
   (On Windows you need to check the "Add in PATH" option in the installation.)
2. Open Terminal/Command Prompt and enter: `pip install dAbot`  
    If that doesn't work, try `python -m pip install dAbot`  
    If that doesn't work either, make sure Python is installed correctly and added to `PATH`.
3. Once dAbot is installed, you can use any of the commands listed below by entering them in Terminal/Command Prompt.

To upgrade it later, run `pip install dAbot --upgrade`

## Usage

```batch
dAbot <username> <password> [-v] llama      give          random        (deviants|groups|exchangers)
dAbot <username> <password> [-v] llama      give          msgs          (activity|replies)           [--trash_msgs]
dAbot <username> <password> [-v] llama      give          file          (dev_names|dev_ids)          <file_path>
dAbot <username> <password> [-v] llama      give          group_members <group>                      [--reversed]
dAbot <username> <password> [-v] llama      give          url           <url>
dAbot <username> <password> [-v] llama      give          traders
dAbot <username> <password> [-v] llama      give          traders_random
dAbot <username> <password> [-v] llama      give          <deviant>
dAbot <username> <password> [-v] points     give          <deviant>     <amount>                     [<message>]
dAbot <username> <password> [-v] points     balance
dAbot <username> <password> [-v] devwatch   (add|remove)  <deviant>
dAbot <username> <password> [-v] msgs       trash         (activity|bulletins|notices|replies|comments)
dAbot <username> <password> [-v] comment    <deviant>     <comment>
dAbot <username> <password> [-v] logout
dAbot <username> <password> [-v] exec       <code>
dAbot <username> <password> [-v] llama      stats         <deviant>
dAbot <username> <password> [-v] llama      hof           group         <group_name> [--reversed]
dAbot <username> <password> [-v] llama      hof           file          <file_path>
dAbot <username> <password> [-v] llama      hof           <deviant_names>...
dAbot <username> <password> [-v] badges     hof           <deviant_names>...
dAbot <username> <password> [-v] save       random        (deviants|groups|exchangers)               <quantity>
dAbot <username> <password> [-v] save       group_members <group>
dAbot <username> <password> [-v] save       dev_ids       <dev_names_file_path>                      [--if_llama_given]
```

### How to bypass bot detection

At some point you might get an error message due to DeviantArt detecting automated tools (i.e. bot usage).  
This is a recent security measure that Wix -- the parent company of DeviantArt -- has introduced in the website, in order to prevent bots from logging in.

In order to continue using dAbot, you need to provide a special kind of token that can be acquired by solving a captcha.  The method was discovered by [DRSDavidSoft](https://github.com/DRSDavidSoft), and you need to install a userscript to acquire the response token.  

The instructions are provided at this page:  https://deviantart.com/perimeterx

Once you solve the captcha, you'll be able to login to your account using dAbot.

## Disclaimer

I don't intend to maintain this tool (except for some occasional changes). I developed this as a personal project back in 2014 and three years later, it wasn't doing much good sitting around, so I put it out here.  
DeviantArt is going to release breaking changes with [eclipse](https://deviantarteclipse.com), which means this bot will most certainly stop working when it is released.  
The code can be refactored a lot and sped up to 100x using asynchronous connections. If you're a developer interested in hacking the code, you should definitely look into that.

## Alternatives

You might want to have a look at the [dADroid](https://www.deviantart.com/dADroid-bot) project once this bot stops to function.  