import aiohttp
import asyncio
from pathlib import Path

urls = [
    "https://storage.googleapis.com/public_test_access_ae/output_20sec.mp4",
    "https://storage.googleapis.com/public_test_access_ae/output_30sec.mp4",
    "https://storage.googleapis.com/public_test_access_ae/output_40sec.mp4",
    "https://storage.googleapis.com/public_test_access_ae/output_50sec.mp4",
    "https://storage.googleapis.com/public_test_access_ae/output_60sec.mp4",
    # "http://localhost:3001/download",
]
timeout = aiohttp.ClientTimeout(total=20)


async def main():
    await asyncio.gather(*[download_url(url) for url in urls])


async def download_url(url: str):
    base_file_name = url.split("/")[-1]
    # Doing this for the file path join just in case this is ran on Windows, with
    # different path separators
    partial_file = Path("downloads") / (base_file_name + ".part")

    headers = {}
    file_read_mode = "wb"
    downloaded_bytes = 0

    if partial_file.exists():
        print("File exists; Resuming download")
        file_size = partial_file.stat().st_size
        headers["Range"] = f"bytes={file_size}"
        file_read_mode = "ab"
        downloaded_bytes = file_size
    else:
        print("New file; Starting new download")

    retry_count = 0
    while retry_count < 5:
        try:
            async with aiohttp.ClientSession(timeout=timeout) as client:
                async with client.get(url, headers=headers) as resp:
                    if resp.status > 300:
                        # Should use own exceptions here; using standard Exception due to POC
                        raise Exception(f"Bad Status: {resp.status}")

                    total_bytes = resp.headers.get("Content-Length", 0)
                    print(f"Total file size: {total_bytes}")

                    with partial_file.open(file_read_mode) as f:
                        async for chunk in resp.content.iter_chunked(1024 * 64):
                            f.write(chunk)
                            downloaded_bytes += len(chunk)
                            # This works nicely with single file, not so much with multiple
                            print(
                                f"Downloaded {
                                    downloaded_bytes}/{total_bytes} bytes",
                                end="\r",
                            )
            # pathhlib dorking - since the current filename has .part appended to the end of it
            # I remove said part with the .stem
            partial_file = partial_file.rename(partial_file.parent / partial_file.stem)
            print(f"Downloaded file {partial_file.absolute()}")
            return
        except Exception as e:
            sleep_time = 0.5 * 2 ** (retry_count)
            retry_count += 1
            print(f"Failed to download file due to {e}. Retry {
                retry_count}/{5}; Retrying in {sleep_time}")
            await asyncio.sleep(sleep_time)


if __name__ == "__main__":
    asyncio.run(main())
