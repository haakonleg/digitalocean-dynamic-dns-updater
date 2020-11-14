# digitalocean-dynamic-dns-updater

Python script and docker image to automate updating DNS A records on DigitalOcean. Useful if you have a dynamic IP and self-hosted server, and wish to keep subdomain records updated to match your current public IP address.

You can use this as a standalone script (dyndns.py), or deploy the docker image which can be configured to check the records at a regular interval.

## Usage

- Ensure that your domain already has the records (if they don't exist, this script won't work)
- You must generate a DigitalOcean API key (can be found in the dashboard under Account -> API -> Token/Keys)

### Example

`python dyndns.py --domain your-domain.com --apikey YOUR_API_KEY subdomain1 subdomain2 subdomain3 ...`

You must specify your domain name and API key. The last argument is a list of subdomains (names of A records) that you want to update.

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
    - DOMAIN=your-domain.com
    - SUBDOMAINS=subdomain1 subdomain2 subdomain3
    - API_KEY=YOUR_API_KEY
  restart: unless-stopped
```

## Todo

- This does not support AAAA records yet (IPV6), since I have no use for it personally. I might add it in the future, though.
- Does not have proper error handling or retrying. If an error occurs (for example, a status code other than 2xx), the script simply prints error and exits.
