# dAbot

CLI tool to automate stuff on DeviantArt.com

### Usage

```
dAbot.py <username> <password> [-v] llama      give          random        (deviants|groups|exchangers)
dAbot.py <username> <password> [-v] llama      give          msgs          (activity|replies)           [--trash_msgs]
dAbot.py <username> <password> [-v] llama      give          file          (dev_names|dev_ids)          <file_path>
dAbot.py <username> <password> [-v] llama      give          group_members <group>                      [--reversed]
dAbot.py <username> <password> [-v] llama      give          url           <url>
dAbot.py <username> <password> [-v] llama      give          traders
dAbot.py <username> <password> [-v] llama      give          traders_random
dAbot.py <username> <password> [-v] llama      give          <deviant>
dAbot.py <username> <password> [-v] points     give          <deviant>     <amount>                     [<message>]
dAbot.py <username> <password> [-v] points     balance
dAbot.py <username> <password> [-v] devwatch   (add|remove)  <deviant>
dAbot.py <username> <password> [-v] msgs       trash         (activity|bulletins|notices|replies|comments)
dAbot.py <username> <password> [-v] comment    <deviant>     <comment>
dAbot.py <username> <password> [-v] logout
dAbot.py <username> <password> [-v] exec       <code>
dAbot.py <username> <password> [-v] llama      stats         <deviant>
dAbot.py <username> <password> [-v] llama      hof           group         <group_name> [--reversed]
dAbot.py <username> <password> [-v] llama      hof           file          <file_path>
dAbot.py <username> <password> [-v] llama      hof           <deviant_names>...
dAbot.py <username> <password> [-v] badges     hof           <deviant_names>...
dAbot.py <username> <password> [-v] save       random        (deviants|groups|exchangers)               <quantity>
dAbot.py <username> <password> [-v] save       group_members <group>
dAbot.py <username> <password> [-v] save       dev_ids       <dev_names_file_path>                      [--if_llama_given]
```
