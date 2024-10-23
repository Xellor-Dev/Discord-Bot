import discord
from discord.ext import commands
import platform
import psutil
import aiosqlite
from datetime import datetime
from datetime import datetime, timezone

class SystemCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Bot info Cog has been loaded!")

    @discord.app_commands.command(name="info", description="Basic information about the bot.")
    async def info(self, interaction: discord.Interaction):
        bot = self.bot
        bot_name = bot.user.name
        bot_id = bot.user.id
        shard_count = bot.shard_count
        total_guilds = len(bot.guilds)
        total_users = sum(guild.member_count for guild in bot.guilds)
        python_version = platform.python_version()
        discord_version = discord.__version__
        host_name = platform.node()
        os_name = platform.system()
        os_version = platform.release()
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
    
        
        bot_creation_time = bot.user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        creation_time = bot.user.created_at
        now = datetime.now(timezone.utc)
        delta = now - creation_time

        years, remainder = divmod(delta.total_seconds(), 31536000)
        months, remainder = divmod(remainder, 2592000)
        weeks, remainder = divmod(remainder, 604800)
        days, _ = divmod(remainder, 86400)

        bot_creation_time_formatted = f"{int(years)} y, {int(months)} m, {int(weeks)} w, {int(days)} d"
        bot_owner = (await bot.application_info()).owner
        command_count = len(bot.tree.get_commands())
    
        
        async with aiosqlite.connect(bot.db_file) as db:
            cursor = await db.execute('SELECT COUNT(*) FROM profiles')
            total_profiles = (await cursor.fetchone())[0]
    
       
        embed = discord.Embed(
            title=f"Information about the bot {bot_name}",
            color=discord.Color.dark_embed()
        )
        embed.add_field(name="Bot Name", value=bot_name)
        embed.add_field(name="Bot ID", value=str(bot_id))
        # embed.add_field(name="Shards", value=str(shard_count))
        embed.add_field(name="Number of servers", value=str(total_guilds))
        embed.add_field(name="Number of users", value=str(total_users))
        embed.add_field(name="Number of user profiles", value=str(total_profiles))
    
        embed.add_field(name="Python version", value=python_version)
        embed.add_field(name="discord.py version", value=discord_version)
    
        embed.add_field(name="Host", value=host_name)
        embed.add_field(name="OS", value=f"{os_name} {os_version}")
        embed.add_field(name="CPU usage", value=f"{cpu_usage}%")
        embed.add_field(name="Memory usage", value=f"{memory_usage}%")
    
        embed.add_field(name="Bot creation time", value=bot_creation_time_formatted)
        embed.add_field(name="Bot owner", value=str(bot_owner))
        embed.add_field(name="Number of commands", value=str(command_count))
    
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="ping", description="Information about the delay of the bot.")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.defer()
        bot = self.bot
        
        latency = round(bot.latency * 1000)
        uptime = datetime.now(timezone.utc) - bot.uptime

        try:
            start_time = datetime.now(timezone.utc)
            async with aiosqlite.connect(bot.db_file) as db:
                await db.execute('SELECT 1')  
            db_latency = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        except Exception as e:
            db_latency = f"Помилка: {str(e)}"

        host_name = platform.node()
        os_name = platform.system()
        os_version = platform.release()
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent

        if latency <= 150:
            color = discord.Color.green()
        elif latency <= 200:
            color = discord.Color.orange()
        else:
            color = discord.Color.red()

        embed = discord.Embed(
            title="Pong!",
            color=color
        )
        embed.add_field(name="Delay Discord API", value=f"{latency}ms")
        days, remainder = divmod(uptime.total_seconds(), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
        embed.add_field(name="Uptime", value=uptime_str) 
        embed.add_field(name="Database latency", value=f"{db_latency:.2f}ms" if isinstance(db_latency, float) else db_latency)
        embed.add_field(name="Host", value=host_name)
        embed.add_field(name="OS", value=f"{os_name} {os_version}")
        embed.add_field(name="CPU usage", value=f"{cpu_usage}%")
        embed.add_field(name="Memory Usage", value=f"{memory_usage}%")

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(SystemCommands(bot))