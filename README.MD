# Running the software (USER GUIDE)
## 0. Install ffmpeg - required external package for software to work
### Windows
#### Using Chocolatey
`choco install ffmpeg`
### Else (https://www.gyan.dev/ffmpeg/builds/)
#### Download *ffmpeg-release-essentials.zip*, extract, and run .exe
### MacOS - Requires Homebrew
`brew install ffmpeg` 
### Linux
`sudo apt update`

`sudo apt install ffmpeg`

## 1. Click on the latest release and download the executable for your OS (ex: for Mac download app-macos)
## 2. Run the software
### Note: this software is unverified and will almost certainly be flagged by all antivirus checkers. 
### a. MacOS: The file is unverfied so MacOS tries to block it. Run these first two commands to enable read/write and bypass checking before running the software.
`chmod +x app-macos`

`xattr -cr app-macos`

`./app-macos`
### b. Linux
`chmod +x app-linux`

`./app-linux`
### c. Windows
#### Double click the exe. Windows Defender will try to block it. Click run anyway. 
#### Accept any other prompts (e.g. Allow this file to make changes, ...)

## 3. The terminal won't display any logs: check the app.log file generated in the same dir as the executable to see info and error statements. You should see "... INFO - Serving on http://0.0.0.0:5050" indicating the server has initiated.
## 3. Navigate to http://127.0.0.1:5050
## 4. Sign in/create account and then navigate to the upload route
## 5. When done using the software, turn off the software by KILLING the terminal (end task / ctrl - c, not just closing window)
## 6. Feel free to delete the uploads, json, clips, and zips folders once you have download the result zip file. 
### Note: Feature will be added soon to automatically clean up folders and residual files.

# Running the software (Developer Guide)
## 1. Download python if not already (https://www.python.org/downloads/)
### Add to PATH
### Install Python Extension in VSCode
## 2. Install ffmpeg
### Windows
#### Using Chocolatey
`choco install ffmpeg`
### Else (https://www.gyan.dev/ffmpeg/builds/)
#### Download *ffmpeg-release-essentials.zip*, extract, and run .exe
### MacOS - Requires Homebrew
`brew install ffmpeg` 
### Linux
`sudo apt update`

`sudo apt install ffmpeg`
## 3. Clone into master branch
`git clone "https://github.com/ocrxn/chopped-ai"`

`cd ./chopped-ai`
## 4. VENV
`python3 -m venv venv`
### Verify python is installed in venv
`which python`
### should say something like "chopped-ai/venv/bin/python"
### Activate VENV
### For Mac/Linux
`source venv/bin/activate`
### For Windows
`./venv/Scripts/Activate`
## 5. ENV FILE
### Create .env file
### Paste contents shared on Teams Chat into .env file 
## 6. Install required dependencies
### if inside venv
`pip install -r requirements.txt`
### if that doesn't work
`python3 -m pip install -r requirements.txt`
### if pip install breaks, install packages manually
`python3 -m pip install <package>`
## 7. Run main.py
`python3 main.py`
### If venv source interrupts, run again
## 8. Website on port 5050 
### [http://127.0.0.1:5050/](http://127.0.0.1:5050/)


# How To Push Changes to Github
## 1. Confirm your branch   
`git status`
## 2. Switch branch (if in wrong branch)
`git checkout <branch_name>`
## 2. Add files for staging (preparation to commit)
`git add <filename>`
### OR to add all files in working directory not mentioned in .gitignore:
`git add .`
## 3. Commit your changes (preparation to push)
`git commit -m "insert commit message"`
## 4. Push committed changes to Github
### For first time ever pushing:
`git push -u origin <branch_name>`
### Subsequent pushes:
`git push`


# Merging to Master
## 1. Go into master branch
`git checkout master`
## 2. Merge side branch to master
`git merge <branch_name>`
### This creates a merge conflict, popping up a window in VSCode to specify what you want code you want to keep (your code/their code). 
### Here is an example of what that looks like and what you should do to fix it.
```
    is_logged_out = require_login()
    if is_logged_out:
        <<<<<<< HEAD
        return -1
        =======
        return is_logged_out
        >>>>>>> feature-branch
```
### In the above example, HEAD refers to the branch you're working on (here it's MASTER). The line under it is what master currently has. The code under it is what the feature-branch (branch trying to be merged with master) has in that place. You must choose which version you keep, and delete the other one, along with the following. NOTE: the feature-branch with the new code may not be right, so don't just override master without looking.
### In the merge conflict case above, it should look like this after editing. Remove all the <<< and === and HEAD/feature-branch, and only keep code from one of the branches.
```
    is_logged_out = require_login()
    if is_logged_out:
        return is_logged_out
```
## 3. Stage the file
`git add <filename>`
## 4. Commit your changes and add commit message (example msg shown)
`git commit -m "Ex: Merged branch: <branch_name>"`
## 5. Push committed changes to Github
`git push`