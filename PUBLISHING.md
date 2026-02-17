# How to Publish "Color Sea"

Since this is now a new extension (no longer "Ruby Sea"), you need to publish it under your own publisher ID.

## 1. Prerequisites

1. **Install `vsce`** (Visual Studio Code Extensions CLI):

   ```bash
   npm install -g @vscode/vsce
   ```

2. **Create a Publisher Account**:
   - Go to [marketplace.visualstudio.com](https://marketplace.visualstudio.com/manage)
   - Log in with your Microsoft/GitHub account.
   - Click **"Create Publisher"**.
   - **Important**: The ID you choose *must* match the `publisher` field in `package.json` (currently set to `danilodanese`). If you chose a different ID, update `package.json`!

3. **Get a Personal Access Token (PAT)**:
   - Go to [Azure DevOps](https://dev.azure.com/).
   - Click **User Settings** (top right) → **Personal Access Tokens**.
   - Create a new token:
     - **Name**: `vsce`
     - **Organization**: `All accessible organizations`
     - **Scopes**: Select **Custom defined** → **Marketplace** → check **Acquire** and **Manage**.
   - **Copy the token** (you won't see it again).

## 2. Login

Run this command in your terminal:

```bash
vsce login <publisher-id>
```

(Replace `<publisher-id>` with `danilodanese` or your chosen ID).
Paste your Personal Access Token when prompted.

## 3. Package & Publish

### To create a local VSIX file (for testing)

```bash
vsce package
```

This creates `color-sea-1.0.6.vsix`. You can drag-and-drop this into VS Code extensions view to install locally.

### To publish to the Marketplace

```bash
vsce publish
```

This uploads the extension to the store. It usually takes 5-10 minutes to verify and appear live.

### Boosting Version

When you make changes, update version in `package.json` (e.g., `1.0.7`) or run:

```bash
vsce publish patch
```

---

## Troubleshooting

- **Error: "Publisher '...' not found"**: You haven't created the publisher on the Marketplace website yet.
- **Error: "401 Unauthorized"**: Your PAT token is invalid or expired. Create a new one.
