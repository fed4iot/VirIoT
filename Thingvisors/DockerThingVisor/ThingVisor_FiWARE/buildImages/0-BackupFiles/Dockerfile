FROM node:8

ENV NODE_ENV=production

# Establish workdir
WORKDIR /home/node/app

# Copy package*.json (workdir)
COPY package*.json ./

# Create node_modules  WORKDIR
# --only=production --> without development packages
RUN npm install --only=production

# Copy sources (workdir)

#COPY controllers ./controllers
#COPY models ./models
COPY routes ./routes
COPY app.js config.js index.js orion.js util.js fromNGSIv2.js wrapperUtils.js ./
#COPY config.js index.js util.js orion.js ./

# application's default port
EXPOSE 1030

# Launch ThingVisor
CMD [ "node", "./index.js" ]
