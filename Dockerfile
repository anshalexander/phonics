# Phonics Playground — production-like static serve.
# nginx:alpine is ~10 MB; total image ~14 MB after copying our 4 MB of assets.
# Use this for local dev to match Vercel's behaviour, or to self-host
# anywhere that runs containers.
FROM nginx:1.27-alpine

# Strip the default nginx config and replace with ours (gzip, cache, headers)
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Static assets. Layer ORDER matters for cache: HTML and nginx.conf rebuild
# fast and change rarely; audio/ is the bulky volatile layer (re-recordings
# rebuild it). Putting audio LAST means iterating on HTML doesn't blow away
# the audio layer cache. Everything not in this list is excluded by
# .dockerignore (Python tools, backups, docs).
COPY SATPIN_StoryMode.html /usr/share/nginx/html/SATPIN_StoryMode.html
COPY audio                 /usr/share/nginx/html/audio

# (No /index.html copy: nginx.conf has `location = / { return 302 ... }`
# and `index SATPIN_StoryMode.html`, so both / and /SATPIN_StoryMode.html
# resolve correctly without a stale duplicate.)

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD wget -qO- http://localhost:8080/ > /dev/null || exit 1
