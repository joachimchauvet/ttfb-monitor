# TTFB Monitor

## Overview

This simple Python script measures the Time To First Byte (TTFB), total request time, and HTTP response code for a given list of URLs at regular intervals. The results are logged and appended to a CSV file. It uses `pycurl` for HTTP requests and `schedule` for running the measurements at specified intervals.

## Features

- Measure TTFB, total request time, and HTTP response code for a list of URLs.
- Schedule measurements at regular intervals.
- Save the results to a specified CSV file.
- Optionally resolve specific IP addresses for given hostnames.

## Installation

1. Clone the repository or download the script files.
2. Install the required Python packages using `pip` in your virtual environment:
   ```bash
   pip install -r requirements.txt
   ```
3. Optionally, create a `.env` file in the same directory as the script if you want to use environment variables to provide the URLs.

## Usage

### Command-Line Arguments

- `-u, --urls`: Comma-separated list of URLs to query. Example: `-u http://example.com,http://example.org`
- `-i, --interval`: Scheduler interval (e.g., `10m` for 10 minutes, `1h` for 1 hour). Default is `10m`.
- `--resolve`: Comma-separated list of hostname:port:IP mappings for curl resolve. Example: `example.com:80:192.168.1.100`
- `-o, --output`: Output CSV file name. Default is `speed_analysis_results.csv`.

### Environment Variables

- `URLS`: Comma-separated list of URLs to query (used if `-u` is not provided).

### Running the Script

To run the script with command-line arguments:

```bash
python ttfb_monitor.py -u "http://example.com,http://example.org" -i 10m -o results.csv
```

To run the script using environment variables, create a `.env` file with the following content:

```
URLS=http://example.com,http://example.org
```

Then run the script without the `-u` argument:

```bash
python ttfb_monitor.py -i 10m -o results.csv
```

### Example

To measure the speed of `http://example.com` and `http://example.org` every 10 minutes and save the results to `results.csv`:

```bash
python ttfb_monitor.py -u http://example.com,http://example.org -i 10m -o results.csv
```

## Output

The script appends the measurement results to the specified CSV file with the following columns:

- `url`: The URL that was measured.
- `timestamp`: The timestamp when the measurement was taken.
- `response_code`: The HTTP response code.
- `ttfb_ms`: The Time To First Byte (in milliseconds).
- `total_time_ms`: The total request time (in milliseconds).

## Logging

The script logs the results of each measurement to the console with the following information:

- URL being measured
- HTTP response code
- TTFB (in milliseconds)
- Total request time (in milliseconds)

## Scheduler

The script uses the `schedule` library to run measurements at regular intervals. The interval can be specified using the `-i` or `--interval` argument.

## License

This project is licensed under the MIT License.
