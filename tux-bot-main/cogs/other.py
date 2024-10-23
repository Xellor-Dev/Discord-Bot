import discord
from discord.ext import commands

class Other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Other Cog has been loaded!")

    @discord.app_commands.command(name="server", description="Get a link to the bot server")
    async def server_link(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Server link",
            description="Here is the link to the bot server:",
            color=discord.Color.dark_embed()
        )
        embed.add_field(name="Link", value="Template Link", inline=False)
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="invite_link", description="Get the invite link for the bot")
    async def invite_link(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Invitation Link",
            description="Here is the invite link for the bot:",
            color=discord.Color.dark_embed()
        )
        embed.add_field(name="Link (Admin)", value="Template Link", inline=False)
        embed.add_field(name="Link (Rights required only, not preferred)", value="Template Link", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Other(bot))
