import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite


class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Profile Cog has been loaded!")

    async def ensure_table_columns(self):
        required_columns = {
            "distro": "TEXT",
            "de_wm": "TEXT",
            "browser": "TEXT",
            "terminal": "TEXT",
            "editor": "TEXT",
            "programming_language": "TEXT",
            "shell": "TEXT",
            "description": "TEXT",
            "image_url": "TEXT"
        }

        async with aiosqlite.connect(self.bot.db_file) as db:
            cursor = await db.execute("PRAGMA table_info(profiles)")
            existing_columns = {row[1] for row in await cursor.fetchall()}

            for column, column_type in required_columns.items():
                if column not in existing_columns:
                    await db.execute(f"ALTER TABLE profiles ADD COLUMN {column} {column_type}")
            await db.commit()

    async def ensure_profile_fields(self, user_id: str):
        required_fields = {
            "distro": "Unknown",
            "de_wm": "Unknown",
            "browser": "Unknown",
            "terminal": "Unknown",
            "editor": "Unknown",
            "programming_language": "Unknown",
            "shell": "Unknown",
            "description": "No description",
            "image_url": ""
        }

        async with aiosqlite.connect(self.bot.db_file) as db:
            for field, default_value in required_fields.items():
                await db.execute(f'''
                    UPDATE profiles
                    SET {field} = COALESCE({field}, ?)
                    WHERE user_id = ?
                ''', (default_value, user_id))
            await db.commit()

    @discord.app_commands.command(name="profile", description="Show user profile.")
    async def view_profile(self, interaction: discord.Interaction, user: discord.Member = None):
        if user is None:
            user = interaction.user
        user_id = str(user.id)
        try:
            await self.ensure_table_columns()

            await self.ensure_profile_fields(user_id)

            profile_data = await self.bot.get_profile(user_id)
            if profile_data:
                embed = discord.Embed(title=f"Profile `{user.name}`", color=discord.Color.dark_embed())
                embed.set_thumbnail(url=user.avatar.url)
                embed.add_field(name="<:linux:1294492394582183976> **| Distribution**", value=profile_data["Distro"], inline=False)
                embed.add_field(name="<:forder:1294491276191727719> **| DE/WM**", value=profile_data["DE/WM"], inline=False)
                embed.add_field(name="<:browser:1294493524930334741> **| Browser**", value=profile_data["Browser"], inline=False)
                embed.add_field(name="<:terminal:1294494820362096710> **| Terminal**", value=profile_data["Terminal"], inline=False)
                embed.add_field(name="<:code:1294491278444073074> **| Code editor**", value=profile_data["Editor"], inline=False)
                embed.add_field(name="<:code:1294491278444073074> **| Programming language**", value=profile_data["Programming language"], inline=False)
                embed.add_field(name="<:settings:1294491262782672896> **| Shell**", value=profile_data["Shell"], inline=False)
                embed.add_field(name="<:mes:1294490746430296096> **| Description**", value=profile_data["Description"], inline=False)
                
                if profile_data["Badges"]:
                    badges_formatted = ", ".join(profile_data["Badges"])
                    embed.add_field(name="<:icon:1294491260060700733> **| Badges**", value=badges_formatted, inline=False)
                
                if profile_data["Image URL"]:
                    embed.set_image(url=profile_data["Image URL"])
                
                embed.add_field(
                    name="<:info:1294491272807190539> | **Account information**",
                    value=(
                        f"<:q_:1294491249599975464> | **User name:** {user}\n"
                        f"<:mention:1294491265068568596> | **ID:** {user.id}\n"
                        f"<:date:1294491269766316032> | **Generated:** {user.created_at.strftime('%d %b %y %H:%M:%S %Z')}\n"
                        f"<:date:1294491269766316032> | **Joined:** {user.joined_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    ),
                    inline=False
                )
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"Profile {user.name} not found. Use `/edit_profile` to add your own profile.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("An error occurred while processing your request.", ephemeral=True)
            print(f"Error in view_profile: {e}")

    @discord.app_commands.command(name="edit_profile", description="Customize your user profile.")
    @discord.app_commands.describe(
        favorite_distro="Distribution",
        favorite_de="DE/WM",
        favorite_browser="Browser",
        favorite_terminal="Terminal",
        favorite_editor="Code Editor",
        favorite_language="Programming Language",
        favorite_shell="Shell",
        description="Profile description",
        image_url="Profile Image URL"
    )
    async def edit_profile(
        self,
        interaction: discord.Interaction,
        favorite_distro: str = None,
        favorite_de: str = None,
        favorite_browser: str = None,
        favorite_terminal: str = None,
        favorite_editor: str = None,
        favorite_language: str = None,
        favorite_shell: str = None,
        description: str = None,
        image_url: str = None
    ):
        await interaction.response.defer(thinking=True)
        user_id = str(interaction.user.id)
        bot = self.bot
        try:

            await self.ensure_table_columns()
            await self.ensure_profile_fields(user_id)

            current_profile = await bot.get_profile(user_id) or {}

            profile_data = {
                "Distro": favorite_distro or current_profile.get("Distro"),
                "DE/WM": favorite_de or current_profile.get("DE/WM"),
                "Browser": favorite_browser or current_profile.get("Browser"),
                "Terminal": favorite_terminal or current_profile.get("Terminal"),
                "Editor": favorite_editor or current_profile.get("Editor"),
                "Programming language": favorite_language or current_profile.get("Programming language"),
                "Shell": favorite_shell or current_profile.get("Shell"),
                "Description": description or current_profile.get("Description"),
                "Image URL": image_url or current_profile.get("Image URL")
            }

            await bot.update_profile(user_id, profile_data)
            await interaction.followup.send(f"User profile `{interaction.user.name}` has been updated!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send("An error occurred while processing your request.", ephemeral=True)
            print(f"Error in edit_profile: {e}")

async def setup(bot):
    await bot.add_cog(ProfileCog(bot))