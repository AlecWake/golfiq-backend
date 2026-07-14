# Deploy GolfIQ to AWS EC2

This runbook deploys the existing FastAPI application and PostgreSQL database to
one Ubuntu LTS EC2 instance with Docker Compose. It intentionally does not add a
reverse proxy, TLS, a domain, managed database, or continuous deployment.

## What runs in production

`docker-compose.production.yml` builds the existing `Dockerfile` and starts two
services:

- `api` publishes TCP port 8000 and uses `restart: unless-stopped`.
- `postgres` is reachable only on the private Compose network. It publishes no
  host or EC2 port and stores its data in the `golfiq_postgres_data` named volume.

The API waits for PostgreSQL's health check. Its existing entrypoint then runs
`python -m alembic upgrade head`; Uvicorn starts only after migrations succeed.
The same image, startup script, migrations, and application code used locally are
used in production.

## 1. Create and secure the EC2 instance

Launch an EC2 instance using a current Ubuntu LTS AMI. A small general-purpose
instance is sufficient for an initial low-traffic deployment; size it for the
actual workload and database growth. Allocate enough EBS storage for Docker
images, logs, backups, and PostgreSQL data. An Elastic IP is recommended if the
public address must remain stable.

Create or attach a security group with only these inbound rules:

| Protocol | Port | Source | Purpose |
| --- | ---: | --- | --- |
| TCP | 22 | Your trusted public IP in `/32` form | SSH administration |
| TCP | 8000 | `0.0.0.0/0` (and `::/0` if using IPv6) | Public GolfIQ API |

Do not add an inbound rule for PostgreSQL port 5432. Keep normal outbound access
so the host can install packages, clone the repository, and pull base images.

Connect with the private key selected when the instance was launched:

```bash
chmod 400 /path/to/golfiq.pem
ssh -i /path/to/golfiq.pem ubuntu@EC2_PUBLIC_IP
```

EC2 Ubuntu images use key authentication by default. Before explicitly disabling
password login, keep the current session open and confirm that a second key-based
SSH session succeeds. Then set these values in an SSH server configuration drop-in
and reload SSH:

```text
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
```

```bash
sudoedit /etc/ssh/sshd_config.d/99-golfiq.conf
sudo sshd -t
sudo systemctl reload ssh
```

Optionally enable Ubuntu's host firewall as a second layer after confirming the
EC2 security-group rules:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 8000/tcp
sudo ufw enable
sudo ufw status
```

## 2. Install Docker Engine and Compose

Use Docker's official Ubuntu apt repository rather than the convenience script:

```bash
sudo apt update
sudo apt install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

Log out and reconnect so the Docker group membership takes effect, then verify:

```bash
docker --version
docker compose version
docker run --rm hello-world
```

Membership in the `docker` group grants root-equivalent access. Only grant it to
trusted administrators.

## 3. Configure GolfIQ

Clone the repository and check out the intended release commit or tag:

```bash
git clone YOUR_REPOSITORY_URL golfiq
cd golfiq
git checkout YOUR_RELEASE_TAG_OR_COMMIT
cp .env.production.example .env.production
chmod 600 .env.production
```

Generate the JWT signing key and a separate database password:

```bash
# SECRET_KEY
openssl rand -hex 32
# POSTGRES_PASSWORD
openssl rand -hex 32
```

Edit `.env.production` and replace both placeholders. Do not put secrets in Git,
shell history, the Compose file, or the EC2 user-data field. Restrict the file to
its owner and back it up through an approved secrets-management process.

| Variable | Required | Production use |
| --- | --- | --- |
| `POSTGRES_USER` | Yes | Internal PostgreSQL role name |
| `POSTGRES_PASSWORD` | Yes | Long, unique PostgreSQL password |
| `POSTGRES_DB` | Yes | Internal PostgreSQL database name |
| `SECRET_KEY` | Yes | JWT signing secret generated with a cryptographic RNG |
| `ALGORITHM` | No | Defaults to the existing `HS256` setting |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Defaults to 30 minutes |
| `LOG_LEVEL` | No | Defaults to `INFO` |
| `API_PORT` | No | Host port; defaults to 8000 |

