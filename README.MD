# Developer Notes
# How to Run Chopped-AI
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
`git init <filename>`
### OR to add all files in working directory not mentioned in .gitignore:
`git init .`
## 3. Commit your changes (preparation to push)
`git commit -m "insert commit message"`
## 4. Push committed changes to Github
### For first time ever pushing:
`git push -u origin <branch_name>`
### Subsequent pushes:
`git push`
## 5. Merge with master ⚠️(Causes merge conflicts)⚠️
`git rebase origin/master`


# Create Public IP Address using Ngrok
`ngrok http 5050`