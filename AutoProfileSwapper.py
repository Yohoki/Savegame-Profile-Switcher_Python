import sys, os, sqlite3, shutil, time
from enum  import Enum
from pyuac import main_requires_admin

""" Some standard strings. Move to some dedicated Enum later """
_root_Path,_    = os.path.split(sys.argv[0])
_DB_FILE        = "config.db"
_old_ini_file   = "AutoProfileSwapper.ini"
_Save_Template  = "Profiles\\{}\\{}"

class __msg(Enum):
    """ Enum for all messages to display to the user. """
    migrate         = "Migrate old data? ['Y'es/'N'o]";                     symFound        = "{}: Simlink found."
    folderNotFound  = "{}: Folder not found. No copy performed";            copyPass        = "{}: Standard folder found. Files Copied."
    deleteAnyway    = "{}: Delete standard folder anyway? ['Y'es/'N'o]";    symPass         = "{}: Symlink not found. Linked save profile folder"
    symFail         = "{}: Error linking profile\n\t{}";                    symFinishWErrors= "Simlinks finished with errors:\n{}";
    symFinishPass   = "Simlinks created successfully";                      folderExists    = "{}: Error copying pre-existing saves. Folder may already exist.\n\t{})"
    msgExit         = "Press enter to exit...";                             unkn            = "Error: Unknown Error"
    missingArgs     = "Error: Missing arguments.";                          addArgs         = "Error: Missing arguments for adding new game."
    activeProfile   = "The currently active profile is: {}";                promptSwap      = "Swap Profile? ('Y'es/'N'o)"
    help            = """
    AutoProfileSwapper - Switches save profiles for games
    
    Usage:
      autoProfileSwapper.py [/a] [GameID] [SaveDir]
      autoProfileSwapper.py [/h] [ProfileID]
      autoProfileSwapper.py /help
      
      /help ----- Displays this help message.
      /a -------- Add a new game to the config file.
                      Requires GameID, SaveDir
      /h -------- Optional. Headless mode. Automatically switch profiles without user interaction.
      ProfileID - Name of profile to swap to. Will prompt user before swapping.
      GameID ---- Required with /a. Adds new one with \a.
      SaveDir --- Required with /a. Directory for game save folder."""

class __query(Enum):
    """ Enum for all strings related to accessing the SQLite3 DB """
    Games           = ["Games","GameID"];                                   Profiles        = ["Profiles","ProfileName"]
    get             = "SELECT * FROM {} WHERE {}=? COLLATE NOCASE";         getAll          = "SELECT * FROM {}"
    enable          = "UPDATE {} SET Active = 1 WHERE {}=? COLLATE NOCASE"; disable         = "UPDATE {} SET Active = NULL"
    active          = "SELECT * FROM {} WHERE Active=1";                    delete          = "DELETE FROM {} WHERE {}=? COLLATE NOCASE"
    addProf         = "INSERT INTO {} ({}) VALUES (?) ON CONFLICT DO NOTHING"
    addGame         = "INSERT INTO {0} ({1}, SaveDir, comment) VALUES (?, ?, ?) ON CONFLICT({1}) DO UPDATE SET SaveDir = excluded.SaveDir, comment = excluded.comment"
    init_A          = "CREATE TABLE IF NOT EXISTS {} ( {} TEXT PRIMARY KEY, SaveDir TEXT NOT NULL UNIQUE, comment TEXT )"
    init_B          = "CREATE TABLE IF NOT EXISTS {} ( {} TEXT PRIMARY KEY, Active INTEGER UNIQUE )"

""" Utility functions cuz lazy """
def util_path(path, test: bool = False): return os.path.exists(os.path.expandvars(path)) if test else os.path.expandvars(path)
def util_bugOut(s=__msg.unkn, *args): print(util_str(s,*args)); time.sleep(5); sys.exit()
def util_str(s=__msg.unkn, *args): return s.value.format(*args)

""" Helper functions to ease accessing SQLite3 DB """
def executeDBQuery(query, *args):
    with sqlite3.connect(_DB_FILE) as conn: return conn.execute(query, *args)
def init_db():
                                executeDBQuery( util_str(__query.init_A , *__query.Games   .value))
                                executeDBQuery( util_str(__query.init_B , *__query.Profiles.value))
def addGame(ID,Dir,Cmnt=None):  executeDBQuery( util_str(__query.addGame, *__query.Games.   value)      , (ID, Dir, Cmnt))
def addProfile(Profile):        executeDBQuery( util_str(__query.addProf, *__query.Profiles.value)      , [Profile])
def getGame(GameID):     return executeDBQuery( util_str(__query.get    , *__query.Games   .value)      , [GameID]) .fetchone() 
def getProfile(Profile): return executeDBQuery( util_str(__query.get    , *__query.Profiles.value)      , [Profile]).fetchone()
def deleteGame(GameID):         executeDBQuery( util_str(__query.delete , *__query.Games   .value)      , [GameID])
def deleteProfile(Profile):     executeDBQuery( util_str(__query.delete , *__query.Profiles.value)      , [Profile])
def getAllGames():       return executeDBQuery( util_str(__query.getAll ,  __query.Games   .value[0]))               .fetchall()
def getAllProfiles():    return executeDBQuery( util_str(__query.getAll ,  __query.Profiles.value[0]))               .fetchall()
def getActiveProfile():  return executeDBQuery( util_str(__query.active ,  __query.Profiles.value[0]))               .fetchone()
def enableProfile(Profile):     executeDBQuery( util_str(__query.enable , *__query.Profiles.value)       , [Profile])
def disableProfiles():          executeDBQuery( util_str(__query.disable,  __query.Profiles.value[0]))

