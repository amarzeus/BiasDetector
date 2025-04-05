/**
 * @license
 * Copyright 2024 Amar Kumar
 * SPDX-License-Identifier: MIT
 */
chrome.runtime.onInstalled.addListener(() => {
  console.log('Bias Neutralizer initialized');
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Message received:', message);
});