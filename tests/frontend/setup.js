import '@testing-library/jest-dom';
import { jest } from '@jest/globals';
import DOMPurify from 'dompurify';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
  writable: true
});

// Mock fetch
global.fetch = jest.fn();

// Add DOMPurify to global
global.DOMPurify = DOMPurify;

// Reset mocks before each test
beforeEach(() => {
  localStorage.getItem.mockClear();
  localStorage.setItem.mockClear();
  fetch.mockClear();
  window.matchMedia.mockClear();
  document.body.innerHTML = '';
});
