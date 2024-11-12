import aiohttp

urls = [
    "https://storage.googleapis.com/public_test_access_ae/output_20sec.mp4",
    "https://storage.googleapis.com/public_test_access_ae/output_30sec.mp4",
    "https://storage.googleapis.com/public_test_access_ae/output_40sec.mp4",
    "https://storage.googleapis.com/public_test_access_ae/output_50sec.mp4",
    "https://storage.googleapis.com/public_test_access_ae/output_60sec.mp4",
]


async def main():
    async with aiohttp.ClientSession() as client:
        await download_file(client, urls[0])


async def download_file(client: aiohttp.ClientSession, url: str):
    resp = await client.stream(url)


if __name__ == "__main__":
    await main()
