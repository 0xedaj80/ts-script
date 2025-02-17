"""Download TS (Transport Stream) video file from a website.

To use it:

- Find the URL of one of the TS files (for example, using the developer tools
  from Firefox or Chromium/Chrome).
- Identify the counter in the URL, and replace it with `{counter}` (this can be
  formatted if the counter must have a specific format, for example:
  `{counter:05d}`).
- Run the script: `python3 ts_downloader.py -o FILE.ts "URL_WITH_COUNTER"`

Bruno Oberle - 2002
"""

import argparse
import os
import signal
import sys
import tempfile
from urllib.error import URLError
from urllib.request import urlopen

# Global variable to store downloaded content
downloaded_content = b""
ts_path = None

def handle_interrupt(signum, frame):
    """Handle program interruption (e.g., Ctrl+C)."""
    global downloaded_content
    if downloaded_content and ts_path:
        print("\nInterrupted! Saving downloaded content...")
        with open(ts_path, 'wb') as fh:
            fh.write(downloaded_content)
        print(f"Saved partially downloaded TS file to {ts_path}")
    sys.exit(1)

def download(template_url):
    """Download the TS chunks and concatenate them in the returned string.

    `template_url` is a string containing the `{counter}` placeholder, which
    may contain formatting options (e.g., `{counter:05d}`).

    The URLs are formed by incrementing the counter. When an error is
    encountered (e.g., a 404), the loop stops.

    The returned value is a binary string.
    """
    global downloaded_content
    global ts_path
    downloaded_content = b""
    counter =0
    while True:
        url = template_url.format(counter=counter)
        print(f"Reading {url}")
        try:
            u = urlopen(url)
            downloaded_content += u.read()
            counter += 1
        except URLError:
            print("Error encountered, quitting downloading")
            break
    return downloaded_content

def save_ts_file(content, ts_path):
    """Save the concatenated TS content to a file.

    `content` is a binary string containing the concatenated TS chunks.
    `ts_path` is the path to save the TS file.
    """
    print(f"Saving concatenated TS file to {ts_path}")
    with open(ts_path, 'wb') as fh:
        fh.write(content)

def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "url_template",
        help="URL template, must include {counter}"
    )
    parser.add_argument(
        "-o", dest="outfpath", required=True,
        help="Output file"
    )
    args = parser.parse_args()
    return args

def main():
    global ts_path
    args = parse_args()
    ts_path = args.outfpath

    # Register signal handler for interruptions
    signal.signal(signal.SIGINT, handle_interrupt)

    template_url = args.url_template
    content = download(template_url)
    
    # Save the concatenated TS file to the specified output path
    save_ts_file(content, ts_path)

if __name__ == "__main__":
    main()

