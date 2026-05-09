# Phonics Playground — production-like static serve.
# nginx:alpine is ~10 MB; total image ~14 MB after copying our 4 MB of assets.
# Use this for local dev to match Vercel's behaviour, or to self-host
# anywhere that runs containers.
FROM nginx:1.27-alpine

# Strip the default nginx config and replace with ours (gzip, cache, headers)
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Static assets: the HTML artifact and the audio folder. Everything else
# (Python tools, recordings backups, project docs) is dev-only — see
# .dockerignore.
COPY SATPIN_StoryMode.html /usr/share/nginx/html/SATPIN_StoryMode.html
COPY audio                  /usr/share/nginx/html/audio

# Convenience: serve the artifact at "/" without forcing the user to type
# the full filename. nginx.conf has the rewrite — this just makes a copy
# at /index.html as a fallback for environments that ignore the rewrite.
RUN cp /usr/share/nginx/html/SATPIN_StoryMode.html /usr/share/nginx/html/index.html

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD wget -qO- http://localhost:8080/ > /dev/null || exit 1
