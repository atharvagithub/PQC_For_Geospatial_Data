const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const CRUD = await hre.ethers.getContractFactory("GeoDataStorage");
  const crud = await CRUD.deploy();
  await crud.waitForDeployment(); // ✅ For latest Hardhat

  const address = await crud.getAddress(); // ✅ Use getAddress() instead of crud.address
  console.log("Contract deployed to:", address);

  const artifact = await hre.artifacts.readArtifact("GeoDataStorage");

  // Save ABI
  fs.writeFileSync(
    path.join(__dirname, "../abi.json"),
    JSON.stringify(artifact.abi, null, 2)
  );

  // Save contract address
  fs.writeFileSync(
    path.join(__dirname, "../address.txt"),
    address
  );
}

main().catch((error) => {
  console.error("Deployment failed:", error);
  process.exitCode = 1;
});
