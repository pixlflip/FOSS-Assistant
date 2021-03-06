"""
__main__.py Version 0.5.
Author: PixlFlip
Date: May 9, 2022

One good turn deserves another
"""
import datetime
import time, os, socket, json
import wikipedia
import discord
import mutagen
import requests
from mutagen.wave import WAVE
from API_Server.Functions import Protocols, User, Email
from API_Server.Tasks import Task

# All key (read top level) variables here
SETTINGS = Protocols.Settings()
TOKEN = SETTINGS.discordBotToken
PREFIX = '?'
currentDirectory = SETTINGS.currentDirectory
API_KEY = '#2AJKLFHW9203NJFC'
# todo top level var that should later on be customizable so people can reach a web host. For testing this works though
BASE = 'http://127.0.0.1:5000/'
# End Key Variables ======================


class MyClient(discord.Client):
    # Startup Bot
    async def on_ready(self):
        print('Logged on as', self.user)

    # Runs When Message is Sent that is Visible to Bot
    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        # return if no prefix to command. Saves tons of processing power
        if not message.content.startswith(PREFIX):
            return  # we know its a command now

        # ==============================================================================================================================================
        # ========================================================== Commands Anyone Can Use ===========================================================
        # ping command
        if message.content == (PREFIX + 'ping'):
            await message.channel.send('pong', delete_after=10)

        # help command
        if message.content == (PREFIX + 'help'):
            # open discord help file
            file = open(currentDirectory + 'help.txt')
            returnList = ""
            for line in file:
                returnList += line
            await message.channel.send(returnList)

        # ===================== Wikipedia =====================
        # takes message, looks for a match on wikipedia, and returns article summary
        if message.content.startswith(PREFIX + 'wiki'):
            # substring extract user query, pass to wikipedia, and return summary
            try:
                summary = wikipedia.summary(message.content[6:], 7)
                await message.channel.send('Wikipedia Top Result: ' + summary)
            except:
                await message.channel.send('No Data Found From Wikipedia')
        # ================================================================ Music Playing ===============================================================
        if message.content.startswith(PREFIX + 'play'):
            channel = message.channel
            # check in a voice channel
            voice_state = message.author.voice
            if voice_state is None:
                # Exiting if the user is not in a voice channel
                return await message.channel.send('You need to be in a voice channel to use this command')
            # in theory song will be placed in the message
            channel = message.author.voice.channel
            # get audio length
            audio = WAVE("startup.wav")
            audio_info = audio.info
            length = int(audio_info.length)
            # connect to vc
            vc = await channel.connect()
            await message.channel.send('Playing Music')
            vc.play(discord.FFmpegPCMAudio('startup.wav'), after=lambda e: (print('done', e)))
            time.sleep(length + 5)
            await vc.disconnect()

        if message.content.startswith(PREFIX + 'laugh'):
            channel = message.channel
            # check in a voice channel
            voice_state = message.author.voice
            if voice_state is None:
                # Exiting if the user is not in a voice channel
                return await message.channel.send('You need to be in a voice channel to use this command')
            # in theory song will be placed in the message
            channel = message.author.voice.channel
            # get audio length
            audio = WAVE(currentDirectory + '/Sound_Effects/laughing.mp3')
            audio_info = audio.info
            length = int(audio_info.length)
            # connect to vc
            vc = await channel.connect()
            vc.play(discord.FFmpegPCMAudio(currentDirectory + '/Sound_Effects/laughing.mp3'))
            time.sleep(length + 1)
            await vc.disconnect()
        # ==============================================================================================================================================
        # ==============================================================================================================================================
        # get profile from api (if it exists)
        profile_request = requests.get(BASE + "profile", json={"session_token": "'" + API_KEY + "'", "discord": "'" + str(message.author) + "'"})
        profile_request = profile_request.json()
        # check if user profile exists and return if no profile
        if profile_request['status'] == 'Failed.':
            return
        # we know the profile exists now

        # todo depreciated code clean it up move it out
        # load the profile of the user into key variable
        PROFILE = profile_request['user']
        # log the command and who did it for diagnosis
        Protocols.debug_log("nothing here", profile_request['user'], (message.content.split(" ")[0]), "Discord")


        # ============================       Email      ==============================
        if message.content.startswith(PREFIX + 'email'):
            # set channel to same as one command issued in
            channel = message.channel
            # ask for and interpret sub command
            await message.channel.send('What would you like to do with email?')
            subCommand1 = await client.wait_for('message')
            subCommand2 = subCommand1.content + " email "
            # 12 meaning they want to view inbox.
            if subCommand2.__contains__("view") and subCommand2.__contains__("email"):
                # verify permissions and get email + password
                if User.isProfileDiscord(str(message.author)):
                    # ask user for password for security
                    await message.channel.send('Please Enter Your Password: ', delete_after=120)
                    userSubmittedPassword = await client.wait_for('message')
                    if userSubmittedPassword.content == PROFILE.password:
                        # with that out of the way we can get the inbox
                        # get inbox
                        inbox = str(Email.userViewGetInbox(PROFILE.defaultEmail, PROFILE.defaultEmailPassword))
                        # Return the entry and related information and delete after 120 seconds for security
                        await channel.send(" " + inbox, delete_after=120)
                    else:
                        await channel.send("Invalid Password for account. Access Denied.", delete_after=120)
                else:
                    # Failed to find profile
                    await channel.send('Profile for Discord Tag ' + (str(message.author)) + ' not found. You must be authorized to use this command.', delete_after=120)

            # 1 entered meaning they want to send an email.
            elif subCommand2.__contains__("send") and subCommand2.__contains__("email"):
                # verify permissions and get email + password
                if User.isProfileDiscord(str(message.author)):
                    # get profile
                    PROFILE = User.Profile(User.getProfileUsernameDiscord(str(message.author)))
                    # ask user for password for security
                    await message.channel.send('Please Enter Your Password: ', delete_after=120)
                    userSubmittedPassword = await client.wait_for('message')
                    if userSubmittedPassword.content == PROFILE.password:

                        # ask user for what information we want
                        await channel.send("Please Enter the Email You Are Sending To: ", delete_after=120)
                        recieverEmail = await client.wait_for('message')
                        await channel.send("Please Enter the Email Subject: ", delete_after=120)
                        emailSubject = await client.wait_for('message')
                        await channel.send("Please Enter the Email Body: ", delete_after=120)
                        body = await client.wait_for('message')

                        # finally send the email
                        Email.sendEmail(PROFILE.defaultEmail, PROFILE.defaultEmailPassword, PROFILE.defaultEmail, recieverEmail.content, emailSubject.content, body.content)
                        # tell the user we managed to somehow do our job
                        await channel.send("Email sent. Consider deleting your message to preserve your privacy and keep it off Discord's servers.", delete_after=120)
                    else:
                        await channel.send("Invalid Password for account. Access Denied.", delete_after=120)
                else:
                    # Failed to find profile
                    await channel.send('Profile for Discord Tag ' + (str(message.author)) + ' not found. You must be authorized to use this command.', delete_after=120)
            else:
                # no valid option chosen
                await channel.send('Invalid Option. Please Specify Sub Command:\n 1 | View Inbox\n 2 | Send Email', delete_after=120)

        # ============================      Journal     ==============================
        if message.content.startswith(PREFIX + 'journal'):
            # Check function so we don't reply to strangers
            def check(m):
                return m.author == message.author and m.channel == channel
            # set channel to same as one command issued in
            channel = message.channel
            # ask for and interpret sub command
            await message.channel.send('What would you like to do with your journal?')
            subCommand1 = await client.wait_for('message', check=check)
            subCommand2 = subCommand1.content + " journal "
            # import journal object for use
            userJournal = PROFILE.journal
            # view entry
            if subCommand2.__contains__("view") and subCommand2.__contains__("entry"):
                # parse next part for a date
                await channel.send('Input Date Of Entry You Want to View Using the Format YYYY-MM-DD (include the - )')
                getDate = await client.wait_for('message', check=check)
                date = getDate.content

                # todo cut all this logic out in favor of API call
                # check if the entry exists
                if userJournal.is_entry(date):
                    # Get the entry
                    entry = userJournal.get_entry(date)
                    # Return the entry and related information and delete after 120 seconds for security
                    await channel.send('Entry for the Date ' + date + ': \n' + entry.entry, delete_after=120)
                else:
                    # return error to user
                    await channel.send('Invalid Date. Try again using the format YYYY-MM-DD (include the - )')
            # 2 entered meaning new entry
            if subCommand2.__contains__("new") and subCommand2.__contains__("entry"):
                await channel.send('Enter Your Entry')
                # format all remaining information in the message and store in variable
                getEntry = await client.wait_for('message', check=check)
                entry = getEntry.content
                x = datetime.now().__str__().replace(" ", "")
                # add the entry using api
                api_call = requests.put(BASE + "journal", json={'session_token': "'" + API_KEY + "'", 'date': "'" + x + "'", 'entry': "'" + entry.replace("\n", "") + "'", 'creation_device': 'DiscordClient', 'starred': 'false', 'time_zone': 'EST'})
                api_call = api_call.json()
                if api_call['status'] == 'Completed.':
                    # tell the user the entry was recorded
                    await channel.send('Entry Recorded.')
                else:
                    await channel.send('Internal server error. Error Message: ' + api_call['error_msg'])
            # send message to channel if no other data given
            else:
                await channel.send('Invalid Option. Please Message Something Like\n"create a new entry"\nor\n"view journal entry"')

        # ============================       Notes      ==============================
        # TODO integrate new note functionality here

        # ============================        News       ==============================
        if message.content.startswith(PREFIX + 'news'):
            # set channel to same as one command issued in
            channel = message.channel
            # get news summary
            client.send(b'{"api_key": "kwy", "command_id": "000020", "date": "2022-05-16"}')
            from_server = client.recv(4096)
            client.close()
            query = json.loads(from_server.decode())
            # return summary to client
            await message.channel.send(query['entry'])

        # ============================       DB Backup       ==============================
        if message.content.startswith(PREFIX + 'backup'):
            # set channel to same as one command issued in
            channel = message.channel
            # backup database
            Task.full_backup(date, SETTINGS.sqlUsername, SETTINGS.sqlPassword, SETTINGS.sqlDatabase)
            # return summary to client
            await message.channel.send('Full System Backup Complete')

        # ===================== Greet =====================
        if message.content.startswith('/greet'):
            channel = message.channel
            await channel.send('Say hello!')

            def check(m):
                return m.content == 'hello' and m.channel == channel

            msg = await client.wait_for('message', check=check)
            await channel.send('Hello {.author}!'.format(msg))


        # ============================      User Project     ==============================
        if message.content.startswith(PREFIX + 'project'):
            # set channel to same as one command issued in
            channel = message.channel
            # Check function so we don't reply to strangers
            def check(m):
                return m.author == message.author and m.channel == channel

            # TODO first get all available projects from user and ask for a numeric selection, or if they have no projects ask to create one


            await message.channel.send('What would you like to do with your project?')
            subCommand1 = await client.wait_for('message', check=check)
            subCommand2 = subCommand1.content + " journal "
            # send to parser with a little extra journal just to ensure it marks it as a journal command
            intentCommand = Protocols.findIntentFromText(subCommand2)
            # import journal object for use
            userJournal = PROFILE.journal
            # 3 entered meaning they want to view entry
            if intentCommand == 3:
                # parse next part for a date
                await channel.send('Input Date Of Entry You Want to View Using the Format YYYY-MM-DD (include the - )')
                getDate = await client.wait_for('message', check=check)
                date = getDate.content
                # check if the entry exists
                if userJournal.is_entry(date):
                    # Get the entry
                    entry = userJournal.get_entry(date)
                    # Return the entry and related information and delete after 120 seconds for security
                    await channel.send('Entry for the Date ' + date + ': \n' + entry.entry, delete_after=120)
                else:
                    # return error to user
                    await channel.send('Invalid Date. Try again using the format YYYY-MM-DD (include the - )')
            # 2 entered meaning new entry
            if intentCommand == 31:
                await channel.send('Enter Your Entry')
                # format all remaining information in the message and store in variable
                getEntry = await client.wait_for('message', check=check)
                entry = getEntry.content
                # add the entry
                userJournal.add_entry(entry.replace("\n", ""), "DiscordClient")
                # tell the user the entry was recorded
                await channel.send('Entry Recorded.')
            # send message to channel if no other data given
            else:
                await channel.send('Invalid Option. Please Message Something Like\n"create a new entry"\nor\n"view journal entry"')

        # ============================       Create User      ==============================
        if message.content.startswith(PREFIX + 'newuser'):
            # todo change this up so it uses the api server and also allows someone to grant a discord account the ability to just make their own account.
            channel = message.channel
            # Check function so we don't reply to strangers
            def check(m):
                return m.author == message.author and m.channel == channel
            # return if low clearance
            if not int(PROFILE.clearanceLevel) == 1:
                await message.channel.send('Insufficient Clearance Level: ' + PROFILE.clearanceLevel + "\nMust be Clearance Level 1 to create new users.")
                return
            # ask for user details
            await message.channel.send('New User Creation. Enter Username:')
            newusername = await client.wait_for('message', check=check)
            await channel.send('Enter User Password. Can Be Changed Later By User:')
            newuserpass = await client.wait_for('message', check=check)
            await channel.send('Enter User Email. Enter NONE For No Email:')
            newuseremail = await client.wait_for('message', check=check)
            await channel.send('Enter User Email Password. Enter NONE If Blank:')
            newuserepass = await client.wait_for('message', check=check)
            await channel.send('Enter User Discord:')
            newuserdiscord = await client.wait_for('message', check=check)
            await channel.send('Enter User Clearance Level. \nWARNING: HIGHER LEVEL = HIGHER PERMISSIONS. Clearance Level 1 is highest and Clearance Level 3 is lowest.')
            newuserclearance = await client.wait_for('message', check=check)
            # verify clearance the rest we don't care about
            try:
                clearanceLevel = int(newuserclearance)
            except:
                print("failed user account creation")
                await channel.send('USER CLEARANCE MUST BE A NUMBER FROM 1 TO 3. PROCESS TERMINATED.')
                return
            User.create(newusername, newuserpass, newuserclearance, newuseremail, newuserepass, newuserdiscord)
            await channel.send('New User ' + newusername + ' Created With Level ' + newuserclearance + ' Clearance.')

        # ===================== Dynamic Command =====================
        # reads intent from message provided to it using intent manager or neural network.

# ffmpeg
# PyNaCa
# mutagen
client = MyClient()

client.run(TOKEN)
