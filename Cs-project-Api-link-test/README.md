# Cs-project

## Instructions

Use Python 3.9 or newer. From the project folder, install the required packages
and start the application:

```powershell
py -m pip install -r requirements.txt
py extract-info.py
```

The first run prompts you to sign in to Microsoft. Your account needs access to
the mailbox, and the app registration must allow device-code sign-in and grant
the requested `User.Read` and `Mail.Read` permissions. A teammate also needs
access to this private repository to clone and run the project.

## Outlook setup

The Microsoft Entra client ID is included in the app so teammates can run it
without configuring an ID. This ID identifies the public desktop app; it is not
a client secret. Each person still signs in to their own Microsoft account on
first run. Do not commit client secrets, access tokens, token caches, or mailbox
data.

To use a different app registration, optionally set `OUTLOOK_CLIENT_ID` in the
environment before running. The sign-in token cache and downloaded messages
are saved locally and ignored by Git.

# Progress
Priority system: in development
Graphics: in research
API work: in research

# 11/12/26 scrum
	- Jose figured out how to get program working on any computer (assuming python is intalled on the computer prior)
	- Now brainstorming how to get the whole thing maybe packacged as a whole executable so that any casual user with no computer knowledge can use it
	
# 11/09/26 scrum
	- Work is being done on local machines/need to push as pull requests
	- Michael and Jose coordinating with different ends of work on the graphics interface
	- Figuring out API distribution
	- Continued research and brainstorming improvements
	
# 11/05/26 scrum
	- Tafara is beginning work API stabilization
	- Jose & Michael continuing work on graphics
	- Giancarlo is overseeing and essentially quality control after doing the heavy lifting with the backend
	- Checking up on our roles and responsibilities
	- Research continuing on using tkinter
		
# 11/02/26 scrum
	- Michael and Jose continuing working on graphics
	- Tafara helping out review code and making sure graphcis code and program are coordinated together
	- Making sure workload is actually distributed evenly
	- Giancarlo and Tafara are making sure that the API can actually be distributed through download
	- Brainstorming how to make the program user friendly
		adding buttons for auto pip installs????
	
# 10/26/26 scrum
	- Code for outlook connection merged into main, locations of some files were changed to comply with github rules
	- Michael and Jose working on graphics 
	- Currently waiting for Graphic interface to be complete to continue

# 10/25/26 scrum
	- Graphics will be started to be updated in its designated branch my Michael and Jose
	- Giancarlo is still on work for trying to make the api work across all devices
	-Tafara working on how to auto install the needed apps to run the api



# 10/22/26 scrum
	- Coordinated together on meeting our goals for the next few weeks
	- Michael and Jose honing in on graphics section over the weekend
	- Giancarlo brainstorming how to share project for use, as of now it only runs natively on his device
	- graphics testing works on each one of our systems though through visual studio
	- Ideas on how to share API file which is the one cauding the issue

# 10/12/26 scrum
	Backend logic is mostly functional and has nearly everything to work with minimal errors (still needs work though)
	Still need to incorporate graphics to make everything visibly pleasing and easier to maneuver
	Additionally, still need to add all-around device capability

# 10/5/26 scrum  
	figuring out API programs(possible programs: Azure, and looking for others)
	discussing ranking + point system: if has "@monmouth.edu" + points
	filtered by student Vs teacher 
	starting boiler plate layout
# 10/3/26 Scrum
	Discussed mainly about if the workload between group members was even. 
	Possible ideas for importance ranking system: 1. Work related emails
	2. Subscriptions email 
	3. Unknown/ informal emails. Parts assigned remained the same as written in previous meeting.

# 9/28/26 Scrum
	Discussing group roles and how we are actually going to make this work
	Jose is working on graphics/interface
	Filtering system: Michael and Giancarlo
	API/Retrieval/actually connecting script to Outlook: Tafara and Giovanni
	We are figuring out "due dates" for each member's tasks, figuring out what to do step by step
	Adding members to GitHub repository
	Create a sheet where we can report our work

# 9/25/26 scrum:
	Topics talked about: 
	We discussed that we need APIs to link the information in the emails to our python program. 
	Also discussed the need of breaking up the different parts of the project and having one person responsible for one part. 
	We are still in the process of trying to assign the leaders of each part of the program. 
	Most planning is still in process. 
	We also came to the conclusion that we are going to have to talk through our logic to ensure that everyone is on the same page
	before even attempting to began writing code, because this can be detrimental later on if none of us are coordinated. 
