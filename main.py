import aiohttp
import asyncio
from pathlib import Path

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
    base_file_name = url.split("/")[-1]
    file = Path("downloads/" + base_file_name + ".part")

    if file.exists():
        print("Resuming download")
        file_size = file.stat().st_size
        async with client.get(url, headers={"Range": f"bytes: {file_size}-"}) as resp:
            with file.open("ab") as f:
                async for chunk in resp.content.iter_chunked(1024 * 64):
                    f.write(chunk)
    else:
        print("Downloading new file")
        async with client.get(url) as resp:
            with file.open("wb") as f:
                async for chunk in resp.content.iter_chunked(1024 * 64):
                    f.write(chunk)

    file = file.rename(file.parent / file.stem)
    print(f"Downloaded file {file.absolute()}")


if __name__ == "__main__":
    asyncio.run(main())
