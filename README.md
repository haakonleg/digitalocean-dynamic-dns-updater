# digitalocean-dynamic-dns-updater

Python script and docker image to automate updating DNS A records on DigitalOcean. Useful if you have a dynamic IP and self-hosted server, and wish to keep subdomain records updated to match your current public IP address.

You can use this as a standalone script (dyndns.py), or deploy the docker image which can be configured to check the records at a regular interval.

## Usage

- Ensure that your domain/s already has the records (if they don't exist, this script won't work)
- You must generate a DigitalOcean API key (can be found in the dashboard under Account -> API -> Token/Keys)

### Example

`python dyndns.py --config dyndns.conf`

You must specify a path to the config file. There is an example provided in `dyndns.conf.example`.

## Docker image

The docker image runs the script at a configurable interval (specified by env variable CHECK_INTERVAL).

Example usage for docker-compose:

```
digitalocean-dyndns:
  build:
    context: ./digitalocean-dynamic-dns-updater
    dockerfile: docker/Dockerfile
  container_name: digitalocean-dyndns
  environment:
    - PUID=41025
    - CHECK_INTERVAL=3600
  volumes:
    - /path/to/config/dyndns.conf:/dyndns.conf:ro
  restart: unless-stopped
```

## Todo

- This does not support AAAA records yet (IPV6), since I have no use for it personally. I might add it in the future, though.
- Does not have proper error handling or retrying. If an error occurs (for example, a status code other than 2xx), the script simply prints error and exits.