def migrateData():
    """ Migrate old config.ini to new SQLite3 DB file. """
    if input(__msg.migrate.value).lower() != 'y': return
    if not util_path(_old_ini_file,True):                   return
    # Initialize configuration parser
    import configparser
    config = configparser.ConfigParser(allow_no_value=True, delimiters=('='))
    config.optionxform = str
    config.read(_old_ini_file)
    # Iterate through the sections and options
    for ID in config.sections():
        Dir,Fldr = config.items(ID)
        addGame(ID,os.path.join(Dir[1].strip('";'),Fldr[1].strip('";')))
        
def init_folders():
    """ Prep Profiles folder """
    if not util_path("Profiles",True): os.makedirs("Profiles")
    for profile in getAllProfiles():
        if not util_path(f"Profiles\\{profile[0]}",True):
            os.makedirs(f"Profiles\\{profile[0]}")

def initialize():
    """ First-run steps """
    init_db()
    migrateData()
    addProfile("Test1");# enableProfile("Test1"); # debug
    addProfile("Test2"); addProfile("Test3")     # debug
    if getActiveProfile() == None: addProfile("Test1"); enableProfile("Test1")
    init_folders()

def copy_save_to_profile(Path, ActiveProfile, ID, Errors):
    try:
        shutil.copytree(util_path(Path), util_path(_Save_Template.format(ActiveProfile,ID)))
        shutil.rmtree(util_path(Path))
        print(__msg.copyPass.value.format(ID))
    except Exception as e:
        print(__msg.folderExists.value.format(ID,e))
        if input(__msg.deleteAnyway.value.format(ID)).lower() == "y": shutil.rmtree(util_path(Path))
        Errors.append(ID)
    return Errors

def create_symlink(Path, ActiveProfile, ID, Errors):
    profilePath = util_path(os.path.join(_root_Path,_Save_Template.format(ActiveProfile,ID)))
    try:
        if not os.path.exists(profilePath): os.mkdir(profilePath)
        os.symlink(profilePath, util_path(Path), True)
        print(__msg.symPass.value.format(ID))
    except Exception as e: print(__msg.symFail.value.format(ID,e)); Errors.append(ID)
    return Errors

def make_all_symlinks():
    """ Still under works. Refactoring required. Move strings to dedicated Enum later. """
    ListGames       = getAllGames()
    ActiveProfile,_ = getActiveProfile()
    Errors          = []
    for ID,Path,_ in ListGames:
        PathExists, IsSym = os.path.exists(util_path(Path)), os.path.islink(util_path(Path))
        if     PathExists and     IsSym:        print(__msg.symFound.value.format(ID)); continue; # short circuit, everything's happy here.
        if not PathExists              :        print(__msg.folderNotFound.value.format(ID));
        if     PathExists and not IsSym:        Errors = copy_save_to_profile(Path, ActiveProfile, ID, Errors)
        if not os.path.exists(util_path(Path)): Errors = create_symlink(Path, ActiveProfile, ID, Errors)
    print(__msg.symFinishWErrors.value.format(Errors) if len(Errors) else __msg.symFinishPass.value)

def remove_symlinks():
    ListGames   = getAllGames()
    Errors      = []
    for ID,Path,_ in ListGames:
        try: os.unlink(Path)
        except Exception as e: print(f"failed to unlink\n{e}")
        continue;
    
def swapProfiles(Profile, Headless = False):
    if not Headless:
        choice = input(util_str(__msg.promptSwap)).strip().lower()
        if choice != 'y': util_bugOut(__msg.activeProfile, getActiveProfile()[0])
    disableProfiles()
    enableProfile(Profile)
    remove_symlinks()
    make_all_symlinks()
    if Headless: util_bugOut(__msg.activeProfile, getActiveProfile()[0])

def parseArgs():
    if len(sys.argv) < 2: util_bugOut(__msg.missingArgs)
    print(util_str(__msg.activeProfile, getActiveProfile()[0]))
    mode = sys.argv[1]
    match(mode):
        case "/help": util_bugOut(__msg.help)
        case "/a":
            if len(sys.argv) != 4: util_bugOut(__msg.addArgs)
            game_id = sys.argv[2]
            save_dir = sys.argv[3]
            add_new_game(game_id, save_dir)
        case "/h":
            if len(sys.argv) < 3: util_bugOut(__msg.missingArgs)
            profile = sys.argv[2]
            swapProfiles(profile, True)
        case _:
            if len(sys.argv) < 2: util_bugOut(__msg.missingArgs)
            profile = sys.argv[1]
            swapProfiles(profile)
            input(util_str(__msg.activeProfile, getActiveProfile()[0]))
            pass

def __main__():
    # Required libraries. Needs UAC for symlink.
    """
    pip install pyuac
    pip install pypiwin32
    pip install win32security
    """
    initialize() # First-run setup
    # make_all_symlinks()
    parseArgs()
    input(__msg.msgExit.value)

if __name__ == "__main__":
    # Idle IDE should autorun with *some* permissions. Will fail creating symlink.
    if not 'idlelib.run' in sys.modules:
        __main__ = main_requires_admin(__main__)
    __main__()
