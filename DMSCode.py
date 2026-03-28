import discord
from discord.ext import tasks
import datetime
import os

# Config
TOKEN = 'BOTTOKENHERE'
USERID = 123123  # Your Discord ID
CHANNELID = 123123 # Where the alert sends

TIMEOUTDAYS = 7

# Custom message here
ALERTMESSAGE = """
This is the message you shall edit for the dead mans switch.
Maybe if you have passed or something, I dunno.
"""

# - - - - - -

TIMESTAMPFILE = "last_seen.txt"

class ContinuousDeadMansBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_seen = self.load_timestamp()
        self.alert_sent = False 

    def load_timestamp(self):
        """Read the last seen time from a file, or return 'now' if file doesn't exist."""
        if os.path.exists(TIMESTAMPFILE):
            try:
                with open(TIMESTAMPFILE, "r") as f:
                    return datetime.datetime.fromisoformat(f.read().strip())
            except Exception as e:
                print(f"Error loading timestamp: {e}")
        return datetime.datetime.now()

    def save_timestamp(self, dt):
        """Save the current time to a file."""
        with open(TIMESTAMPFILE, "w") as f:
            f.write(dt.isoformat())

    async def on_ready(self):
        print(f'Logged in as {self.user}. Monitoring for user ID: {USERID}')
        if not self.check_deadline.is_running():
            self.check_deadline.start()

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.author.id == USERID:
            self.last_seen = datetime.datetime.now()
            self.save_timestamp(self.last_seen)
            if self.alert_sent:
                self.alert_sent = False
                print("User returned. DMS has been reset.")
            
            print(f"Activity logged at {self.last_seen}. Timer reset.")

    @tasks.loop(hours=1)
    async def check_deadline(self):
        if self.alert_sent:
            return

        now = datetime.datetime.now()
        diff = now - self.last_seen
        
        if diff.days >= TIMEOUTDAYS:
            channel = self.get_channel(CHANNELID)
            if channel:
                await channel.send(ALERTMESSAGE)
                self.alert_sent = True
                print("Switch triggered. Alert message sent. System remains active but silent.")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True 

bot = ContinuousDeadMansBot(intents=intents)
bot.run(TOKEN)