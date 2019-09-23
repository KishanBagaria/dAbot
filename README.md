# dAbot

CLI tool to automate stuff on DeviantArt.com

## Installation

1. [Install Python 3](https://www.python.org/downloads/) (Python 2 will work too but it's not recommended)
2. Open Terminal/Command Prompt and enter `pip install dAbot`  
    If that doesn't work, try `python -m pip install dAbot`  
    If that doesn't work either, you're likely using Windows and you should reinstall Python making sure that the "Add in PATH" option is checked.
3. Once dAbot is installed, you can use any of the commands listed below by entering them in Terminal/Command Prompt.

To upgrade it later, run `pip install dAbot --upgrade`

## Usage

```
dAbot <cookies_txt_path> [-v] llama      give          random        (deviants|groups|exchangers)
dAbot <cookies_txt_path> [-v] llama      give          msgs          (activity|replies)           [--trash_msgs]
dAbot <cookies_txt_path> [-v] llama      give          file          (dev_names|dev_ids)          <file_path>
dAbot <cookies_txt_path> [-v] llama      give          group_members <group>                      [--reversed]
dAbot <cookies_txt_path> [-v] llama      give          url           <url>
dAbot <cookies_txt_path> [-v] llama      give          traders
dAbot <cookies_txt_path> [-v] llama      give          traders_random
dAbot <cookies_txt_path> [-v] llama      give          <deviant>
dAbot <cookies_txt_path> [-v] points     give          <deviant>     <amount>                     [<message>]
dAbot <cookies_txt_path> [-v] points     balance
dAbot <cookies_txt_path> [-v] devwatch   (add|remove)  <deviant>
dAbot <cookies_txt_path> [-v] msgs       trash         (activity|bulletins|notices|replies|comments)
dAbot <cookies_txt_path> [-v] comment    <deviant>     <comment>
dAbot <cookies_txt_path> [-v] logout
dAbot <cookies_txt_path> [-v] exec       <code>
dAbot <cookies_txt_path> [-v] llama      stats         <deviant>
dAbot <cookies_txt_path> [-v] llama      hof           group         <group_name> [--reversed]
dAbot <cookies_txt_path> [-v] llama      hof           file          <file_path>
dAbot <cookies_txt_path> [-v] llama      hof           <deviant_names>...
dAbot <cookies_txt_path> [-v] badges     hof           <deviant_names>...
dAbot <cookies_txt_path> [-v] save       random        (deviants|groups|exchangers)               <quantity>
dAbot <cookies_txt_path> [-v] save       group_members <group>
dAbot <cookies_txt_path> [-v] save       dev_ids       <dev_names_file_path>                      [--if_llama_given]
```

1. Install a browser extension that can export a `cookies.txt` file. Here's one for [Chrome](https://chrome.google.com/webstore/detail/njabckikapfpffapmjgojcnbfjonfjfg).
2. Go to DeviantArt.com and export the `cookies.txt` file for that tab only (or for DeviantArt.com only).
3. For `<cookies_txt_path>`, supply the path where the `cookies.txt` was exported/saved.  
     This should look something like `C:\Users\you\Downloads\cookies.txt` or `/Users/you/Downloads/cookies.txt`

## Example

This will give me a llama:
```
dAbot /Users/you/Downloads/cookies.txt llama give Kishan-Bagaria
```

## Disclaimer

I don't intend to maintain this tool (except for some occasional changes). I developed this as a personal project back in 2014 and three years later, it wasn't doing much good sitting around, so I put it out here.  
It can be refactored a lot and sped up 100x using asynchronous connections. If you're a developer interested in hacking the code, you should definitely look into that.
