
import discord
from discord.ext import commands
import requests
import pyttsx3
import asyncio

TOKEN = "BOT_TOKENINI_YAZ"

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

@bot.event
async def on_ready():
    print("Bot aktif!")

@bot.command()
async def start(ctx):
    await ctx.send("Merhaba! Botuma hos geldin!")

@bot.command()
async def fact(ctx):
    try:
        r = await asyncio.to_thread(
            requests.get,
            "https://uselessfacts.jsph.pl/random.json?language=en",
            timeout=10
        )

        if r.status_code == 200:
            bilgi = r.json()["text"]
            await ctx.send("Ilginc bilgi: " + bilgi)
            await asyncio.to_thread(speak, bilgi)
        else:
            await ctx.send("Bilgi alinamadi!")

    except (requests.RequestException, KeyError, ValueError):
        await ctx.send("API hatasi!")

@bot.command()
async def hava(ctx):
    await ctx.send("Hangi sehirde yasiyorsun?")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        cevap = await bot.wait_for("message", check=check, timeout=60)

        geo = await asyncio.to_thread(
            requests.get,
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": cevap.content, "count": 1},
            timeout=10
        )
        geo.raise_for_status()

        yer = geo.json()["results"][0]

        r = await asyncio.to_thread(
            requests.get,
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": yer["latitude"],
                "longitude": yer["longitude"],
                "current": "temperature_2m,weather_code",
                "timezone": "auto"
            },
            timeout=10
        )
        r.raise_for_status()

        data = r.json()["current"]
        sicaklik = data["temperature_2m"]
        kod = data["weather_code"]

        durum = {
            0: "Gunesli",
            1: "Az bulutlu",
            2: "Parcali bulutlu",
            3: "Kapali",
            45: "Sisli",
            51: "Ciseleme",
            61: "Yagmurlu",
            63: "Yagmurlu",
            65: "Yogun yagmur",
            71: "Hafif kar",
            73: "Karli",
            75: "Yogun kar",
            80: "Yagmur saganagi",
            95: "Firtinali"
        }.get(kod, "Degisken hava")

        kiyafet = (
            "Kalin mont ve bot giy." if sicaklik < 5 else
            "Ceket ve uzun pantolon giy." if sicaklik < 15 else
            "Sweatshirt tercih edebilirsin." if sicaklik < 25 else
            "Ince kiyafetler giy."
        )

        if kod in [51, 61, 63, 65, 80]:
            kiyafet += " Semsiye al!"

        if kod in [71, 73, 75]:
            kiyafet += " Bere ve bot kullan."

        mesaj = (
            f"{yer['name']}: {durum}, {sicaklik} derece.\n"
            f"Kiyafet onerisi: {kiyafet}"
        )

        await ctx.send(mesaj)
        await asyncio.to_thread(speak, mesaj)

    except asyncio.TimeoutError:
        await ctx.send("Sure doldu!")

    except (requests.RequestException, KeyError, IndexError, ValueError):
        await ctx.send("Sehir bulunamadi veya sunucuya ulasilamadi!")

bot.run(TOKEN)