The production Compose file constructs `DATABASE_URL` from the PostgreSQL values
and the private `postgres:5432` service address. Do not add a public database port.
The root `.env.example` remains the template for local and hybrid development.

Check interpolation before starting. The rendered output contains secrets, so do
not paste it into tickets or logs:

```bash
docker compose --env-file .env.production -f docker-compose.production.yml config --quiet
```

## 4. Start the application

Build and start both services:

```bash
docker compose --env-file .env.production -f docker-compose.production.yml up -d --build
docker compose --env-file .env.production -f docker-compose.production.yml ps
```

On every API container start, the existing entrypoint applies pending Alembic
migrations before starting Uvicorn. If a migration fails, the API does not start;
inspect its logs and fix the cause rather than bypassing migrations.

Both services use `restart: unless-stopped`, and Docker is enabled at boot. They
therefore return after an instance reboot unless an administrator explicitly
stopped them.

## 5. Verify health

From the EC2 instance:

```bash
curl --fail http://localhost:8000/api/v1/health
curl --fail --output /dev/null http://localhost:8000/docs
docker compose --env-file .env.production -f docker-compose.production.yml ps
docker compose --env-file .env.production -f docker-compose.production.yml logs --tail=100 api
docker compose --env-file .env.production -f docker-compose.production.yml logs --tail=100 postgres
```

The health response should contain `"status":"ok"`; `ps` should show both
containers running and healthy. From another machine, verify public access:

```bash
curl --fail http://EC2_PUBLIC_IP:8000/api/v1/health
```

Open `http://EC2_PUBLIC_IP:8000/docs` to verify Swagger UI. Until HTTPS is added,
do not send real credentials or sensitive data over the public internet because
HTTP traffic is unencrypted.

## 6. Update the application

Before an update, record the deployed revision and create a database backup:

```bash
cd ~/golfiq
git rev-parse HEAD
mkdir -p backups
docker compose --env-file .env.production -f docker-compose.production.yml exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "backups/golfiq-$(date +%Y%m%d-%H%M%S).dump"
```

Store important backups off the instance as well; the named Docker volume and a
backup on the same EBS volume share the same failure domain. Then deploy a reviewed
commit and verify health:

```bash
git fetch --tags origin
git checkout YOUR_NEW_RELEASE_TAG_OR_COMMIT
docker compose --env-file .env.production -f docker-compose.production.yml config --quiet
docker compose --env-file .env.production -f docker-compose.production.yml up -d --build
docker compose --env-file .env.production -f docker-compose.production.yml ps
curl --fail http://localhost:8000/api/v1/health
```

Compose recreates only services whose configuration or image changed. This first
single-instance deployment can have a short API interruption while its one API
container is replaced; it is not a zero-downtime rolling deployment.

## 7. Roll back

Check out the exact previously recorded revision, rebuild, and verify:

```bash
git checkout PREVIOUS_RELEASE_TAG_OR_COMMIT
docker compose --env-file .env.production -f docker-compose.production.yml up -d --build
docker compose --env-file .env.production -f docker-compose.production.yml ps
curl --fail http://localhost:8000/api/v1/health
```

Do not automatically run `alembic downgrade`: a code rollback and a schema
rollback are separate operations. If the newer release applied an incompatible
migration, stop writes, review that migration's downgrade path, and restore the
pre-update database backup or run a specifically validated downgrade. Never use
`docker compose down -v` in production; `-v` deletes the PostgreSQL data volume.

## Operations reference

```bash
# Follow API logs
docker compose --env-file .env.production -f docker-compose.production.yml logs -f api

# Restart the API without deleting data
docker compose --env-file .env.production -f docker-compose.production.yml restart api

# Stop containers while retaining PostgreSQL data
docker compose --env-file .env.production -f docker-compose.production.yml down

# Start the retained deployment again
docker compose --env-file .env.production -f docker-compose.production.yml up -d
```

Docker's installation commands are based on the official
[Docker Engine for Ubuntu](https://docs.docker.com/engine/install/ubuntu/) and
[Compose plugin](https://docs.docker.com/compose/install/linux/) documentation.
