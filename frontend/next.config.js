const withPWA = require('next-pwa')({
  dest: 'public',
  disable: process.env.NODE_ENV === 'development',
  register: true,
  skipWaiting: true,
});

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Use static export for performance and hosting simplicity
  output: 'export',
  images: {
    unoptimized: true,
  },
  // Ensure strict mode for better reliability
  reactStrictMode: true,
  // Turbopack is already enabled by default in Next 16
  turbopack: {},
};

module.exports = withPWA(nextConfig);
