# Concurrent file download

## Setup

I used `poetry` for the dependency management. To install it:
```bash
pip install poetry
```

followed by:
```bash
poetry install
```
to install the dependencies.

To run the application:
1. `poetry run python main.py`
2. activate shell via: `poetry shell`, then run `python main.py`

## General notes

- While the assignment description highly recommends using Django, this problem does not require it, or use the capabilities of it, so it is not used in this problem, however adding support for it should be trivial.
- I've used only one dependecy - `aiohttp` for asyncronous request and streaming support.
- I've used age old technique for resumable files that is used by many modern browsers - appending `.part` to the file that is still being downloaded.
- It is assumed that once all of the files are downloaded, executing the program again will redownload these files.
- I've used exponential backoff for the retry mechanism - it retries total of 5 times, with exponentially growing delay.
- Basic debug logging is done via standard `print` statements. It's not perfect, especially when dealing with parallel downloads (as the outputs overlay themselves), but is lightweight. For the best performance, async code also requires async logging, otherwise syncronous logging blocks the execution.
- by default `aiohttp` client has a timeout of 5 minutes - even if the physical connection is lost, no error will be thrown until then. 5 minutes is an extremely long duration, so I have shortened that to 20 seconds, which seems reasonable in the context of this application.
- I've used `mockoon` to test the retry logic - with it it is trivial to fail requests 1-4 but succeed the request 5.
- `justfile` is a file similar to `makefile`, but with cleaner syntax.
