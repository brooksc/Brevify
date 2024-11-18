export default {
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.js$': 'babel-jest',
  },
  setupFilesAfterEnv: ['<rootDir>/tests/frontend/setup.js'],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': '<rootDir>/tests/frontend/__mocks__/styleMock.js',
  },
  testMatch: [
    '<rootDir>/tests/frontend/**/*.test.js',
  ],
  collectCoverageFrom: [
    'static/js/**/*.js',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  verbose: true,
  testTimeout: 10000,
  moduleFileExtensions: ['js', 'json', 'jsx', 'node'],
};
