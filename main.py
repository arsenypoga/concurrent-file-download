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
    await asyncio.gather(*[download_url(url) for url in urls])


async def download_url(url: str):
    base_file_name = url.split("/")[-1]
    partial_file = Path("downloads/" + base_file_name + ".part")

    retry_count = 0
    while retry_count < 5:
        try:
            if partial_file.exists():
                print("Resuming download")
                file_size = partial_file.stat().st_size

                async with aiohttp.ClientSession() as client:
                    async with client.get(
                        url, headers={"Range": f"bytes={file_size}-"}
                    ) as resp:
                        if resp.status > 300:
                            # Should use own exceptions here; using standard Exception due to POC
                            raise Exception(f"Bad Status: {resp.status}")

                        total_bytes = resp.headers.get("Content-Length", 0)
                        print(f"Total file size: {total_bytes}")

                        with partial_file.open("ab") as f:
                            downloaded_bytes = file_size
                            async for chunk in resp.content.iter_chunked(1024 * 64):
                                f.write(chunk)
                                downloaded_bytes += len(chunk)
                                print(
                                    f"Downloaded {
                                        downloaded_bytes}/{total_bytes} bytes",
                                    end="\r",
                                )
            else:
                print("Downloading new file")
                async with aiohttp.ClientSession() as client:
                    async with client.get(url) as resp:
                        if resp.status != 200:
                            raise Exception(
                                f"Failed to download file due to status: {
                                    resp.status}"
                            )

                        total_bytes = resp.headers.get("Content-Length", 0)
                        print(f"Total file size: {total_bytes}")

                        with partial_file.open("wb") as f:
                            downloaded_bytes = 0

                            async for chunk in resp.content.iter_chunked(1024 * 64):
                                f.write(chunk)
                                downloaded_bytes += len(chunk)
                                print(
                                    f"Downloaded {
                                        downloaded_bytes}/{total_bytes} bytes",
                                    end="\r",
                                )

            partial_file = partial_file.rename(
                partial_file.parent / partial_file.stem)
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
