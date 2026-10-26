# Cs-project

## Run the Outlook email manager

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

#Progress:
Priority system: in development
graphics: in resarch
api work: in resarch

#10/11/26 scrum
Created all main files needed for our program (all in main branch)
Began working on the priority system for the emails
Api's are still in the resarch stage
graphics are in the resarch stage


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
