FROM python:3.12-slim

# Install Node.js and dependencies
RUN apt-get update && apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean

# Set working directory for backend
WORKDIR /app

# Copy FastAPI app and requirements
COPY requirements.txt .
COPY app/ ./app

# Install FastAPI requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy blockchain project
COPY blockchain/ ./blockchain

# Install blockchain dependencies and compile contract
WORKDIR /app/blockchain
RUN npm install
RUN npx hardhat compile

# Copy back to app dir and launch
WORKDIR /app

CMD bash -c "cd /app/blockchain && \
             npx hardhat node & \
             sleep 5 && \
             cd /app/blockchain && \
             npx hardhat run scripts/deploy.js --network localhost && \
             cd ../ && \
             uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
