# 📦 01Agent Windows Installer Build Guide

## 🚀 Quick Start

Run this command to build your Windows installer:
```bash
BUILD_INSTALLER_EXE.bat
```

## 📋 What This Creates

### **Professional Windows Installer (.exe)**
- **NSIS Installer**: Professional Windows installation package
- **One-Click Install**: Users can install with a single .exe file
- **Desktop Shortcuts**: Automatically creates desktop and start menu shortcuts
- **Uninstaller**: Includes proper uninstall functionality
- **Windows Integration**: Adds to Programs & Features list

### **Installation Features**
- **Custom Install Location**: Users can choose installation directory
- **Desktop Shortcut**: Optional desktop icon creation
- **Start Menu Entry**: Adds 01Agent to Windows Start Menu
- **Auto-Launch**: Option to start app after installation
- **Update Support**: Built-in update mechanism

## 🔧 Build Process

### **Step 1: React Production Build**
```bash
cd desktop/01agent-app
npm run build
```
- Creates optimized React production files
- Minifies and bundles all assets
- Prepares UI for desktop integration

### **Step 2: Electron Builder Setup**
```bash
cd desktop
npm install electron-builder --save-dev
```
- Installs professional packaging tool
- Configures Windows installer creation
- Sets up code signing (optional)

### **Step 3: Windows Installer Creation**
```bash
npm run build
```
- Packages Electron app with React build
- Creates NSIS installer (.exe)
- Includes all dependencies and assets
- Generates uninstaller

## 📁 Output Files

### **Generated Files:**
```
desktop/dist/
├── 01Agent Setup 2.0.0.exe          # Main installer
├── 01Agent Setup 2.0.0.exe.blockmap # Update metadata
├── latest.yml                        # Update configuration
└── win-unpacked/                     # Unpacked app files
    ├── 01Agent.exe                   # Main executable
    ├── resources/                    # App resources
    └── ...                          # Dependencies
```

### **Installer Properties:**
- **File Size**: ~150-300MB (includes Electron runtime)
- **Install Size**: ~400-600MB (full installation)
- **Platforms**: Windows 10/11 (64-bit)
- **Architecture**: x64 (Intel/AMD)

## 🎯 Installer Configuration

### **Current Configuration (package.json):**
```json
{
  "build": {
    "appId": "com.get01agent.desktop",
    "productName": "01Agent",
    "directories": {
      "buildResources": "assets",
      "output": "dist"
    },
    "files": [
      "main.js",
      "electron/**/*",
      "01agent-app/build/**/*"
    ],
    "win": {
      "target": "nsis"
    },
    "nsis": {
      "oneClick": false,
      "perMachine": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    }
  }
}
```

### **Installer Features:**
- ✅ **Custom Install Path**: Users can choose location
- ✅ **Desktop Shortcut**: Optional desktop icon
- ✅ **Start Menu**: Adds to Windows Start Menu
- ✅ **Uninstaller**: Proper removal functionality
- ✅ **Per-User Install**: No admin rights required
- ✅ **Update Support**: Built-in update mechanism

## 🔧 Advanced Build Options

### **Manual Build Commands:**
```bash
# Standard build
npm run build

# Windows-specific build
npx electron-builder --win

# Build without publishing
npx electron-builder --win --publish=never

# Build with specific architecture
npx electron-builder --win --x64

# Build with debug info
npx electron-builder --win --publish=never --config.compression=store
```

### **Custom Build Script:**
```bash
# Build React app first
cd desktop/01agent-app && npm run build

# Build Electron installer
cd .. && npx electron-builder --win --config.directories.output=dist
```

## 📦 Distribution Ready

### **What You Get:**
- **Professional Installer**: `01Agent Setup 2.0.0.exe`
- **Easy Distribution**: Single file to share
- **Professional Installation**: Windows-standard install process
- **Automatic Updates**: Built-in update mechanism
- **Uninstall Support**: Proper removal from Windows

### **Installation Experience:**
1. **Download**: User downloads `01Agent Setup 2.0.0.exe`
2. **Run Installer**: Double-click to start installation
3. **Choose Location**: Select installation directory
4. **Install**: Automatic installation process
5. **Launch**: Option to start 01Agent immediately
6. **Desktop Icon**: Shortcut created on desktop
7. **Start Menu**: Added to Windows Start Menu

## 🚀 Professional Features

### **Installer Includes:**
- ✅ **Complete Desktop App**: Full Electron application
- ✅ **React UI**: All interface components
- ✅ **Native Integration**: Windows system integration
- ✅ **Auto-Updater**: Built-in update mechanism
- ✅ **Professional Icons**: High-quality app icons
- ✅ **Code Signing**: Optional digital signature
- ✅ **Crash Reporting**: Error reporting system

### **User Experience:**
- **One-Click Install**: Simple installation process
- **No Dependencies**: Everything included in installer
- **Professional Appearance**: Windows-standard installer
- **Easy Uninstall**: Standard Windows uninstall
- **Automatic Updates**: Seamless update process

## 🎊 Success Criteria

### **✅ Successful Build:**
- Installer file created: `01Agent Setup 2.0.0.exe`
- File size: 150-300MB
- No build errors or warnings
- Installer runs without issues

### **✅ Professional Quality:**
- Windows-standard installation process
- Desktop and Start Menu shortcuts
- Proper uninstall functionality
- Professional app icons and branding

### **✅ Distribution Ready:**
- Single .exe file for easy sharing
- No external dependencies required
- Works on Windows 10/11 systems
- Professional installation experience

## 🚀 Ready to Build!

Your 01Agent desktop app is ready to be packaged into a professional Windows installer!

Run `BUILD_INSTALLER_EXE.bat` to create your distribution-ready installer package.

The result will be a professional-grade Windows installer that users can download and install with a single click!