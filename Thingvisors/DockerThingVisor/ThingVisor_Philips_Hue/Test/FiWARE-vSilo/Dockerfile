#
#Copyright Odin Solutions S.L. All Rights Reserved.
#
#SPDX-License-Identifier: Apache-2.0
#

FROM node:8

ENV NODE_ENV=production

# Establish workdir
WORKDIR /home/node/app

# Copy package*.json (workdir)
COPY package.json ./

# Create node_modules  WORKDIR
# --only=production --> without development packages
RUN npm install --only=production

# Copy sources (workdir)
COPY routes ./routes
COPY app.js config.js index.js util.js  ./

# Launch
CMD [ "node", "./index.js" ]