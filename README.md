# Savegame Profile Switcher: Python Version
Complete rewrite of my old savegame swapper, now with 100% less Batch and 100% Python!
Original found at: https://github.com/Yohoki/Savegame-Profile-Switcher

# Savegame Profile Switcher
A small python script for use with Launchbox (or as a standalone program) to switch savegames for games that don't allow multiple profiles.

The script creates a profile folder in the directory where it is run. Inside, it generates a folder for each profile you create. Each profile then contains folders for every game you manage.

When you switch profiles, the script redirects the game to these managed folders instead of the original save locations by creating symlinks (shortcut-like links). This allows the game to save and load from your selected profile folder without detecting any difference.

You will need to tell it your profile names, game save locations and give each game an ID. For games that share a folder (like your steam saves folder, or series by the same devs) you can just add the root folder instead of each individual game.

Warning: This script does not include extensive filesystem integrity checks. Use it carefully and ensure you understand how symlinks work before making changes. I take no responsibility for data loss or corruption—use at your own risk!
TL;DR : Be smart. Don't @ me if you break shit.

# Usage
## Launchbox
> Launchbox Prep
- Right Click on your preffered game and click `Edit -> Edit Metadata/media...`
- Click `Additional Apps` tab and `Add Application...`
- Name it something like `Profile Swapper (Yohoki)`—this is how it will appear in the game's right-click menu.
  - You'll make one of these for each profile.
- Click `Browse` and add the Profile swapper's .py file as the application.
- Set the command line parameters for your profile (`Yohoki` or `/h "Player Two"`)
- Repeat for any profile you want to swap!
> Running in Launchbox
- Right Click your game and click the `Profile Swapper` option that you created.
- Follow onscreen prompts.

## As a Windows Shortcut
- Right click on a folder and select `New -> Shortcut`
- Add the Profile swapper's .py file as the target for the shortcut.
- Right click the new shortcut and click "Properties"
- Under `Target` add your command line parameters after the filename (`D:\Games\AutoProfileSwapper.py /h Yohoki`, for example)
- Open shortcut and follow onscreen instructions.

# Commandline Parameters
- `"ProfileID"`
  - Asks if you want to swap profiles, and changes the save location to `ProfileID`'s folder.
- `/h "ProfileID"`
  - Loads `ProfileID`'s folder automatically
  - Great for computers lacking mouse/keyboard.
- `/add-game "GameID" "C:\Path\to\Game SaveFolder"`
  - Adds `GameID` as a new, managed save.
  - Copies existing saves to your profile folders.
- `/add-prof "ProfileID" "C:\Path\to\Game SaveFolder"`
  - Adds `ProfileID` as a new, managed profile.
  - Auto-populates the profile folder with empty game folders.
  - Copies existing saves into it (useful for initial setup).
- `/help`
  - Displays the help text.

# Adding New Games/Profiles
AutoProfileSwapper stores profile and game information in an SQLite3 database (config.db). Do not delete or modify this file manually—doing so may break profile swapping, and I won’t help you fix it. However, your saves will remain intact, as the symlinks only change which profile is active.

Use the command `/add-game "GameID" "C:\Path\to\Game SaveFolder"` to manage new games. The quotes are only required if your ID or path contain spaces. Special locations like `%appdata%` and `%localappdata%` are allowed.

Likewise, `/add-prof "My Gamer Tag"` will create a profile. Add quotes if you have spaces in your ID.

# Removing Managed Games/Profiles
This is not a feature currently. Check back for v2 when I feel like it.

Editing the `config.db` file, you can remove the rows you want to remove. Then delete the symlink from the original save location manually. Your save data is still in the profile folders.
