FROM node:18

WORKDIR /code

# Copy root-level package.json and lock file
COPY package*.json ./

# Install Hardhat and dependencies
RUN npm install

# Copy the rest of the project (contracts, scripts, config)
COPY . ./

# Set final working directory for commands
WORKDIR /code
