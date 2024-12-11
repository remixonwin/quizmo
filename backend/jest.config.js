// filepath: /home/remixonwin/Documents/backend/jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.ts'],
  setupFilesAfterEnv: ['./jest.setup.js']
};