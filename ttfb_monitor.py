import argparse
import io
import logging
import os
import random
import time
from datetime import datetime

import certifi
import humanfriendly
import pandas as pd
import pycurl
import schedule
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Measure server speed.")
parser.add_argument(
    "-u", "--urls", type=str, help="Comma-separated list of URLs to query"
)
parser.add_argument(
    "-i",
    "--interval",
    type=str,
    default="10m",
    help="Scheduler interval (e.g., 10m for 10 minutes, 1h for 1 hour)",
)
parser.add_argument(
    "--resolve",
    type=str,
    help="Comma-separated list of hostname:port:IP mappings for curl resolve (e.g., example.com:80:192.168.1.100)",
)
parser.add_argument(
    "-o", "--output", type=str, default="ttfb_results.csv", help="Output CSV file name"
)
args = parser.parse_args()

# Get URLs from command-line arguments or environment variables
if args.urls:
    urls = args.urls.split(",")
else:
    urls = os.getenv("URLS", "").split(",")

# Remove any empty strings in the URL list
urls = [url for url in urls if url]

# Check if URLs are provided
if not urls:
    raise ValueError(
        "No URLs provided. Please set URLs through command-line arguments or environment variables."
    )

# Parse the interval argument to seconds
interval_seconds = humanfriendly.parse_timespan(args.interval)

# Parse the resolve argument if provided
resolve_mappings = []
if args.resolve:
    resolve_mappings = args.resolve.split(",")

output_file = args.output


def measure_speed(url):
    """Measures the Time To First Byte (TTFB), total request time, and response code for a given URL.

    Args:
        url (str): The URL to measure.

    Returns:
        tuple: A tuple containing the TTFB (int) in milliseconds, the total request time (int) in milliseconds, and the HTTP response code (int).
    """
    buffer = io.BytesIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEDATA, buffer)
    curl.setopt(pycurl.CAINFO, certifi.where())

    if resolve_mappings:
        curl.setopt(pycurl.RESOLVE, resolve_mappings)

    start_time = time.time()
    curl.perform()

    response_code = curl.getinfo(pycurl.RESPONSE_CODE)
    ttfb = round(curl.getinfo(pycurl.STARTTRANSFER_TIME) * 1000)
    total_time = round((time.time() - start_time) * 1000)

    curl.close()

    return response_code, ttfb, total_time


def perform_speed_analysis():
    """Performs speed analysis on a list of URLs and logs the results.

    The function measures TTFB, total request time, and response code for each URL, logs the results, and appends them to a CSV file.
    """
    results = []
    random.shuffle(urls)

    for url in urls:
        response_code, ttfb, total_time = measure_speed(url)
        result = {
            "url": url,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "response_code": response_code,
            "ttfb_ms": ttfb,
            "total_time_ms": total_time,
        }
        results.append(result)
        logging.info(
            f"URL: {url}, Response Code: {response_code}, TTFB: {ttfb}ms, Total Time: {total_time}ms"
        )
        time.sleep(1)

    df = pd.DataFrame(results)
    df.to_csv(output_file, mode="a", index=False, header=False)


def run_scheduler(interval_seconds):
    """Sets up and runs the scheduler to perform speed analysis at regular intervals.

    Args:
        interval_seconds (int): The interval in seconds at which to run the speed analysis.
    """
    perform_speed_analysis()
    schedule.every(interval_seconds).seconds.do(perform_speed_analysis)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    # Add CSV headers if the file is being created for the first time
    try:
        with open(output_file, "x") as f:
            df = pd.DataFrame(
                columns=[
                    "url",
                    "timestamp",
                    "response_code",
                    "ttfb_ms",
                    "total_time_ms",
                ]
            )
            df.to_csv(f, index=False)
    except FileExistsError:
        pass

    # Run the scheduler with the specified interval in seconds
    run_scheduler(interval_seconds)
