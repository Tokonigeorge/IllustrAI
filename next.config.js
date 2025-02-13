/** @type {import('next').NextConfig} */
const nextConfig = {
  staticPageGenerationTimeout: 60000,
  httpAgentOptions: {
    keepAlive: true,
  },
};

module.exports = nextConfig;
