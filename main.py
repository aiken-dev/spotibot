from interactions import Client, Intents, slash_command, SlashContext, OptionType, slash_option, listen, Embed
bot = Client(intents=Intents.DEFAULT)

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

from PIL import Image
from colorthief import ColorThief
import io
import requests
import os
scope = "user-library-read"
from dotenv import load_dotenv

load_dotenv()

# auth_manager = SpotifyOAuth(client_id="cd029bdca565477088ea8142111326ff", client_secret="7c3441a09ba142dfb026ba432359a878", redirect_uri="http://localhost:3000", scope="user-read-playback-state user-read-currently-playing")
# sp = spotipy.Spotify(auth_manager=auth_manager)

auth_manager = SpotifyClientCredentials(client_id="cd029bdca565477088ea8142111326ff", client_secret="7c3441a09ba142dfb026ba432359a878")
sp = spotipy.Spotify(auth_manager=auth_manager)
@listen()
async def on_ready():
    print("ready")

def get_artist_id(artist):
    result = sp.search(q=f'artist:{artist}', type="artist", limit=1)

    if result['artists']['items']:
        return result['artists']['items'][0]['id']
        
@slash_command(
    name="test",
    description="just a test"
)
async def test(ctx: SlashContext):
    await ctx.send("test!!!")

@slash_command()
async def ping(ctx: SlashContext):
    await ctx.send("ping!")

@slash_command(name="albums", description="lists the albums for an artist")
@slash_option(name="artist", description="provide artist name", required=True, opt_type=OptionType.STRING)
async def albums(ctx: SlashContext, artist: str):
    artistId = get_artist_id(artist)
    results = sp.artist_albums(artistId)

    albums = results['items']

    artist = sp.artist(artistId)
    artistName = artist['name']

        # get dominant colour from artist image
    response = requests.get(artist['images'][0]['url']) # downloads artists image
    color_thief = ColorThief(io.BytesIO(response.content)) # passes image data into color thief. image data is converted into bytes by io.BytesIO
    dominant_color = color_thief.get_color(quality=1) # gets the dominant colour
    embed_color = (dominant_color[0] << 16) + (dominant_color[1] << 8) + dominant_color[2] # dominant colour has r g and b values. this essentially finds the most frequent colour in the image

    embed = Embed(
        title=f"Top albums for {artistName}",
        color=embed_color
    )


    for idx, album in enumerate(albums):
        album_name = album['name']
        number = idx + 1
    
        embed.add_field(name=f'{number}. {album_name}',
                        value="test",
                        inline=False)
        
    await ctx.send(embeds=[embed])

    
















@slash_command(name="toptracks", description="lists top 10 tracks for an artist")
@slash_option(name="artist", description="provide artist name", required=True, opt_type=OptionType.STRING)
@slash_option(name="quantity", description="how many tracks?", required=False, opt_type=OptionType.INTEGER)
async def toptracks(ctx: SlashContext, artist: str, quantity: int = 10):


 
    artistid = get_artist_id(artist)
    results = sp.artist_top_tracks(artistid)
    
  
    topTracks = results['tracks'][:quantity] # quantity of how many songs

    artist = sp.artist(artistid)
    artist_name = artist['name']

    # get dominant colour from artist image
    response = requests.get(artist['images'][0]['url']) # downloads artists image
    color_thief = ColorThief(io.BytesIO(response.content)) # passes image data into color thief. image data is converted into bytes by io.BytesIO
    dominant_color = color_thief.get_color(quality=1) # gets the dominant colour
    embed_color = (dominant_color[0] << 16) + (dominant_color[1] << 8) + dominant_color[2] # dominant colour has r g and b values. this essentially finds the most frequent colour in the image

    embed = Embed(
        title=f"Top tracks for {artist_name}",
        color=embed_color
    )


    for idx, track in enumerate(topTracks):
        track_name = track['name']
        number = idx + 1
        album_name = track['album']['name']

        embed.add_field(
            name=f"{number}. {track_name}",
            value=f"_{album_name}_",
            inline=False
        )

        embed.set_thumbnail(url=artist['images'][0]['url'])
        embed.set_image(url=topTracks[0]['album']['images'][0]['url'])
        number_one_track = topTracks[0]['name'] #0 means the first track in the list topTracks and ['name'] is the name of the first track
        embed.set_footer(f"#1 Track: {number_one_track}")
        

    await ctx.send(embeds=[embed])


@slash_command(name="np", description="my currently playing track")
async def np(ctx: SlashContext):
    np = sp.current_playback()
    np_artist = np['item']['artists'][0]['name']
    np_track = np['item']['name']
    np_album = np['item']['album']['name']

    # get dominant colour from artist image
    response = requests.get(np['item']['album']['images'][0]['url']) # downloads artists image
    color_thief = ColorThief(io.BytesIO(response.content)) # passes image data into color thief. image data is converted into bytes by io.BytesIO
    dominant_color = color_thief.get_color(quality=1) # gets the dominant colour
    embed_color = (dominant_color[0] << 16) + (dominant_color[1] << 8) + dominant_color[2] # dominant colour has r g and b values. this essentially finds the most frequent colour in the image

    np_embed = Embed(
        title="Now playing for aiken",
        description=f"{np_track} by {np_artist} on {np_album}",
        color = embed_color
    )

    np_embed.set_thumbnail(url=np['item']['album']['images'][0]['url'])
    

    await ctx.send("Sorry! This command is under construction bruv")
    await ctx.send(embeds=[np_embed])


@slash_command(name="recartist", description="recommends you artists based on an artist")
@slash_option(name="artist", description="provide artist name", required=True, opt_type=OptionType.STRING)
@slash_option(name="quantity", description="provide quantity, max 10", required=False, opt_type=OptionType.INTEGER)
async def recartist(ctx: SlashContext, artist: str, quantity: int=10):
    artist_id = get_artist_id(artist)
    results = sp.artist_related_artists(artist_id)
    
    relatedArtists = results['artists'][:quantity]

    artist_name = sp.artist(artist_id)['name']
    embed = Embed(title=f'Artists similar to {artist_name}')

    for idx, artist in enumerate(relatedArtists):
        number = idx + 1
        related_artist_name = artist['name']
        embed.add_field(name=f'{number}. {related_artist_name}', value = ".", inline=False)
    
    await ctx.send(embeds=[embed])

bot.start(os.environ["DISCORD_TOKEN"])
