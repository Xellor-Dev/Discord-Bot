import discord
import aiohttp
from discord.ext import commands
import requests

class LinuxCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print('LinuxCog has been loaded!')

    @discord.app_commands.command(name="aur_search", description="Search for packages on the AUR.")
    async def aur_search(self, interaction: discord.Interaction, package: str):
        url = f'https://aur.archlinux.org/rpc/?v=5&type=search&arg={package}'
        response = requests.get(url)
        data = response.json()

        if data['resultcount'] > 0:
            results = data['results']
            view = self.AurPaginationView(results, package, per_page=5)
            embed = view.create_embed()
            await interaction.response.send_message(embed=embed, view=view)
        else:
            await interaction.response.send_message(f'Package `{package}` not found on AUR.', ephemeral=True)

    @discord.app_commands.command(name="cheat", description="Shows information about the terminal command.")
    async def cheat_command(self, interaction: discord.Interaction, command: str):
        await interaction.response.defer()

        command_details = await self.fetch_cheat_command_info(command)

        
        messages = self.split_text(f"{command_details}")

        if messages:
            view = self.CheatPaginationView(messages, command, per_page=1)
            embed = view.create_embed()
            await interaction.followup.send(embed=embed, view=view)
        else:
            await interaction.followup.send(f'Information about command `{command}` not found.', ephemeral=True)

    async def fetch_cheat_command_info(self, command_name: str) -> str:
        url = f"https://cheat.sh/{command_name}?T" 

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    text = await response.text()
                    return text
                return "The command is missing."

    def split_text(self, text: str, max_length: int = 1999) -> list[str]:
        lines = text.splitlines()
        chunks = []
        current_chunk = "```"

        for line in lines:
            if len(current_chunk) + len(line) + 1 > max_length:
                current_chunk += "```"
                chunks.append(current_chunk)
                current_chunk = "```" + line + "\n"
            else:
                current_chunk += line + "\n"

        if current_chunk:
            current_chunk += "```"
            chunks.append(current_chunk)

        return chunks

    class AurPaginationView(discord.ui.View):
        def __init__(self, results, package, per_page=5):
            super().__init__()
            self.results = results
            self.package = package
            self.per_page = per_page
            self.current_page = 0
            self.max_page = (len(results) - 1) // per_page
            self.add_item(LinuxCog.PreviousButton())
            self.add_item(LinuxCog.NextButton())

        def create_embed(self):
            start = self.current_page * self.per_page
            end = start + self.per_page
            embed = discord.Embed(
                title=f"Search results for `{self.package}`",
                description=f"Results {start + 1} to {min(end, len(self.results))} from {len(self.results)}:",
                color=discord.Color.dark_embed()
            )

            for result in self.results[start:end]:
                embed.add_field(
                    name=f"**{result['Name']}**",
                    value=f"Version: `{result['Version']}`\nDescription: `{result['Description']}`\n[Link]({result['URL']})",
                    inline=False
                )
            return embed

    class CheatPaginationView(discord.ui.View):
        def __init__(self, messages, command, per_page=1):
            super().__init__()
            self.messages = messages
            self.command = command
            self.per_page = per_page
            self.current_page = 0
            self.max_page = len(messages) - 1
            self.add_item(LinuxCog.PreviousButton())
            self.add_item(LinuxCog.NextButton())

        def create_embed(self):
            embed = discord.Embed(
                title=f"Information about the command: `{self.command}`",
                description=self.messages[self.current_page],
                color=discord.Color.dark_embed()
            )
            return embed

    class PreviousButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label='<', style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            view: LinuxCog.PaginationView = self.view
            if view.current_page > 0:
                view.current_page -= 1
                embed = view.create_embed()
                await interaction.response.edit_message(embed=embed, view=view)

    class NextButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label='>', style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            view: LinuxCog.PaginationView = self.view
            if view.current_page < view.max_page:
                view.current_page += 1
                embed = view.create_embed()
                await interaction.response.edit_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(LinuxCog(bot))