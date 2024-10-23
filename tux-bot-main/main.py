import os
import discord
from discord.ext import commands
import aiosqlite

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True 
        super().__init__(command_prefix="!", intents=intents)
        self.db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profiles.db')
        self.channel_id = "Your channel ID here"

    async def setup_hook(self):
        await self.initialize_database()
        await self.load_extension('cogs.bot_info')
        await self.load_extension('cogs.linux')
        await self.load_extension('cogs.profiles')
        await self.load_extension('cogs.other')
        await self.tree.sync()

    async def initialize_database(self):
        db_exists = os.path.exists(self.db_file)
        
        async with aiosqlite.connect(self.db_file) as db:
            if not db_exists:
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS profiles (
                        user_id TEXT PRIMARY KEY,
                        distro TEXT,
                        de_wm TEXT,
                        browser TEXT,
                        terminal TEXT,
                        editor TEXT,
                        programming_language TEXT,
                        shell TEXT,
                        description TEXT,
                        image_url TEXT
                    )
                ''')
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS badges (
                        user_id TEXT,
                        badge_name TEXT,
                        PRIMARY KEY (user_id, badge_name),
                        FOREIGN KEY (user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
                    )
                ''')
                await db.commit()

    async def get_profile(self, user_id: str):
        async with aiosqlite.connect(self.db_file) as db:
            cursor = await db.execute('SELECT * FROM profiles WHERE user_id = ?', (user_id,))
            row = await cursor.fetchone()
            if row:
                cursor = await db.execute('SELECT badge_name FROM badges WHERE user_id = ?', (user_id,))
                badges = await cursor.fetchall()
                badge_list = [badge[0] for badge in badges]
                profile = {
                    "Distro": row[1],
                    "DE/WM": row[2],
                    "Browser": row[3],
                    "Terminal": row[4],
                    "Editor": row[5],
                    "Programming language": row[6],
                    "Shell": row[7],
                    "Description": row[8],
                    "Badges": badge_list,
                    "Image URL": row[9]
                }
                return profile
            return None

    async def update_profile(self, user_id: str, profile_data: dict):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute('''
                INSERT INTO profiles (user_id, distro, de_wm, browser, terminal, editor, programming_language, shell, description, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    distro=excluded.distro,
                    de_wm=excluded.de_wm,
                    browser=excluded.browser,
                    terminal=excluded.terminal,
                    editor=excluded.editor,
                    programming_language=excluded.programming_language,
                    shell=excluded.shell,
                    description=excluded.description,
                    image_url=excluded.image_url
            ''', (
                user_id,
                profile_data['Distro'],
                profile_data['DE/WM'],
                profile_data['Browser'],
                profile_data['Terminal'],
                profile_data['Editor'],
                profile_data['Programming language'],
                profile_data['Shell'],
                profile_data['Description'],
                profile_data['Image URL']
            ))
            await db.commit()

    async def add_badge(self, user_id: str, badge_name: str):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute('''
                INSERT OR IGNORE INTO badges (user_id, badge_name)
                VALUES (?, ?)
            ''', (user_id, badge_name))
            await db.commit()

    async def remove_badge(self, user_id: str, badge_name: str):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute('''
                DELETE FROM badges WHERE user_id = ? AND badge_name = ?
            ''', (user_id, badge_name))
            await db.commit()

    async def get_badges(self, user_id: str):
        async with aiosqlite.connect(self.db_file) as db:
            cursor = await db.execute('SELECT badge_name FROM badges WHERE user_id = ?', (user_id,))
            badges = await cursor.fetchall()
            return [badge[0] for badge in badges]

    async def on_ready(self):
        self.uptime = discord.utils.utcnow()
        status_channel_id = 1286054953940680850  
        status_channel = self.get_channel(status_channel_id)
        if status_channel:
            await status_channel.send(f'Bot {self.user.name} is now online and ready!')
        else:
            print(f'Channel with ID {status_channel_id} not found.')

        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Linux is better than Windows — that's a fact, not up for debate."))

bot = Bot()

bot.run("Your bot token here")
