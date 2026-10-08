# The evedeploy toolchain: everything the eve.gd deploy pipeline shells
# out to, so a clone of the repo deploys from any machine with Docker or
# Podman. Built automatically by ./deploy.sh (see evedeploy/container.py);
# the tag is a digest of this file, entrypoint.sh, Gemfile and
# Gemfile.lock, so changing any of them triggers a rebuild.
#
# Nothing from the repository is baked in except the gem set: the repo is
# bind-mounted at run time, so edits, caches (.pdf_cache, .og_cache,
# .jekyll-cache) and _site are the host's own files.

FROM debian:trixie-slim

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    BUNDLE_SILENCE_DEPRECATIONS=true \
    BUNDLE_SILENCE_ROOT_WARNING=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

# Ruby for Jekyll (sass-embedded and google-protobuf ship native
# extensions → build tools); headless Chromium renders the PDF editions
# and OG cards (python3's http.server backs the PDF render; exiftool
# embeds metadata; ImageMagick's `convert` crops OG sources); Node for
# sequoia; rsync + ssh + git for shipping. Fonts: the site self-hosts its
# web fonts, so these are fallbacks for glyphs the page fonts lack.
RUN apt-get update && apt-get install -y --no-install-recommends \
        ruby ruby-dev build-essential \
        chromium \
        libimage-exiftool-perl imagemagick \
        python3 \
        nodejs npm \
        git openssh-client rsync ca-certificates curl \
        fonts-liberation fonts-dejavu-core fonts-noto-core \
        fonts-noto-color-emoji \
        util-linux xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# uv (Python project runner) from its official image; the Python it runs
# is Debian's own python3 (3.13 ≥ the projects' 3.12 floor).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# sequoia-cli (ATProto publisher) — only on npm; the published tarball is a
# self-contained bundle (no postinstall, no native code).
ARG SEQUOIA_VERSION=0.5.7
RUN npm install -g "sequoia-cli@${SEQUOIA_VERSION}" && npm cache clean --force

# The site's gem set, installed system-wide from the repo's lockfile so a
# plain `jekyll build` (which runs Bundler.setup against this Gemfile)
# finds every gem, exactly what failed on an unprovisioned host.
WORKDIR /opt/blog-gems
COPY Gemfile Gemfile.lock ./
RUN gem install bundler -v "$(tail -1 Gemfile.lock | tr -d ' ')" \
    && bundle config set --global without 'development test' \
    && bundle install --jobs 4 \
    && rm -rf /root/.bundle/cache /usr/local/bundle/cache

# Jekyll reads the Gemfile from the working directory (the mounted repo),
# whose contents match the one installed above; BUNDLE_GEMFILE pins it
# regardless so a build started elsewhere in the tree still resolves.
ENV BUNDLE_GEMFILE=/opt/blog-gems/Gemfile

COPY evedeploy/container/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash"]
