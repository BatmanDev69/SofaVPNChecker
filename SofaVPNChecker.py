import discord
from discord.ext import commands
import requests
import asyncio

# Set up intents
intents = discord.Intents.all()
intents.message_content = True

# Define the bot command prefix and intents
bot = commands.Bot(command_prefix='.', intents=intents)

# Tokens and URLs
DISCORD_BOT_TOKEN = 'YOUR_DISCORD_BOT_TOKEN_HERE'
IPINFO_TOKEN = 'YOUR_IPINFO_TOKEN_HERE'
PROXYCHECK_API_KEY = 'YOUR_PROXYCHECK_API_KEY_HERE'
IPINFO_URL = f'https://ipinfo.io/{{}}?token={IPINFO_TOKEN}'
PROXYCHECK_URL = f'http://proxycheck.io/v2/{{}}?key={PROXYCHECK_API_KEY}&vpn=1'

# Custom help command to avoid conflict with default help
@bot.command(name='helpme')
async def help(ctx):
    help_message = (
        "To lookup an IP address, type `.lookup` followed by the IP address.\n"
        "Example: `.lookup 8.8.8.8`"
    )
    await ctx.send(help_message)

# Lookup command
@bot.command()
async def lookup(ctx, ip: str = None):
    if ip is None:
        await ctx.send("Please provide an IP address in the format `.lookup <IP_ADDRESS>`")
        return

    try:
        # Get general IP information from ipinfo.io
        ipinfo_response = requests.get(IPINFO_URL.format(ip))
        ipinfo_data = ipinfo_response.json()

        if ipinfo_response.status_code != 200:
            await ctx.send(f"Error: Unable to retrieve information for IP {ip}")
            return

        # Check for VPN using proxycheck.io
        proxycheck_response = requests.get(PROXYCHECK_URL.format(ip))
        proxycheck_data = proxycheck_response.json()

        if proxycheck_response.status_code != 200 or ip not in proxycheck_data:
            await ctx.send(f"Error: Unable to retrieve VPN information for IP {ip}")
            return

        is_vpn = proxycheck_data[ip].get('proxy', 'no') == 'yes'

        # Create a rich embed message
        embed = discord.Embed(
            title=f"IP Information for {ip}",
            color=discord.Color.blue()
        )

        embed.add_field(name="IP Address", value=ipinfo_data.get('ip', 'N/A'), inline=False)
        embed.add_field(name="City", value=ipinfo_data.get('city', 'N/A'), inline=True)
        embed.add_field(name="Region", value=ipinfo_data.get('region', 'N/A'), inline=True)
        embed.add_field(name="Country", value=ipinfo_data.get('country', 'N/A'), inline=True)
        embed.add_field(name="Organization", value=ipinfo_data.get('org', 'N/A'), inline=True)
        embed.add_field(name="VPN", value="Yes" if is_vpn else "No", inline=True)

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Run the bot
bot.run(DISCORD_BOT_TOKEN)
