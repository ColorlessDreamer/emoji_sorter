import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Define the command callback as a free async function.
async def show_emojis(interaction: discord.Interaction):
    guild = interaction.guild
    if guild:
        # Create list of emoji strings
        emoji_strings = [f"<:{emoji.name}:{emoji.id}>" for emoji in guild.emojis]
        
        # Send initial response
        await interaction.response.send_message("Current emojis:")
        
        # Split emojis into chunks of 50 to stay well under the 2000 char limit
        chunk_size = 50
        for i in range(0, len(emoji_strings), chunk_size):
            chunk = ' '.join(emoji_strings[i:i + chunk_size])
            if chunk:  # Only send if chunk has content
                # Use followup since we can only use response once
                await interaction.followup.send(chunk)
    else:
        await interaction.response.send_message("No guild found for this interaction.")


# Manually wrap the function in an ApplicationCommand instance.
command_show_emojis = discord.app_commands.Command(
    callback=show_emojis,
    name="show_emojis",
    description="Display all server emojis"
)

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guild_messages = True
        intents.guilds = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        guild_id = int(os.getenv("GUILD_ID"))
        guild_obj = discord.Object(id=guild_id)

        # Debug: Print current cached commands before clearing.
        print("Before clearing:")
        print("Global Commands:", self.tree._global_commands)
        print("Guild Commands:", self.tree._guild_commands)

        # Clear global commands and guild commands (these methods are synchronous).
        self.tree.clear_commands(guild=None)
        self.tree.clear_commands(guild=guild_obj)

        # Add the wrapped command for the specific guild.
        self.tree.add_command(command_show_emojis, guild=guild_obj)
        await self.tree.sync(guild=guild_obj)

        # Debug: Print command caches after syncing.
        print("\nAfter clearing and syncing:")
        print("Global Commands:", self.tree._global_commands)
        print("Guild Commands:", self.tree._guild_commands)

        print("\nBot is starting...")
        print(f"Connected to guild ID: {guild_id}")

    async def on_ready(self):
        guild_id = int(os.getenv("GUILD_ID"))
        guild = self.get_guild(guild_id)
        if guild:
            print(f"Connected to guild: {guild.name} (ID: {guild.id})")
            print(f"Owner ID: {guild.owner_id}")
            print(f"Emoji count: {len(guild.emojis)}")
            print(f"Member count: {guild.member_count}")
        else:
            print("Guild not found.")

# Create and run the bot using the token from your .env.
bot = Bot()

# Add at the bottom
def run_bot():
    bot.run(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    run_bot()

