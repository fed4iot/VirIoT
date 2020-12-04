#
#Copyright Odin Solutions S.L. All Rights Reserved.
#
#SPDX-License-Identifier: Apache-2.0
#

FROM node:8

ENV NODE_ENV=production

# Establish workdir
WORKDIR /home/node/app

# Copy package.json (workdir)
COPY src/package.json ./

# Create node_modules  WORKDIR
# --only=production --> without development packages
RUN npm install --only=production

# Copy sources (workdir)
COPY src/routes ./routes
COPY src/app.js buildImages/Actuator-TV/config.js src/index.js src/orion.js src/util.js src/fromNGSIv2.js src/wrapperUtils.js ./
COPY src/DataModels ./DataModels
COPY buildImages/Actuator-TV/entities.js ./DataModels/

# application's default port
EXPOSE 1030

# Launch ThingVisor
CMD [ "node", "./index.js" ]
