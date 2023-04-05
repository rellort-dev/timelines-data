
import digitalocean

import config


def main():
    droplet = digitalocean.Droplet(id=config.DIGITALOCEAN_MEILISEARCH_DROPLET_ID)
    droplet.reboot()

if __name__ == "__main__":
    main()
