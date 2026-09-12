# mailthought — email-to-thought gateway for eve.gd.
#
# The image carries everything the runtime clone of the blog needs to
# publish a thought: the jekyll toolchain the deploy uses (plain
# `jekyll build`, so the gems are installed system-wide, pinned to the
# repo's Gemfile versions), chromium + fonts + imagemagick for the
# OG-card build pass, git/rsync/ssh for persistence and deploy, and uv
# to run the in-repo thought_composer/evedeploy projects. The blog
# itself is NOT baked in — the entrypoint clones it onto the /data
# volume on first boot so build caches survive across deploys.

FROM ruby:3.3-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        rsync \
        openssh-client \
        curl \
        ca-certificates \
        tzdata \
        chromium \
        fonts-liberation \
        fonts-dejavu \
        imagemagick \
        libimage-exiftool-perl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# The blog builds with plain `jekyll`, not bundler; pin to the repo's
# Gemfile (jekyll 4.4.1, liquid 4.0.4, jekyll-feed, bigdecimal).
RUN gem install --no-document liquid:4.0.4 jekyll:4.4.1 jekyll-feed bigdecimal

# uv runs the gateway and the in-repo Python projects; bake a Python so
# first boot needs no interpreter download.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
ENV UV_PYTHON_INSTALL_DIR=/opt/uv/pythons
RUN uv python install 3.13

# GitHub's published SSH host keys, so the first clone is verified
# rather than trusted on first use (https://api.github.com/meta).
RUN mkdir -p /etc/mailthought && printf '%s\n' \
    'github.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl' \
    'github.com ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEmKSENjQEezOmxkZMy7opKgwFB9nkt5YRrYMjNuG5N87uRgg6CLrbo5wAdT/y6v0mKV0U2w0WZ2YB/++Tpockg=' \
    'github.com ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCj7ndNxQowgcQnjshcLrqPEiiphnt+VTTvDP6mHBL9j1aNUkY4Ue1gvwnGLVlOhGeYrnZaMgRK6+PKCUXaDbC7qtbW8gIkhL7aGCsOr/C56SJMy/BCZfxd1nWzAOxSDPgVsmerOBYfNqltV9/hWCqBywINIR+5dIg6JTJ72pcEpEjcYgXkE2YEFXV1JHnsKgbLWNlhScqb2UmyRkQyytRLtL+38TGxkxCflmO+5Z8CSSNY7GidjMIZ7Q4zMjA2n1nGrlTDkzwDCsw+wqFPGQA179cnfGWOWRVruj16z6XyvxvjJwbz0wQZ75XK5tKSb7FNyeIEs4TT4jk+S4dhPeAUC5y+bDYirYgM4GC7uEnztnZyaVWQ7B381AK4Qdrwt51ZqExKbQpTUNn+EjqoTwvqNj4kqx5QUCI0ThS/YkOxJCXmPUWZbhjpCg56i+2aB6CmK2JGhn57K5mj0MNdBXA4/WnwH6XoPWJzK5Nyu2zB3nAZp+S5hpQs+p1vN1/wsjk=' \
    > /etc/mailthought/github_known_hosts

# The gateway app itself.
WORKDIR /app
COPY pyproject.toml uv.lock README.md __version__.py /app/
COPY mailthought /app/mailthought
RUN uv sync --frozen --no-dev

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV TZ=Europe/London \
    JEKYLL_SKIP_PDFS=1 \
    BUNDLE_SILENCE_DEPRECATIONS=true \
    DATA_DIR=/data

EXPOSE 8080
ENTRYPOINT ["/app/entrypoint.sh"]
